FROM python:3.12-slim
WORKDIR /app
RUN pip install --no-cache-dir poetry
COPY pyproject.toml ./
RUN poetry config virtualenvs.create false && poetry install --only main --no-root
COPY store ./store
EXPOSE 8000
CMD ["uvicorn", "store.main:app", "--host", "0.0.0.0", "--port", "8000"]
