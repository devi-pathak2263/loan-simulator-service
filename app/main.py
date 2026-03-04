from fastapi import FastAPI
from pydantic import BaseModel
from loan_amortization_engine.engine import calculate_declining

app = FastAPI(title="Loan Amortization Simulator")

class LoanRequest(BaseModel):
    principal: float
    annual_rate: float
    months: int
    method: str = "declining"

@app.post("/simulate")
def simulate_loan(data: LoanRequest):

    if data.method == "declining":
        return calculate_declining(
            data.principal,
            data.annual_rate,
            data.months
        )

    return {"error": "Method not supported yet"}