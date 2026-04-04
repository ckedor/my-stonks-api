from datetime import datetime

from pydantic import BaseModel


class Transaction(BaseModel):
    portfolio_id: int
    asset_id: int
    broker_id: int
    date: datetime
    quantity: float
    price: float