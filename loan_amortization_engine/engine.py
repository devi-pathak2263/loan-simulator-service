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

# -----------------------------
# Calculate Flat
# -----------------------------

def calculate_flat(principal, annual_rate, months):

    years = Decimal(months) / Decimal("12")

    total_interest = principal * (annual_rate / Decimal("100")) * years
    total_interest = total_interest.quantize(Decimal("0.01"))

    total_payment = (principal + total_interest).quantize(Decimal("0.01"))

    emi = (total_payment / Decimal(months)).quantize(Decimal("0.01"))

    schedule = generate_flat_schedule(principal, annual_rate, months)

    return {
        "method": "flat",
        "emi": float(emi),
        "total_interest": float(total_interest),
        "total_payment": float(total_payment),
        "schedule": schedule
    }


# -----------------------------
# Generate Flat Amortization Schedule
# -----------------------------

def generate_flat_schedule(principal, annual_rate, months):
    schedule = []

    years = Decimal(months) / Decimal("12")
    total_interest = principal * (annual_rate / Decimal("100")) * years
    monthly_interest = (total_interest / Decimal(months)).quantize(Decimal("0.01"))
    monthly_principal = (principal / Decimal(months)).quantize(Decimal("0.01"))

    remaining_balance = principal

    for month in range(1, months + 1):

        if month == months:
            monthly_principal = remaining_balance.quantize(Decimal("0.01"))

        emi = (monthly_principal + monthly_interest).quantize(Decimal("0.01"))

        remaining_balance = (remaining_balance - monthly_principal).quantize(Decimal("0.01"))

        schedule.append({
            "month": month,
            "emi": float(emi),
            "interest": float(monthly_interest),
            "principal": float(monthly_principal),
            "balance": float(remaining_balance)
        })

    return schedule


# -----------------------------
# prepayment simulation (Declining)
# -----------------------------

# calculate_emi()
#        ↓
# generate_schedule() → before prepayment
#        ↓
# reduce balance
#        ↓
# generate_schedule() → after prepayment
#        ↓
# merge schedules


def simulate_declining_prepayment(
    principal: float,
    annual_rate: float,
    months: int,
    prepayment_month: int,
    extra_payment: float,
    strategy: str = "reduce_tenure"
):

    principal = Decimal(str(principal))
    annual_rate = Decimal(str(annual_rate))
    extra_payment = Decimal(str(extra_payment))

    monthly_rate = annual_rate / Decimal("12") / Decimal("100")

    emi = calculate_emi(principal, annual_rate, months)
    emi = emi.quantize(Decimal("0.01"))

    remaining_balance = principal
    total_interest = Decimal("0.00")

    schedule = []

    for month in range(1, months + 1):

        interest = (remaining_balance * monthly_rate).quantize(Decimal("0.01"))
        principal_component = (emi - interest).quantize(Decimal("0.01"))

        payment = emi

        # Apply prepayment
        if month == prepayment_month:

            principal_component += extra_payment
            payment += extra_payment

            # Update remaining balance immediately
            remaining_balance = (
                remaining_balance - principal_component
            ).quantize(Decimal("0.01"))

            # Strategy: Reduce EMI
            if strategy == "reduce_emi":

                remaining_months = months - month

                if remaining_months > 0:
                    emi = calculate_emi(
                        remaining_balance,
                        annual_rate,
                        remaining_months
                    ).quantize(Decimal("0.01"))

            total_interest += interest

            schedule.append({
                "month": month,
                "emi": float(payment),
                "interest": float(interest),
                "principal": float(principal_component),
                "balance": float(remaining_balance)
            })
            continue

        # Prevent overpayment
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

        # Stop if loan closed
        if remaining_balance <= Decimal("0.00"):
            break

    return {
        "method": "declining_with_prepayment",
        "strategy": strategy,
        "emi": float(emi),
        "prepayment_month": prepayment_month,
        "extra_payment": float(extra_payment),
        "months_saved": months - len(schedule),
        "loan_closed_month": len(schedule),
        "total_interest": float(total_interest),
        "schedule": schedule
    }