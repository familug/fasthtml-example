FROM python:3.13
WORKDIR /app
RUN pip install uv
ADD pyproject.toml /app/
RUN uv sync
ADD . /app
CMD uv run uvicorn --host 0.0.0.0 --port 8001 main:app
