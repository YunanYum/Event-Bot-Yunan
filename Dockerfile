# --- Stage 1: build ---
FROM python:3.12-slim AS builder

WORKDIR /app

COPY requirements.txt .
RUN pip install --no-cache-dir --prefix=/install -r requirements.txt

# --- Runtime ---
FROM python:3.12-slim AS runtime

WORKDIR /app

RUN apt-get update && apt-get install -y --no-install-recommends ca-certificates \
    && rm -rf /var/lib/apt/lists/*

COPY --from=builder /install /usr/local

COPY . .

# Ship the repo's default data/ (e.g. scripts.json) under a separate path
RUN mkdir -p /app/data-seed && cp -r /app/data/. /app/data-seed/ 2>/dev/null || true

RUN useradd --create-home --uid 1000 botuser \
    && chown -R botuser:botuser /app
USER botuser

VOLUME ["/app/data"]

ENTRYPOINT ["/bin/sh", "-c", "cp -rn /app/data-seed/. /app/data/ 2>/dev/null; exec python main.py"]
