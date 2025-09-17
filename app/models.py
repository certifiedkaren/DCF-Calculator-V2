from pydantic import BaseModel

class DCFRequest(BaseModel):
    base_fcf: float
    growth_rate: float 
    perpetual_growth_rate: float 
    discount_rate: float 
    years: int 

class DCFResponse(BaseModel):
    base_case: float 
    thirty_percent_margin_of_safety: float 
