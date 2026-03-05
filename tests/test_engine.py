from decimal import Decimal
from loan_amortization_engine.engine import (
    calculate_declining,
    calculate_flat,
    simulate_declining_prepayment,
    calculate_emi
)


def test_declining_emi_calculation():

    result = calculate_declining(
        principal=100000,
        annual_rate=12,
        months=12
    )

    # EMI should match known value
    assert round(result["emi"], 2) == 8884.88

    # Schedule length should match loan tenure
    assert len(result["schedule"]) == 12

    # Loan should end with balance 0
    assert result["schedule"][-1]["balance"] == 0




def test_flat_interest_calculation():

    result = calculate_flat(
        principal=100000,
        annual_rate=12,
        months=12
    )

    # Total interest should be fixed
    assert round(result["total_interest"], 2) == 12000

    # Schedule length
    assert len(result["schedule"]) == 12


def test_prepayment_reduces_tenure():

    result = simulate_declining_prepayment(
        principal=100000,
        annual_rate=12,
        months=12,
        prepayment_month=6,
        extra_payment=20000
    )

    # Loan should close earlier
    assert result["months_saved"] > 0

    # Final balance must be zero
    assert result["schedule"][-1]["balance"] == 0