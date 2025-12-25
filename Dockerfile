FROM ubuntu:24.04

ENV DEBIAN_FRONTEND=noninteractive
ENV PATH="/root/.local/bin:/root/.deno/bin:$PATH"

RUN apt-get update && apt-get install -y \
    unzip \
    curl \
    python3 \
    python3-pip \
    python3-venv \
    && rm -rf /var/lib/apt/lists/*

COPY --from=ghcr.io/astral-sh/uv:latest /uv /usr/local/bin/uv

RUN curl -fsSL https://deno.land/install.sh | sh

COPY . /app
WORKDIR /app

RUN apt-get update && apt-get install -y build-essential \
    && uv sync \
    && apt-get remove -y build-essential \
    && apt-get autoremove -y \
    && rm -rf /var/lib/apt/lists/* \
    && uv cache clean

ENV IS_DEVELOPMENT=false
CMD ["uv", "run", "bot.py"]