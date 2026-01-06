# Streak Bot Dockerfile
#
# Build:  docker build -t streak-bot .
# Run:    docker run -d --name streak-bot \
#           -e TELEGRAM_BOT_TOKEN=your-token \
#           -v /path/to/.streak:/app/.streak \
#           streak-bot

FROM python:3.11-slim

WORKDIR /app

# Install git for sync functionality
RUN apt-get update && apt-get install -y --no-install-recommends \
    git \
    && rm -rf /var/lib/apt/lists/*

# Install Python dependencies
RUN pip install --no-cache-dir "python-telegram-bot[job-queue]==21.0" pytz

# Copy bot script
COPY streak-bot.py .

# Environment variables (override at runtime)
ENV TELEGRAM_BOT_TOKEN=""
ENV STREAK_PATH="/app/.streak"
ENV GIT_AUTO_SYNC="true"
ENV ALLOWED_USERS=""
ENV NOTIFICATION_ENABLED="true"
ENV NOTIFICATION_HOUR="9"
ENV NOTIFICATION_MINUTE="0"
ENV TIMEZONE="UTC"

# Health check
HEALTHCHECK --interval=30s --timeout=10s --start-period=5s --retries=3 \
    CMD python -c "import urllib.request; urllib.request.urlopen('https://api.telegram.org')" || exit 1

# Run the bot
CMD ["python", "streak-bot.py"]
