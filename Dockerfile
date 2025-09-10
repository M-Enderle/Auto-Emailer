FROM python:3.12-slim

WORKDIR /app

# Install poetry
RUN pip install poetry

# Copy poetry files
COPY pyproject.toml poetry.lock* ./
COPY README.md ./
COPY emailer/ ./emailer/
COPY config.toml ./

# Configure poetry: don't create virtual env, install dependencies
RUN poetry config virtualenvs.create false \
    && poetry install

ENV PORT=8000

CMD ["uvicorn", "emailer.main:app", "--host", "0.0.0.0", "--port", "8000"]
