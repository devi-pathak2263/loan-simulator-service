from fastapi.testclient import TestClient
from app.main import app

client = TestClient(app)


def test_simulate_declining():

    response = client.post(
        "/simulate",
        json={
            "principal": 100000,
            "annual_rate": 12,
            "months": 12,
            "method": "declining"
        }
    )

    assert response.status_code == 200

    data = response.json()

    assert round(data["emi"], 2) == 8884.88
    assert data["method"] == "declining"
    assert len(data["schedule"]) == 12



def test_compare_endpoint():

    response = client.post(
        "/compare",
        json={
            "principal": 100000,
            "annual_rate": 12,
            "months": 12
        }
    )

    assert response.status_code == 200

    data = response.json()

    assert "declining" in data
    assert "flat" in data
    assert data["better_option"] == "declining"



def test_prepayment_simulation():

    response = client.post(
        "/simulate-prepayment",
        json={
            "principal": 100000,
            "annual_rate": 12,
            "months": 12,
            "prepayment_month": 6,
            "extra_payment": 20000,
            "strategy": "reduce_tenure"
        }
    )

    assert response.status_code == 200

    data = response.json()

    assert data["months_saved"] > 0




def test_what_if_simulation():

    response = client.post(
        "/what-if",
        json={
            "principal": 100000,
            "annual_rate": 12,
            "months": 12,
            "new_rate": 10,
            "extra_payment_monthly": 1000
        }
    )

    assert response.status_code == 200

    data = response.json()

    assert data["interest_saved"] > 0