
import pytest
from app import app


@pytest.fixture()
def client():
    app.config["TESTING"] = True

    with app.test_client() as client:
        yield client


def test_dashboard_loads(client):
    response = client.get("/")
    assert response.status_code == 200
    assert b"CloudPulse" in response.data


def test_health_endpoint(client):
    response = client.get("/health")

    assert response.status_code == 200
    assert response.json["status"] == "healthy"


def test_status_endpoint(client):
    response = client.get("/api/status")

    assert response.status_code == 200
    assert response.json["application"] == "CloudPulse"
    assert response.json["version"] == "1.0.0"
