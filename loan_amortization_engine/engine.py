from decimal import Decimal, getcontext

getcontext().prec = 28


# -----------------------------
# Core EMI Formula (Declining)
# -----------------------------
def calculate_emi(principal, annual_rate, months):
    if annual_rate == 0:
        return principal / Decimal(months)

    monthly_rate = annual_rate / Decimal("12") / Decimal("100")
    one_plus_r_power_n = (Decimal("1") + monthly_rate) ** months

    emi = (
        principal * monthly_rate * one_plus_r_power_n
        / (one_plus_r_power_n - Decimal("1"))
    )

    return emi


# -----------------------------
# Generate Amortization Schedule
# -----------------------------
def generate_schedule(principal, annual_rate, months, emi):
    schedule = []

    monthly_rate = annual_rate / Decimal("12") / Decimal("100")
    remaining_balance = principal.quantize(Decimal("0.01"))

    total_interest = Decimal("0.00")

    for month in range(1, months + 1):

        interest = (remaining_balance * monthly_rate).quantize(Decimal("0.01"))
        principal_component = (emi - interest).quantize(Decimal("0.01"))

        if month == months:
            principal_component = remaining_balance
            emi_adjusted = (principal_component + interest).quantize(Decimal("0.01"))
            remaining_balance = Decimal("0.00")
        else:
            emi_adjusted = emi.quantize(Decimal("0.01"))
            remaining_balance = (remaining_balance - principal_component).quantize(Decimal("0.01"))

        total_interest += interest

        schedule.append({
            "month": month,
            "emi": float(emi_adjusted),
            "interest": float(interest),
            "principal": float(principal_component),
            "balance": float(remaining_balance)
        })

    return schedule, total_interest


# -----------------------------
# Public API Function (Declining)
# -----------------------------
def calculate_declining(principal: float, annual_rate: float, months: int):

    principal = Decimal(str(principal))
    annual_rate = Decimal(str(annual_rate))

    emi = calculate_emi(principal, annual_rate, months)
    emi = emi.quantize(Decimal("0.01"))

    schedule, total_interest = generate_schedule(
        principal, annual_rate, months, emi
    )

    return {
        "method": "declining",
        "emi": float(emi),
        "total_interest": float(total_interest),
        "total_payment": float(principal + total_interest),
        "schedule": schedule
    }