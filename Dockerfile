FROM alpine:3.23

RUN apk add uv python3 deno

COPY . /app
WORKDIR /app

RUN uv sync

ENV IS_DEVELOPMENT=false
CMD ["uv", "run", "bot.py"]

