from decimal import Decimal
from datetime import datetime
from typing import Optional

from pydantic import BaseModel, Field

from .models import MarketState


class MarketCreate(BaseModel):
    title: str
    description: Optional[str] = None
    close_time: datetime
    b: Decimal = Decimal("10.0")
    fee_rate: Decimal = Decimal("0.01")


class MarketOut(BaseModel):
    id: int
    title: str
    description: Optional[str] = None
    close_time: datetime
    state: MarketState
    prob_yes: Decimal

    class Config:
        orm_mode = True


class QuoteRequest(BaseModel):
    side: str
    dq: Decimal = Field(gt=0)


class QuoteResponse(BaseModel):
    base_cost: Decimal
    fee: Decimal
    total: Decimal
    price: Decimal
    q_yes: Decimal
    q_no: Decimal


class TradeRequest(QuoteRequest):
    user_id: int = 1

