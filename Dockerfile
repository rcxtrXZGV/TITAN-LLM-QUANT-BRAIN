FROM debian:bookworm-slim

ENV DEBIAN_FRONTEND=noninteractive
ENV WINEPREFIX=/root/.wine
ENV WINEARCH=win64
ENV DISPLAY=:1

# Install base dependencies, Wine, Xvfb and Python
RUN dpkg --add-architecture i386 && \
    apt-get update && apt-get install -y --no-install-recommends \
    wine \
    wine64 \
    wine32 \
    xvfb \
    x11vnc \
    wget \
    curl \
    cabextract \
    python3 \
    python3-pip \
    python3-venv \
    procps \
    git \
    unzip && \
    apt-get clean && rm -rf /var/lib/apt/lists/*

# Setup virtual display and working directory
WORKDIR /app

# Copy application files
COPY . /app

# Setup start script
COPY start.sh /start.sh
RUN chmod +x /start.sh

CMD ["/start.sh"]
