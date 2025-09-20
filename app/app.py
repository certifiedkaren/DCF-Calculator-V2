from fastapi import FastAPI, HTTPException, Query
from fastapi.middleware.cors import CORSMiddleware
import analysis
from models import DCFRequest, DCFResponse

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


@app.get("/cagr/{ticker}/{name}")
def get_cagr_endpoint(ticker:str, name:str, time_period: int = Query(5, ge=1)):
    try: 
        cagr = analysis.get_cagr(ticker, name, time_period)
        return {"cagr": cagr}
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
    

@app.post("/dcf/{ticker}", response_model=DCFResponse) 
def get_dcf_endpoint(ticker:str, payload: DCFRequest):
    try:
        base_case, mos_30 = analysis.calculate_dcf(
            ticker = ticker,
            base_fcf = payload.base_fcf,
            growth_rate = payload.growth_rate, 
            perpetual_growth_rate = payload.perpetual_growth_rate,
            discount_rate = payload.discount_rate,
            years = payload.years
        )
        return DCFResponse(
            base_case = base_case, 
            thirty_percent_margin_of_safety=mos_30
        )
        
    except KeyError as e:
        raise HTTPException(status_code=400, detail=f"Data not found {e}") 
    except IndexError as e:
        raise HTTPException(status_code=404, detail=f"Not enough data for calculation") 
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Internal Error: {e}")