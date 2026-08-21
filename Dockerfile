FROM python:3.12-slim-bookworm AS base

# System dependencies
RUN apt-get update && apt-get install -y --no-install-recommends \
    build-essential \
    libssl-dev \
    libffi-dev \
    libgfortran5 \
    gcc \
    g++ \
    cmake \
    pkg-config \
    curl \
    git \
    sqlite3 \
    libatlas3-base \
    && rm -rf /var/lib/apt/lists/*

# Python env
ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONFAULTHANDLER=1 \
    PIP_NO_CACHE_DIR=1 \
    FT_APP_ENV=docker

# App user
RUN useradd -m -u 1000 -s /bin/bash orazenuser
WORKDIR /app

# Install Python deps
COPY requirements.txt requirements-orazenai.txt requirements-orazenai-rl.txt ./
RUN pip install --upgrade pip wheel && \
    pip install -r requirements.txt && \
    pip install -r requirements-orazenai.txt

# Copy source
COPY --chown=orazenuser:orazenuser . /app

# Switch to non-root
USER orazenuser

EXPOSE 8000

CMD ["python", "web/app.py"]
