import requests
import os
import sys
import time
from bs4 import BeautifulSoup

# --- CONFIGURATION ---
DB_FILE = "last_videos.txt"
# Liste de tes chaînes favorites
CHANNELS = {
    "MrBeast": "UCX6OQk8i3LsXBdMGtJK-JuQ",
    "Michou": "UCoS6nZREK37H2WvY3i_S9Kg",
    "Inoxtag": "UCL9aTJKoOo_jJH_mO_PrpBQ",
    "Furious Jumper": "UC_yP2DpIgs5Y1uWC0T03Chw",
    "Crunchyroll FR": "UCNc2aXvJ9bN6G7xG0z0x7yA"
}

# --- CHARGEMENT DES SECRETS ---
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
    print("--- Démarrage du Scan ---")
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
        print("Sauvegarde effectuée.")
    else:
        print("Rien de nouveau.")

if __name__ == "__main__":
    check_videos()
    })

def check_videos():
    print("--- Démarrage du Scan ---")
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
        print("Sauvegarde effectuée.")
    else:
        print("Rien de nouveau.")

if __name__ == "__main__":
    check_videos()
                    parts = line.strip().split(":", 1)
                    if len(parts) == 2:
                        data[parts[0]] = parts[1]
            return data
    except Exception as e:
        print(f"⚠️ Erreur lecture fichier: {e}")
        return {}

def save_ids(data):
    """Sauvegarde les IDs dans le fichier."""
    try:
        with open(DB_FILE, "w") as f:
            for name, vid_id in data.items():
                f.write(f"{name}:{vid_id}\n")
    except Exception as e:
        print(f"⚠️ Erreur sauvegarde: {e}")

def send_telegram(msg):
    if not TOKEN or not CHAT_ID:
        print("❌ Pas de token Telegram configuré. Message non envoyé.")
        return
    url = f"https://api.telegram.org/bot{TOKEN}/sendMessage"
    try:
        requests.post(url, data={
            "chat_id": CHAT_ID,
            "text": msg,
            "parse_mode": "Markdown",
            "disable_web_page_preview": False
        })
    except Exception as e:
        print(f"❌ Erreur envoi Telegram: {e}")

def check_videos():
    print(f"🔍 Démarrage du scan ({time.strftime('%H:%M:%S')})...")
    last_ids = get_last_ids()
    updated = False

    for name, channel_id in CHANNELS.items():
        try:
            # On utilise l'agent utilisateur 'Googlebot' pour éviter les blocages
            headers = {"User-Agent": "Mozilla/5.0 (compatible; Googlebot/2.1; +http://www.google.com/bot.html)"}
            url = f"https://www.youtube.com/feeds/videos.xml?channel_id={channel_id}"
            
            resp = requests.get(url, headers=headers, timeout=10)
            if resp.status_code != 200:
                print(f"🔸 {name}: Erreur HTTP {resp.status_code}")
                continue

            soup = BeautifulSoup(resp.content, "xml")
            entry = soup.find("entry")

            if entry:
                vid_id = entry.find("videoId").text
                title = entry.find("title").text
                link = entry.find("link")["href"]

                # Si c'est une nouvelle vidéo
                if last_ids.get(name) != vid_id:
                    print(f"🚀 NOUVEAU: {title}")
                    msg = f"🚨 **{name.upper()} A POSTÉ !**\n\n🎬 {title}\n🔗 [Voir la vidéo]({link})"
                    send_telegram(msg)
                    
                    last_ids[name] = vid_id
                    updated = True
                else:
                    print(f"✅ {name}: Rien de neuf")
            else:
                print(f"🔸 {name}: Pas de contenu trouvé")

        except Exception as e:
            print(f"❌ Erreur sur {name}: {e}")

    if updated:
        save_ids(last_ids)
        print("💾 Base de données mise à jour.")
    else:
        print("zzz Aucune mise à jour nécessaire.")

if __name__ == "__main__":
    check_videos()
