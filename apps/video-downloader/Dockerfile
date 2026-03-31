FROM python:3.12-slim

ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1 \
    DOWNLOAD_DIR=/data/downloads \
    ENABLE_OPEN_DOWNLOADS=0

RUN apt-get update \
    && apt-get install -y --no-install-recommends ffmpeg curl unzip \
    && curl -fsSL https://deno.land/install.sh | DENO_INSTALL=/usr/local sh \
    && ARCH=$(uname -m) \
    && case "${ARCH}" in \
         x86_64)  BGUTIL_ARCH="x86_64"  ;; \
         aarch64) BGUTIL_ARCH="aarch64" ;; \
         *) echo "Unsupported arch: ${ARCH}" && exit 1 ;; \
       esac \
    && BGUTIL_TAG=$(curl -fsSL https://api.github.com/repos/jim60105/bgutil-ytdlp-pot-provider-rs/releases/latest | grep '"tag_name"' | cut -d'"' -f4) \
    && curl -fsSL -o /usr/local/bin/bgutil-pot "https://github.com/jim60105/bgutil-ytdlp-pot-provider-rs/releases/download/${BGUTIL_TAG}/bgutil-pot-linux-${BGUTIL_ARCH}" \
    && chmod +x /usr/local/bin/bgutil-pot \
    && PLUGIN_DIR=$(python3 -c 'import site; print(site.getsitepackages()[0])') \
    && curl -fsSL -o /tmp/bgutil-plugin.zip "https://github.com/jim60105/bgutil-ytdlp-pot-provider-rs/releases/download/${BGUTIL_TAG}/bgutil-ytdlp-pot-provider-rs.zip" \
    && unzip -q /tmp/bgutil-plugin.zip -d "${PLUGIN_DIR}" \
    && rm /tmp/bgutil-plugin.zip \
    && rm -rf /var/lib/apt/lists/*

WORKDIR /app

COPY requirements.txt ./requirements.txt
RUN pip install --no-cache-dir -r requirements.txt gunicorn==23.0.0

COPY . .

RUN chmod +x entrypoint.sh && mkdir -p /data/downloads

EXPOSE 4000

CMD ["/app/entrypoint.sh"]
