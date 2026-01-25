# --- Base image ---
FROM python:3.11-slim

# --- Set working directory ---
WORKDIR /app

# --- Copy Python scripts and API ---
COPY scripts/ /app/scripts/
COPY api/ /app/api/

# --- Copy vault ---
COPY vault/ /app/vault/

# --- Create store directory for SQLite DB ---
RUN mkdir -p /app/store

# --- Install dependencies ---
RUN pip install --no-cache-dir fastapi uvicorn pyyaml rapidfuzz

# --- Build the SQLite DB ---
RUN python scripts/build_sqlite.py

# --- Expose API port ---
EXPOSE 8000

# --- Start FastAPI ---
CMD ["uvicorn", "api.api:app", "--host", "0.0.0.0", "--port", "8000"]
