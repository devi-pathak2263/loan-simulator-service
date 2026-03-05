from fastapi import FastAPI
from pydantic import BaseModel
from fastapi import HTTPException
from decimal import Decimal
from loan_amortization_engine.engine import (
    calculate_declining,
    calculate_flat,
    simulate_declining_prepayment
)
app = FastAPI(title="Loan Amortization Simulator")


# ---------------------
# Request Models
# ---------------------

class LoanRequest(BaseModel):
    principal: float
    annual_rate: float
    months: int
    method: str = "declining"

class CompareRequest(BaseModel):
    principal: float
    annual_rate: float
    months: int

class PrepaymentRequest(BaseModel):
    principal: float
    annual_rate: float
    months: int
    prepayment_month: int
    extra_payment: float
    strategy: str = "reduce_tenure"

# ---------------------
# Endpoints
# ---------------------

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


@app.post("/compare")
def compare_loan(data: CompareRequest):

    principal = Decimal(str(data.principal))
    annual_rate = Decimal(str(data.annual_rate))
    months = data.months

    declining_result = calculate_declining(
        principal,
        annual_rate,
        months
    )

    flat_result = calculate_flat(
        principal,
        annual_rate,
        months
    )

    difference = round(
        abs(flat_result["total_interest"] - declining_result["total_interest"]), 2
    )

    better_option = (
        "declining"
        if declining_result["total_interest"] < flat_result["total_interest"]
        else "flat"
    )

    return {
        "declining": declining_result,
        "flat": flat_result,
        "difference_in_interest": difference,
        "better_option": better_option
    }


@app.post("/simulate-prepayment")
def simulate_prepayment(data: PrepaymentRequest):

    if data.strategy not in ["reduce_tenure", "reduce_emi"]:
        raise HTTPException(
        status_code=400,
        detail="Strategy must be reduce_tenure or reduce_emi"
    )

    if data.prepayment_month > data.months:
        raise HTTPException(
            status_code=400,
            detail="Prepayment month cannot exceed loan tenure"
        ) 
    
    if data.prepayment_month < 1:
        raise HTTPException(
        status_code=400,
        detail="Prepayment month must be at least 1"
    )

    return simulate_declining_prepayment(
        data.principal,
        data.annual_rate,
        data.months,
        data.prepayment_month,
        data.extra_payment,
        data.strategy
    )