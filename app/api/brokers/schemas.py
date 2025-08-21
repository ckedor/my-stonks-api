from pydantic import BaseModel, ConfigDict


class Currency(BaseModel):
    id: int
    code: str
    name: str
    
    model_config = ConfigDict(from_attributes=True)

class Broker(BaseModel):
    id: int
    currency: Currency
    name: str
    cnpj: str

    model_config = ConfigDict(from_attributes=True)