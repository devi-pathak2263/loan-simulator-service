# Loan Amortization Simulator

FastAPI-based microservice for loan amortization calculations and financial scenario simulations.

## Features

- Declining balance EMI calculation
- Flat interest loan method
- Loan comparison
- Prepayment simulation
- What-if loan scenario simulation
- Unit tested with pytest

## API Endpoints

POST /simulate  
POST /compare  
POST /simulate-prepayment  
POST /what-if  

## Run Locally

pip install -r requirements.txt

uvicorn app.main:app --reload

Open:

http://127.0.0.1:8000/docs