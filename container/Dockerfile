# docker build -t entox .
# docker run -it -v "$(pwd)":/app -p 5067:5000 entox /bin/bash
# Use the specified image as the base
FROM python:3.10-slim-buster

# Set the working directory
WORKDIR /app

# Copy only pyproject.toml and poetry.lock first to leverage Docker caching
COPY pyproject.toml poetry.lock /app/

# Install Poetry
RUN apt-get update && apt-get install -y curl
RUN curl -sSL https://install.python-poetry.org | python - 
ENV PATH="/root/.local/bin:$PATH"

# Install project dependencies
RUN poetry config virtualenvs.create false \
  && poetry install --no-dev --no-interaction --no-ansi

# RUN pip install https://huprdontoxnlpst.blob.core.windows.net/en-tox/en_tox-2.0.0-py3-none-any.whl

EXPOSE 5000
