# Telegram Channel Metrics

Read-only Telegram channel metric aggregation with private environment-based API configuration.

Python 3.10+; install requirements.txt, then privately set TELEGRAM_API_ID,
TELEGRAM_API_HASH and comma-separated TELEGRAM_CHANNELS (only channels you are allowed to access).
Run `python analyse.py` manually. Missing configuration fails before a Telegram connection attempt.
Telethon may create a local login session; session/config/history files must stay outside Git.
The tool reads participant/view/reaction metadata and prints averages. Source publication checks do
not log in to Telegram, fetch posts or send any messages. Current Telegram SDK/service compatibility
was not validated by a real login.

See VALIDATION.md for actual checks.
