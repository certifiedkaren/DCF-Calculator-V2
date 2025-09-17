import requests 
from bs4 import BeautifulSoup
from bs4.element import Tag
import yfinance as yf 

def get_cagr(ticker, name, time_period):
    # name param shouald be name in the url on macrotrends 
    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 Chrome/122.0 Safari/537.36"
    }
    url = f'https://www.macrotrends.net/stocks/charts/{ticker}/{name.title()}/free-cash-flow'

    response = requests.get(url, headers=headers)
    soup = BeautifulSoup(response.text, 'html.parser')
    
    annual_title = soup.find('th', string=f'{name.title()} Annual Free Cash Flow')
    if not isinstance(annual_title, Tag):
        raise LookupError("Header not found")

    annual_table = annual_title.find_next('tbody')
    if not isinstance(annual_table, Tag):
        raise LookupError("tbody after header not found")

    free_cash_flow = annual_table.find_all('td') 
    td_text = [td.get_text(strip=True) for td in free_cash_flow]
    cash_flow_values = td_text[1::2]
    cash_flow_ints = [int(val.replace(',', '').split('.')[0]) for val in cash_flow_values][:time_period]
    cagr = (cash_flow_ints[0] / cash_flow_ints[-1]) ** (1 / len(cash_flow_ints)) - 1 

    return f'{cagr:.3f}', cash_flow_ints[0]


def calculate_wacc(ticker, capm):
    dat = yf.Ticker(ticker)
    bal_sheet = dat.get_balance_sheet().iloc[:, 0] # type: ignore
    income_stmt = dat.get_income_stmt().iloc[:, 0] # type: ignore

    market_cap = dat.info['marketCap']
    total_debt = bal_sheet['TotalDebt']
    total_firm_value = market_cap + total_debt
    
    cost_of_equity = capm
    if "InterestExpense" not in income_stmt:
        raise KeyError("Interest Expense not found in income statement")
    interest_expense = income_stmt['InterestExpense']
    cost_of_debt = interest_expense / total_debt

    if "TaxProvision" not in income_stmt:
        raise KeyError("Tax Provision not in income statement")
    tax_provision = income_stmt['TaxProvision']
    earnings_before_tax = income_stmt['PretaxIncome']
    corporate_tax_rate = tax_provision / earnings_before_tax
    weight_equity = market_cap / total_firm_value
    weight_debt = total_debt / total_firm_value

    wacc = (weight_equity * cost_of_equity) + (weight_debt * cost_of_debt * (1 - corporate_tax_rate))
    return round(wacc, 3)


def calculate_capm(ticker):
    dat = yf.Ticker(ticker)
    tnx = yf.Ticker("^TNX")
    data = tnx.history(period="1d")
    risk_free_rate = (data["Close"].iloc[-1] / 100) if not data.empty else 0.045
    beta = dat.info.get("beta", 1)
    equity_risk_premium = 0.055
    capm = risk_free_rate + beta * equity_risk_premium
    return capm

def calculate_base_fcf(ticker):
    dat = yf.Ticker(ticker)
    cash_flow = dat.get_cash_flow()
    if "FreeCashFlow" not in cash_flow.index: #type: ignore
        raise KeyError("Free Cash Flow not found in cash flow statement")
    
    fcf_row = cash_flow.loc["FreeCashFlow"] #type: ignore
    if fcf_row.shape[0] >=3:
        base_fcf = round(fcf_row.iloc[:3].mean(), 3)
    elif fcf_row.shape[0] >=1:
        base_fcf = fcf_row.iloc[0]
    else:
        raise ValueError("No Free Cash Flow Data Avaliable")
    
    return base_fcf

def calculate_dcf(ticker, base_fcf, growth_rate, perpetual_growth_rate, discount_rate, years):

    if perpetual_growth_rate >= discount_rate:
        raise ValueError(
            f"Invalid rates: perpetual_growth_rate ({perpetual_growth_rate:.2%}) "
            f"must be less than discount_rate ({discount_rate:.2%})"
        )
    
    dat = yf.Ticker(ticker)
    bal_sheet = dat.get_balance_sheet().iloc[:, 0] # type: ignore
    market_cap = dat.info['marketCap']
    shares_out = dat.info['sharesOutstanding']
    total_debt = bal_sheet['TotalDebt']
    cash_cash_eqiv = bal_sheet['CashAndCashEquivalents']

    pv_fcfs = 0
    for t in range(1, years + 1):
        fcf_t = base_fcf * (1 + growth_rate) ** t
        pv_fcfs += fcf_t / ((1 + discount_rate) ** t)

    last_year_fcf = base_fcf * (1 + growth_rate) ** years
    terminal_value = last_year_fcf * (1 + perpetual_growth_rate) / (discount_rate - perpetual_growth_rate)
    pv_terminal = terminal_value / ((1 + discount_rate) ** years)

    total_value = pv_fcfs + pv_terminal
    final_value = total_value + cash_cash_eqiv - total_debt
    intrinsic_value = round(final_value / shares_out, 2)

    return f"base case: {intrinsic_value}, 30% margin of safety: {round(intrinsic_value * 0.7, 2)}"


ticker = "tsla"
discount_rate = calculate_wacc(ticker, calculate_capm(ticker))
base_fcf = calculate_base_fcf(ticker)

fcf = calculate_dcf(ticker, base_fcf, 0.15, 0.025, discount_rate, 10)
print(f"discount rate {discount_rate}")
print(fcf)


