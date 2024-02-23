# docker build -t entox .
# docker run -it -v "$(pwd)":/app -p 5067:5000 entox /bin/bash

# Tag the built image for Docker Hub. Replace 'your_dockerhub_username' with your actual Docker Hub username:
# docker tag entox your_dockerhub_username/entox:latest

# Push the tagged image to Docker Hub. Make sure you are logged in to Docker Hub via 'docker login':
#  docker push your_dockerhub_username/entox:latest

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

# Copy the rest of your application's code
COPY ./ /app

# Expose the port the app runs on
EXPOSE 5000

# Set environment variables
ENV FLASK_APP=app.py
ENV FLASK_RUN_HOST=0.0.0.0
ENV FLASK_ENV=production

# Start the Flask application
CMD ["flask", "run"]
