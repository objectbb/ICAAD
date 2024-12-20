FROM python:3.13 AS builder

ENV PYTHONUNBUFFERED=1 \
    PYTHONDONTWRITEBYTECODE=1
WORKDIR /app

RUN pip install poetry
RUN poetry config virtualenvs.in-project true
COPY pyproject.toml poetry.lock ./
RUN poetry install
FROM python:3.13-slim
WORKDIR /app
COPY --from=builder /app/.venv .venv/
COPY . .

# Install wkhtmltopdf
RUN apt update && apt -y upgrade
RUN apt install -y --no-install-recommends wkhtmltopdf 

CMD ["/app/.venv/bin/fastapi", "run"]
