FROM python:3.12-slim

ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1 \
    DOWNLOAD_DIR=/data/downloads \
    ENABLE_OPEN_DOWNLOADS=0

RUN apt-get update \
    && apt-get install -y --no-install-recommends ffmpeg curl unzip \
    && curl -fsSL https://deno.land/install.sh | DENO_INSTALL=/usr/local sh \
    && rm -rf /var/lib/apt/lists/*

WORKDIR /app

COPY requirements.txt ./requirements.txt
RUN pip install --no-cache-dir -r requirements.txt gunicorn==23.0.0

COPY . .

RUN mkdir -p /data/downloads

EXPOSE 4000

CMD ["gunicorn", "--bind", "0.0.0.0:4000", "--workers", "2", "--threads", "4", "--timeout", "1800", "app:app"]
