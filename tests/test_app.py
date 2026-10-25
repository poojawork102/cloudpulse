import pytest
from app import app, VERSION


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
    assert response.json["version"] == VERSION


def test_status_endpoint(client):
    response = client.get("/api/status")

    assert response.status_code == 200
    assert response.json["application"] == "CloudPulse"
    # Compare against the app's own VERSION so a version bump doesn't break the pipeline
    assert response.json["version"] == VERSION
