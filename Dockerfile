FROM python:3.12-slim

# ffmpeg для склейки DASH-потоков и автосплита, curl для скачивания deno
RUN apt-get update && \
    apt-get install -y --no-install-recommends ffmpeg curl unzip && \
    rm -rf /var/lib/apt/lists/*

# deno — JS-рантайм для yt-dlp (решает n-challenge для некоторых видеохостингов)
RUN curl -fsSL https://github.com/denoland/deno/releases/latest/download/deno-x86_64-unknown-linux-gnu.zip \
    -o /tmp/deno.zip && \
    unzip /tmp/deno.zip -d /usr/local/bin/ && \
    chmod +x /usr/local/bin/deno && \
    rm /tmp/deno.zip

WORKDIR /app

# сначала зависимости (кэшируется Docker слоем)
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# потом код
COPY bot/ bot/

CMD ["python", "-m", "bot.main"]
