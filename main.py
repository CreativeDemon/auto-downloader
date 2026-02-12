import os
import sys
import time
import random
import logging
import requests
from bs4 import BeautifulSoup
from urllib.parse import urljoin, unquote
from pyrogram import Client
from config import *

# ---------------- LOGGING ---------------- #

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s | %(levelname)s | %(message)s",
    handlers=[logging.StreamHandler(sys.stdout)]
)

log = logging.getLogger("AUTO-DL")

HEADERS = {"User-Agent": "Mozilla/5.0"}

# ---------------- HELPERS ---------------- #

def notify_admin(app, text):
    try:
        app.send_message(ADMIN_ID, text)
    except:
        pass

def load_downloaded():
    if not os.path.exists(LOG_FILE):
        return set()
    with open(LOG_FILE, "r") as f:
        return set(x.strip() for x in f)

def save_downloaded(url):
    with open(LOG_FILE, "a") as f:
        f.write(url + "\n")

# ---------------- SCRAPING ---------------- #

def get_episode_pages():
    r = requests.get(GENRE_URL, headers=HEADERS, timeout=20)
    r.raise_for_status()
    soup = BeautifulSoup(r.text, "html.parser")

    links = set()
    for a in soup.find_all("a", href=True):
        href = a["href"]
        if href.startswith("https://hentaigasm.com/") and "/episode/" in href:
            links.add(href)

    return list(links)

def get_download_link(page_url):
    r = requests.get(page_url, headers=HEADERS, timeout=20)
    r.raise_for_status()
    soup = BeautifulSoup(r.text, "html.parser")

    for a in soup.find_all("a", href=True):
        if a.get_text(strip=True).lower() == "download":
            return urljoin(page_url, a["href"])

    return None

# ---------------- DOWNLOAD ---------------- #

def download_file(url):
    filename = unquote(url.split("/")[-1])
    path = os.path.join(TEMP_DIR, filename)

    log.info(f"Downloading: {filename}")
    with requests.get(url, stream=True, headers=HEADERS) as r:
        r.raise_for_status()
        with open(path, "wb") as f:
            for chunk in r.iter_content(chunk_size=1024 * 1024):
                if chunk:
                    f.write(chunk)

    return path

# ---------------- MAIN LOOP ---------------- #

def main():
    app = Client(SESSION, api_id=API_ID, api_hash=API_HASH)
    app.start()

    notify_admin(app, "🚀 Downloader started")

    downloaded = load_downloaded()

    while True:
        try:
            episodes = get_episode_pages()
            random.shuffle(episodes)

            target = None
            for ep in episodes:
                if ep not in downloaded:
                    target = ep
                    break

            if not target:
                log.info("No new episodes found. Sleeping...")
                time.sleep(3600)
                continue

            log.info(f"Selected episode: {target}")
            notify_admin(app, f"⬇️ Download started\n{target}")

            dl_link = get_download_link(target)
            if not dl_link:
                raise Exception("Download link not found")

            file_path = download_file(dl_link)

            log.info("Uploading to Telegram")
            notify_admin(app, "⬆️ Upload started")

            app.send_document(
                chat_id=CHANNEL_ID,
                document=file_path
            )

            os.remove(file_path)
            save_downloaded(target)

            log.info("Completed successfully")
            notify_admin(app, "✅ Upload completed")

            time.sleep(10)

        except Exception as e:
            log.error(f"ERROR: {e}")
            notify_admin(app, f"❌ Error occurred:\n{e}")
            time.sleep(300)

# ---------------- START ---------------- #

if __name__ == "__main__":
    os.makedirs(TEMP_DIR, exist_ok=True)
    main()
