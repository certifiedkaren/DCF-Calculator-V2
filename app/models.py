from pydantic import BaseModel
from typing import List 

class DCFRequest(BaseModel):
    base_fcf: float
    growth_rate: float 
    perpetual_growth_rate: float 
    discount_rate: float 
    years: int 

class DCFResponse(BaseModel):
    base_case: float 

class PriceRequest(BaseModel):
    dates: List[str]

class PricePoint(BaseModel):
    date: str 
    price: float 

class PriceSeriesResponse(BaseModel):
    ticker: str 
    points: List[PricePoint]
