# app/modules/brokers/api/schemas.py
"""Brokers API schemas"""

from typing import Optional

from pydantic import BaseModel, ConfigDict


class Currency(BaseModel):
    id: int
    code: str
    name: str
    
    model_config = ConfigDict(from_attributes=True)


class BrokerCreate(BaseModel):
    name: str
    cnpj: Optional[str] = None
    currency_id: int


class BrokerUpdate(BaseModel):
    name: Optional[str] = None
    cnpj: Optional[str] = None
    currency_id: Optional[int] = None


class Broker(BaseModel):
    id: int
    currency: Currency
    name: str
    cnpj: Optional[str]

    model_config = ConfigDict(from_attributes=True)
