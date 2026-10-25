
from flask import Flask, jsonify, render_template, make_response
from datetime import datetime, timezone

app = Flask(__name__)

VERSION = "1.1.0"
STARTED_AT = datetime.now(timezone.utc).isoformat()


@app.route("/")
def home():
    return render_template(
        "index.html",
        version=VERSION,
        started_at=STARTED_AT
    )


@app.route("/health")
def health():
    return jsonify({
        "status": "healthy",
        "version": VERSION,
        "started_at": STARTED_AT
    }), 200


@app.route("/api/status")
def api_status():
    return jsonify({
        "application": "CloudPulse",
        "status": "running",
        "version": VERSION,
        "environment": "Docker / AWS EC2",
        "health_url": "/health",
        "started_at": STARTED_AT
    }), 200


@app.after_request
def security_headers(response):
    response.headers["X-Content-Type-Options"] = "nosniff"
    response.headers["X-Frame-Options"] = "SAMEORIGIN"
    response.headers["Cache-Control"] = "no-store"
    return response


if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000, debug=False)
