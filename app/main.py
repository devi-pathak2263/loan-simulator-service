from fastapi import FastAPI
from pydantic import BaseModel
from fastapi import HTTPException
from decimal import Decimal
from loan_amortization_engine.engine import (
    calculate_declining,
    calculate_flat
)
app = FastAPI(title="Loan Amortization Simulator")

class LoanRequest(BaseModel):
    principal: float
    annual_rate: float
    months: int
    method: str = "declining"

@app.post("/simulate")
def simulate_loan(data: LoanRequest):

    principal = Decimal(str(data.principal))
    annual_rate = Decimal(str(data.annual_rate))
    months = data.months

    if data.method == "declining":
        return calculate_declining(
            principal,
            annual_rate,
            months
        )
    elif data.method == "flat":
        return calculate_flat(
            principal,
            annual_rate,
            months
        )

    else:
        raise HTTPException(
            status_code=400,
            detail="Invalid method. Supported methods: declining, flat"
        )