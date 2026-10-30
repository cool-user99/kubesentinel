"""KubeSentinel API — Flask + PostgreSQL, instrumentée pour Prometheus."""
import os
import time

import psycopg
from flask import Flask, Response, g, jsonify, request
from prometheus_client import CONTENT_TYPE_LATEST, Counter, Histogram, generate_latest

app = Flask(__name__)

# Métriques Prometheus. Le label "endpoint" utilise la route (ex: /api/items)
# et non l'URL brute, pour garder une cardinalité bornée.
REQUESTS = Counter(
    "http_requests_total", "Nombre de requêtes HTTP", ["method", "endpoint", "status"]
)
LATENCY = Histogram(
    "http_request_duration_seconds", "Latence des requêtes HTTP", ["endpoint"]
)


def get_conn():
    """Ouvre une connexion PostgreSQL à partir des variables d'environnement."""
    return psycopg.connect(
        host=os.environ.get("DB_HOST", "localhost"),
        port=int(os.environ.get("DB_PORT", "5432")),
        dbname=os.environ.get("DB_NAME", "kubesentinel"),
        user=os.environ.get("DB_USER", "kubesentinel"),
        password=os.environ.get("DB_PASSWORD", ""),
        connect_timeout=3,
    )


@app.before_request
def start_timer():
    g.start = time.perf_counter()


@app.after_request
def record_metrics(response):
    endpoint = request.url_rule.rule if request.url_rule else "unknown"
    REQUESTS.labels(request.method, endpoint, response.status_code).inc()
    LATENCY.labels(endpoint).observe(time.perf_counter() - g.start)
    return response


@app.get("/health")
def health():
    """Liveness : le processus répond. Ne dépend PAS de la base."""
    return jsonify(status="ok")


@app.get("/ready")
def ready():
    """Readiness : l'API peut servir du trafic seulement si la base répond."""
    try:
        with get_conn() as conn:
            conn.execute("SELECT 1")
        return jsonify(status="ready")
    except psycopg.Error:
        return jsonify(status="database unavailable"), 503


@app.get("/metrics")
def metrics():
    return Response(generate_latest(), mimetype=CONTENT_TYPE_LATEST)


@app.get("/api/items")
def list_items():
    with get_conn() as conn:
        rows = conn.execute(
            "SELECT id, name, created_at FROM items ORDER BY id DESC LIMIT 50"
        ).fetchall()
    return jsonify(
        [{"id": r[0], "name": r[1], "created_at": r[2].isoformat()} for r in rows]
    )


@app.post("/api/items")
def create_item():
    data = request.get_json(silent=True) or {}
    name = str(data.get("name", "")).strip()
    if not name or len(name) > 100:
        return jsonify(error="'name' est requis (1 à 100 caractères)"), 400
    with get_conn() as conn:
        item_id = conn.execute(
            "INSERT INTO items (name) VALUES (%s) RETURNING id", (name,)
        ).fetchone()[0]
    return jsonify(id=item_id, name=name), 201


if __name__ == "__main__":
    app.run(host="0.0.0.0", port=8000)
