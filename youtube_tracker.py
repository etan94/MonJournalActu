import requests
import os
import sys
from bs4 import BeautifulSoup

# --- CONFIGURATION ---
DB_FILE = "last_videos.txt"
CHANNELS = {
    "MrBeast": "UCX6OQk8i3LsXBdMGtJK-JuQ",
    "Michou": "UCoS6nZREK37H2WvY3i_S9Kg",
    "Inoxtag": "UCL9aTJKoOo_jJH_mO_PrpBQ",
    "Furious Jumper": "UC_yP2DpIgs5Y1uWC0T03Chw",
    "Crunchyroll FR": "UCNc2aXvJ9bN6G7xG0z0x7yA"
}

TOKEN = os.getenv("TELEGRAM_TOKEN")
CHAT_ID = os.getenv("TELEGRAM_CHAT_ID")

def get_last_ids():
    if not os.path.exists(DB_FILE): return {}
    try:
        with open(DB_FILE, "r") as f:
            return dict(line.strip().split(":", 1) for line in f if ":" in line)
    except: return {}

def save_ids(data):
    with open(DB_FILE, "w") as f:
        for k, v in data.items(): f.write(f"{k}:{v}\n")

def send_telegram(msg):
    if not TOKEN or not CHAT_ID: return
    requests.post(f"https://api.telegram.org/bot{TOKEN}/sendMessage", data={
        "chat_id": CHAT_ID, "text": msg, "parse_mode": "Markdown", "disable_web_page_preview": False
    })

def check_videos():
    print("--- Scan ---")
    last_ids = get_last_ids()
    updated = False

    for name, channel_id in CHANNELS.items():
        try:
            url = f"https://www.youtube.com/feeds/videos.xml?channel_id={channel_id}"
            res = requests.get(url, timeout=10)
            if res.status_code != 200: continue
            
            soup = BeautifulSoup(res.content, "xml")
            entry = soup.find("entry")
            if not entry: continue

            vid_id = entry.find("videoId").text
            title = entry.find("title").text
            link = entry.find("link")["href"]

            if last_ids.get(name) != vid_id:
                print(f"Nouveau: {title}")
                send_telegram(f"🚨 **{name.upper()}**\n\n🎬 {title}\n🔗 [Voir]({link})")
                last_ids[name] = vid_id
                updated = True
        except Exception as e:
            print(f"Erreur {name}: {e}")

    if updated:
        save_ids(last_ids)
        print("Sauvegarde.")
    else:
        print("Rien.")

if __name__ == "__main__":
    check_videos()
