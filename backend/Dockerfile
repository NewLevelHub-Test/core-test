FROM python:3.11-slim

RUN apt-get update && apt-get install -y --no-install-recommends \
    stockfish \
    build-essential \
    libpq-dev \
    gcc \
    libheif-dev \
    && rm -rf /var/lib/apt/lists/*

RUN useradd --create-home appuser

WORKDIR /app

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY . .

RUN mkdir -p /app/uploads && chown -R appuser:appuser /app

EXPOSE 5000

COPY entrypoint.sh /app/entrypoint.sh
RUN chmod +x /app/entrypoint.sh

USER appuser

CMD ["/app/entrypoint.sh"]