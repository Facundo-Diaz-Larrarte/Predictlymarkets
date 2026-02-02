from decimal import Decimal
from datetime import datetime
from typing import Optional
import logging
import os

from fastapi import FastAPI, Depends, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from sqlalchemy.orm import Session
import redis

from .db import SessionLocal, Base, engine
from .models import Market, MarketState, Position, Trade, LedgerEntry
from .lmsr import quote_buy, price_yes
from .schemas import MarketCreate, MarketOut, QuoteResponse, TradeRequest

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Create tables
Base.metadata.create_all(bind=engine)

app = FastAPI(title="Predictly Markets API")

# Test database connection
try:
    with engine.connect() as conn:
        logger.info("✅ Successfully connected to PostgreSQL database")
except Exception as e:
    logger.error(f"❌ Failed to connect to PostgreSQL: {e}")

# Test Redis connection
redis_url = os.getenv("REDIS_URL", "redis://localhost:6379/0")
try:
    redis_client = redis.from_url(redis_url)
    redis_client.ping()
    logger.info("✅ Successfully connected to Redis")
except Exception as e:
    logger.error(f"❌ Failed to connect to Redis: {e}")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


@app.get("/health")
def health():
    return {"status": "ok"}


@app.post("/markets", response_model=MarketOut)
def create_market(payload: MarketCreate, db: Session = Depends(get_db)):
    market = Market(
        title=payload.title,
        description=payload.description,
        close_time=payload.close_time,
        b=payload.b,
        fee_rate=payload.fee_rate,
        state=MarketState.ACTIVE,
    )
    db.add(market)
    db.commit()
    db.refresh(market)
    prob = price_yes(market.q_yes, market.q_no, market.b)
    return MarketOut(
        id=market.id,
        title=market.title,
        description=market.description,
        close_time=market.close_time,
        state=market.state,
        prob_yes=prob,
    )


@app.get("/markets", response_model=list[MarketOut])
def list_markets(db: Session = Depends(get_db)):
    markets = db.query(Market).all()
    result = []
    for m in markets:
        prob = price_yes(m.q_yes, m.q_no, m.b)
        result.append(
            MarketOut(
                id=m.id,
                title=m.title,
                description=m.description,
                close_time=m.close_time,
                state=m.state,
                prob_yes=prob,
            )
        )
    return result


@app.get("/markets/{market_id}", response_model=MarketOut)
def get_market(market_id: int, db: Session = Depends(get_db)):
    market = db.query(Market).get(market_id)
    if not market:
        raise HTTPException(status_code=404, detail="Market not found")
    prob = price_yes(market.q_yes, market.q_no, market.b)
    return MarketOut(
        id=market.id,
        title=market.title,
        description=market.description,
        close_time=market.close_time,
        state=market.state,
        prob_yes=prob,
    )


@app.get("/markets/{market_id}/quote", response_model=QuoteResponse)
def quote(market_id: int, side: str, dq: Decimal, db: Session = Depends(get_db)):
    market = db.query(Market).get(market_id)
    if not market or market.state != MarketState.ACTIVE:
        raise HTTPException(status_code=400, detail="Invalid market")
    q = quote_buy(side, dq, market.q_yes, market.q_no, market.b, Decimal(market.fee_rate))
    price = price_yes(q["new_q_yes"], q["new_q_no"], market.b)
    return QuoteResponse(
        base_cost=q["base_cost"],
        fee=q["fee"],
        total=q["total"],
        price=price,
        q_yes=q["new_q_yes"],
        q_no=q["new_q_no"],
    )


@app.post("/markets/{market_id}/trade", response_model=QuoteResponse)
def trade(market_id: int, payload: TradeRequest, db: Session = Depends(get_db)):
    market = db.query(Market).get(market_id)
    if not market or market.state != MarketState.ACTIVE:
        raise HTTPException(status_code=400, detail="Invalid market")
    q = quote_buy(payload.side, payload.dq, market.q_yes, market.q_no, market.b, Decimal(market.fee_rate))
    market.q_yes = q["new_q_yes"]
    market.q_no = q["new_q_no"]
    pos = db.query(Position).filter_by(user_id=payload.user_id, market_id=market_id).first()
    if not pos:
        pos = Position(user_id=payload.user_id, market_id=market_id)
        db.add(pos)
    if payload.side == "YES":
        pos.yes_shares = (pos.yes_shares or Decimal("0")) + payload.dq
    else:
        pos.no_shares = (pos.no_shares or Decimal("0")) + payload.dq
    trade_row = Trade(user_id=payload.user_id, market_id=market_id, side=payload.side, shares=payload.dq, cost=q["base_cost"], fee=q["fee"])
    db.add(trade_row)
    db.add(LedgerEntry(user_id=payload.user_id, market_id=market_id, amount=q["total"], is_credit=False, description="Trade debit"))
    db.add(LedgerEntry(user_id=None, market_id=market_id, amount=q["base_cost"], is_credit=True, description="Market collateral"))
    db.add(LedgerEntry(user_id=None, market_id=market_id, amount=q["fee"], is_credit=True, description="Protocol fee"))
    db.commit()
    price = price_yes(market.q_yes, market.q_no, market.b)
    return QuoteResponse(
        base_cost=q["base_cost"],
        fee=q["fee"],
        total=q["total"],
        price=price,
        q_yes=market.q_yes,
        q_no=market.q_no,
    )
