FROM python:3.13-slim

WORKDIR /app

RUN pip install uv

COPY pyproject.toml ./
RUN uv venv .venv && uv pip install -e .

COPY . .

RUN chmod +x entrypoint.sh

EXPOSE 8000

ENTRYPOINT ["./entrypoint.sh"]
