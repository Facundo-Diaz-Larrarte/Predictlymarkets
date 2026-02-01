from datetime import datetime
from enum import Enum
from decimal import Decimal

from sqlalchemy import Column, DateTime, Enum as SQLEnum, ForeignKey, Integer, Numeric, String, Boolean, Text
from sqlalchemy.orm import relationship

from .db import Base


class MarketState(str, Enum):
    DRAFT = "DRAFT"
    ACTIVE = "ACTIVE"
    FROZEN = "FROZEN"
    RESOLVED_YES = "RESOLVED_YES"
    RESOLVED_NO = "RESOLVED_NO"
    CANCELED = "CANCELED"


class User(Base):
    __tablename__ = "users"
    id = Column(Integer, primary_key=True, index=True)
    email = Column(String, unique=True, nullable=False)
    is_admin = Column(Boolean, default=False)
    created_at = Column(DateTime, default=datetime.utcnow)
    wallet = relationship("Wallet", back_populates="user", uselist=False)


class Wallet(Base):
    __tablename__ = "wallets"
    id = Column(Integer, primary_key=True)
    user_id = Column(Integer, ForeignKey("users.id"), unique=True)
    balance = Column(Numeric(18, 4), default=Decimal("1000.0"))
    user = relationship("User", back_populates="wallet")


class Market(Base):
    __tablename__ = "markets"
    id = Column(Integer, primary_key=True)
    title = Column(String, nullable=False)
    description = Column(Text, nullable=True)
    close_time = Column(DateTime, nullable=False)
    state = Column(SQLEnum(MarketState), default=MarketState.DRAFT)
    b = Column(Numeric(18, 4), default=Decimal("10.0"))
    fee_rate = Column(Numeric(6, 4), default=Decimal("0.01"))
    q_yes = Column(Numeric(18, 8), default=Decimal("0"))
    q_no = Column(Numeric(18, 8), default=Decimal("0"))
    created_at = Column(DateTime, default=datetime.utcnow)


class Position(Base):
    __tablename__ = "positions"
    id = Column(Integer, primary_key=True)
    user_id = Column(Integer, ForeignKey("users.id"))
    market_id = Column(Integer, ForeignKey("markets.id"))
    yes_shares = Column(Numeric(18, 8), default=Decimal("0"))
    no_shares = Column(Numeric(18, 8), default=Decimal("0"))


class Trade(Base):
    __tablename__ = "trades"
    id = Column(Integer, primary_key=True)
    user_id = Column(Integer, ForeignKey("users.id"))
    market_id = Column(Integer, ForeignKey("markets.id"))
    side = Column(String)  # YES or NO
    shares = Column(Numeric(18, 8))
    cost = Column(Numeric(18, 4))
    fee = Column(Numeric(18, 4))
    created_at = Column(DateTime, default=datetime.utcnow)


class LedgerEntry(Base):
    __tablename__ = "ledger_entries"
    id = Column(Integer, primary_key=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=True)
    market_id = Column(Integer, ForeignKey("markets.id"), nullable=True)
    amount = Column(Numeric(18, 4))
    is_credit = Column(Boolean)
    description = Column(String)
    created_at = Column(DateTime, default=datetime.utcnow)

