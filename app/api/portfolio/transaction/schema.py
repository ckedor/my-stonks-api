from datetime import datetime

from pydantic import BaseModel


class Transaction(BaseModel):
    asset_id: int
    portfolio_id: int
    transaction_type: str
    quantity: float
    price: float
    broker_id: int
    date: datetime