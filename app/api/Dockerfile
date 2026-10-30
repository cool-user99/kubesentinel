# --- Étape 1 : builder — installe les dépendances dans un venv isolé
FROM python:3.12.16-slim-bookworm AS builder
RUN python -m venv /opt/venv
ENV PATH="/opt/venv/bin:$PATH"
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# --- Étape 2 : runtime — uniquement le venv et le code, exécuté en non-root
FROM python:3.12.16-slim-bookworm
ENV PATH="/opt/venv/bin:$PATH" \
    PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1
RUN groupadd --gid 10001 app \
    && useradd --uid 10001 --gid app --no-create-home --shell /usr/sbin/nologin app
WORKDIR /app
COPY --from=builder /opt/venv /opt/venv
COPY app.py .
# UID numérique : permet à Kubernetes (runAsNonRoot) de vérifier qu'on n'est pas root
USER 10001
EXPOSE 8000
# 1 worker : les métriques Prometheus restent cohérentes ; on scale par pods (HPA)
CMD ["gunicorn", "--bind", "0.0.0.0:8000", "--workers", "1", "--threads", "4", "--access-logfile", "-", "app:app"]
