FROM python:3.13-slim

WORKDIR /app

RUN pip install uv

COPY pyproject.toml ./
RUN uv venv .venv && uv pip install -e .

COPY . .

EXPOSE 8000

CMD ["uv", "run", "uvicorn", "src.api.main:app", "--host", "0.0.0.0", "--port", "8000"]
