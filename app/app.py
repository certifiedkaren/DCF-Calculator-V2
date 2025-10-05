from fastapi import FastAPI, HTTPException 
from fastapi.middleware.cors import CORSMiddleware
import analysis
from models import DCFRequest, DCFResponse, PriceRequest, PriceSeriesResponse

app = FastAPI()

origins = [
    'http://localhost:5173'
]

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins, 
    allow_credentials=True,
    allow_methods=["*"], 
    allow_headers=["*"],  
)


@app.get("/price/{ticker}")
def get_price_endpoint(ticker:str):
    try:
        current_price = analysis.get_price(ticker)
        return {"currentprice": current_price}
    except KeyError as e:
        raise HTTPException(status_code=404, detail=f"Data not found {e}") 
    except IndexError as e:
        raise HTTPException(status_code=404, detail=f"Not enough data for calculation") 
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Internal Error: {e}")  
        
    
@app.post("/historicalPrice/{ticker}", response_model=PriceSeriesResponse)
def get_historical_prices_endpoint(ticker:str, body: PriceRequest):
    try: 
        points = analysis.get_historical_prices(ticker, body.dates)
        if not points: 
            raise HTTPException(status_code=404, detail="No price data found")
        return {"ticker": ticker.upper(), "points": points}
    except HTTPException:
        raise 
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Internal server error {e}")


@app.get("/pastfcf/{ticker}")
def get_past_fcf_endpoint(ticker:str): 
    try: 
        pastfcf = analysis.get_past_fcfs(ticker)
        return {"pastfcf": pastfcf}
    except KeyError as e:
        raise HTTPException(status_code=404, detail=f"Data not found {e}") 
    except IndexError as e:
        raise HTTPException(status_code=404, detail=f"Not enough data for calculation") 
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Internal Error: {e}")  


@app.get("/capm/{ticker}")
def get_capm_endpoint(ticker:str):
    try:
        capm = analysis.calculate_capm(ticker)
        return {"capm": capm}
    except KeyError as e:
        raise HTTPException(status_code=400, detail=f"Data not found {e}") 
    except IndexError as e:
        raise HTTPException(status_code=404, detail=f"Not enough data for calculation") 
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Internal Error: {e}")


@app.get("/wacc/{ticker}/{capm}")
def get_wacc_endpoint(ticker:str, capm: float):
    try: 
        wacc = analysis.calculate_wacc(ticker, capm)
        return {"wacc": wacc}
    except KeyError as e:
        raise HTTPException(status_code=400, detail=f"Data not found {e}") 
    except IndexError as e:
        raise HTTPException(status_code=404, detail=f"Not enough data for calculation") 
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Internal Error: {e}")
    
    
@app.get("/basefcf/{ticker}")
def get_basefcf_endpoint(ticker:str):
    try: 
        basefcf = analysis.calculate_base_fcf(ticker)
        return {"basefcf": basefcf}
    except KeyError as e:
        raise HTTPException(status_code=400, detail=f"Data not found {e}") 
    except IndexError as e:
        raise HTTPException(status_code=404, detail=f"Not enough data for calculation") 
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Internal Error: {e}")


@app.get("/eps/{ticker}")
def get_eps_endpoint(ticker: str):
    try: 
        eps = analysis.get_eps(ticker)
        return {"eps": eps}
    except KeyError as e:
        raise HTTPException(status_code=400, detail=f"Data not found {e}") 
    except IndexError as e:
        raise HTTPException(status_code=404, detail=f"Not enough data for calculation") 
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Internal Error: {e}")


@app.post("/dcf/{ticker}", response_model=DCFResponse) 
def get_dcf_endpoint(ticker:str, payload: DCFRequest):
    try:
        dcf_result = analysis.calculate_dcf(
            ticker = ticker,
            base_fcf = payload.base_fcf,
            growth_rate = payload.growth_rate, 
            perpetual_growth_rate = payload.perpetual_growth_rate,
            discount_rate = payload.discount_rate,
            years = payload.years
        )
        return DCFResponse(
            base_case = dcf_result[0] 
        )
        
    except KeyError as e:
        raise HTTPException(status_code=400, detail=f"Data not found {e}") 
    except IndexError as e:
        raise HTTPException(status_code=404, detail=f"Not enough data for calculation") 
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Internal Error: {e}")