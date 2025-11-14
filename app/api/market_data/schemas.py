


import datetime
from datetime import date
from typing import Dict, List, Optional

from pydantic import BaseModel, ConfigDict, RootModel


class Currency(BaseModel):
    id: int
    code: str
    name: str
    
    model_config = ConfigDict(from_attributes=True)

class MarketIndex(BaseModel):
    id: int
    short_name: str
    name: str
    symbol: str
    currency_id: int | None = None
    currency: Currency | None = None
    
    model_config = ConfigDict(from_attributes=True)
    
class IndexPoint(BaseModel):
    date: date
    value: float
    
    model_config = ConfigDict(from_attributes=True)
    
class MarketIndexesTimeSeries(RootModel[Dict[str, List[IndexPoint]]]):
    """Maps each index (ex: 'S&P500', 'USD/BRL') to its time series"""
    pass

class USD_BRL_History(RootModel[List[IndexPoint]]):
    model_config = ConfigDict(from_attributes=True)


class OHLCV(BaseModel):
    date: datetime.datetime
    close: float
    open: Optional[float] = None
    high: Optional[float] = None
    low: Optional[float] = None
    volume: Optional[int] = None

class QuoteResponse(BaseModel):
    ticker: str
    asset_type: str
    currency: Optional[str] = None
    quotes: List[OHLCV]