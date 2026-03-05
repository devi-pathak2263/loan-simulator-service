from fastapi import FastAPI
from pydantic import BaseModel
from fastapi import HTTPException
from decimal import Decimal
from loan_amortization_engine.engine import (
    calculate_declining,
    calculate_flat,
    simulate_declining_prepayment,
    calculate_emi
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

class WhatIfRequest(BaseModel):
    principal: float
    annual_rate: float
    months: int

    new_rate: float | None = None
    extra_payment_monthly: float | None = None

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


@app.post("/what-if")
def what_if_simulation(data: WhatIfRequest):

    principal = Decimal(str(data.principal))
    annual_rate = Decimal(str(data.annual_rate))
    months = data.months

    #validation
    if data.principal <= 0:
        raise HTTPException(status_code=400, detail="Principal must be positive")

    if data.months <= 0:
        raise HTTPException(status_code=400, detail="Months must be greater than zero")

    if data.annual_rate < 0:
        raise HTTPException(status_code=400, detail="Interest rate cannot be negative")
    
    # Current loan
    current = calculate_declining(principal, annual_rate, months)

    new_rate = annual_rate
    extra_payment = Decimal("0")

    if data.new_rate is not None:
        new_rate = Decimal(str(data.new_rate))

    if data.extra_payment_monthly is not None:
        extra_payment = Decimal(str(data.extra_payment_monthly))

    monthly_rate = new_rate / Decimal("12") / Decimal("100")

    emi = calculate_emi(principal, new_rate, months)
    emi = emi.quantize(Decimal("0.01"))

    remaining_balance = principal
    total_interest = Decimal("0")
    schedule = []

    for month in range(1, months + 1):

        interest = (remaining_balance * monthly_rate).quantize(Decimal("0.01"))

        payment = emi + extra_payment
        principal_component = (payment - interest).quantize(Decimal("0.01"))

        if principal_component > remaining_balance:
            principal_component = remaining_balance
            payment = principal_component + interest

        remaining_balance = (remaining_balance - principal_component).quantize(Decimal("0.01"))

        total_interest += interest

        schedule.append({
            "month": month,
            "emi": float(payment),
            "interest": float(interest),
            "principal": float(principal_component),
            "balance": float(remaining_balance)
        })

        if remaining_balance <= 0:
            break

    new_result = {
        "emi": float(emi),
        "total_interest": float(total_interest),
        "months_taken": len(schedule),
        "schedule": schedule
    }

    savings = current["total_interest"] - new_result["total_interest"]

    return {
        "current_loan": current,
        "what_if_scenario": new_result,
        "scenario": {
        "new_rate": data.new_rate,
        "extra_payment_monthly": data.extra_payment_monthly
        },
        "interest_saved": round(savings, 2)
    }