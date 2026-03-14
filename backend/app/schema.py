from pydantic import BaseModel

class StockBase(BaseModel):
    symbol: str
    name: str
    sector: str

class StockCreate(StockBase):
    pass

class Stock(StockBase):
    id: int
    current_price: float
    market_cap: float

    class Config:
        orm_mode = True