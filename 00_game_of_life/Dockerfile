FROM python:3.13
ADD . /app
WORKDIR /app
RUN pip install uv
RUN uv sync
CMD uv run uvicorn --host 0.0.0.0 --port 8001 main:app
