# Automated Episode Downloader & Telegram Uploader

A production-ready Python automation script that:
- Scrapes a genre page
- Randomly selects an episode
- Extracts the direct download link
- Downloads the file to a temp directory
- Uploads it to a private Telegram channel using Pyrogram
- Deletes the file after upload
- Maintains a log to avoid duplicate downloads
- Sends admin notifications on start, progress, success, and errors

Designed to run continuously and safely on **Termux or Linux**.

---

## Features

- Random episode selection
- Duplicate prevention using TXT log
- Temporary storage handling
- Clean console logging
- Admin DM notifications
- Automatic retry on failure
- Production-safe infinite loop

---

## Requirements

- Python 3.9+
- Termux or Linux
- Telegram API credentials

### Python packages

```bash
pip install pyrogram tgcrypto requests beautifulsoup4
