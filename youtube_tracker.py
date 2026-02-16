import requests
from bs4 import BeautifulSoup
import os

# --- CONFIGURATION ---
TOKEN = os.getenv("TELEGRAM_TOKEN")
CHAT_ID = os.getenv("TELEGRAM_CHAT_ID")
DB_FILE = "last_videos.txt"

# Liste des chaînes à surveiller
CHANNELS = {
    "MrBeast": "UCX6OQ3DkcsbYNE6H8uQQuVA",
    "Michou": "UCoS6nZREK37H2WvY3i_S9Kg",
    "Inoxtag": "UCL9aTJKoOo_jJH_mO_PrpBQ",
    "Furious Jumper": "UC_mN0mN69p_C_SIsyInMh8A",
    "Anime": "UC6pWAs_uP3fA8OunU6A8R8g" # Exemple (ID à vérifier selon la chaîne précise)
}

def load_last_ids():
    """Charge les derniers IDs de vidéos envoyés depuis le fichier"""
    last_ids = {}
    if os.path.exists(DB_FILE):
        with open(DB_FILE, "r") as f:
            for line in f:
                if ":" in line:
                    name, vid_id = line.strip().split(":", 1)
                    last_ids[name] = vid_id
    return last_ids

def save_last_ids(last_ids):
    """Sauvegarde les IDs dans le fichier"""
    with open(DB_FILE, "w") as f:
        for name, vid_id in last_ids.items():
            f.write(f"{name}:{vid_id}\n")

def check_youtube():
    last_ids = load_last_ids()
    new_data_found = False

    for name, channel_id in CHANNELS.items():
        url_rss = f"https://www.youtube.com/feeds/videos.xml?channel_id={channel_id}"
        try:
            res = requests.get(url_rss, timeout=10)
            soup = BeautifulSoup(res.content, 'xml')
            latest_entry = soup.find('entry')
            
            if not latest_entry: continue

            video_id = latest_entry.find('yt:videoId').text
            video_title = latest_entry.find('title').text
            video_url = latest_entry.find('link')['href']

            # Si l'ID est différent de celui enregistré
            if last_ids.get(name) != video_id:
                print(f"✨ Nouvelle vidéo pour {name} !")
                message = f"🚨 **NOUVEAU CHEZ {name.upper()}**\n\n🎬 {video_title}\n🔗 [Regarder la vidéo]({video_url})"
                send_to_telegram(message)
                last_ids[name] = video_id
                new_data_found = True
        except Exception as e:
            print(f"Erreur pour {name}: {e}")

    if new_data_found:
        save_last_ids(last_ids)

def send_to_telegram(text):
    url = f"https://api.telegram.org/bot{TOKEN}/sendMessage"
    payload = {
        "chat_id": CHAT_ID, 
        "text": text, 
        "parse_mode": "Markdown",
        "disable_web_page_preview": False
    }
    requests.post(url, data=payload)

if __name__ == "__main__":
    check_youtube()
          
