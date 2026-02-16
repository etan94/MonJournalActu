import requests
import time
import os
from bs4 import BeautifulSoup

# ==========================================
# CONFIGURATION (REMPLIS TES INFOS ICI)
# ==========================================

# Ton Token de Bot Telegram (créé via @BotFather)
TOKEN = "METS_TON_TOKEN_ICI"

# Ton ID Telegram (trouvé via @userinfobot, c'est une suite de chiffres)
CHAT_ID = "METS_TON_ID_ICI"

# Fichier de sauvegarde (ne pas toucher)
DB_FILE = "last_videos.txt"

# Liste des chaînes à surveiller (IDs vérifiés et corrigés)
CHANNELS = {
    "MrBeast": "UCX6OQ3DkcsbYNE6H8uQQuVA",
    "Michou": "UCoS6nZREK37H2WvY3i_S9Kg",
    "Inoxtag": "UCL9aTJKoOo_jJH_mO_PrpBQ",
    "Furious Jumper": "UC_yP2DpIgs5Y1uWC0T03Chw",  # ID Corrigé
    "Crunchyroll FR": "UCNc2aXvJ9bN6G7xG0z0x7yA"   # ID Anime (Crunchyroll)
}

# ==========================================
# FONCTIONS DU BOT
# ==========================================

def load_last_ids():
    """Charge la mémoire du bot (dernières vidéos vues)"""
    last_ids = {}
    if os.path.exists(DB_FILE):
        try:
            with open(DB_FILE, "r") as f:
                for line in f:
                    if ":" in line:
                        parts = line.strip().split(":", 1)
                        if len(parts) == 2:
                            last_ids[parts[0]] = parts[1]
        except Exception as e:
            print(f"Erreur lecture fichier: {e}")
    return last_ids

def save_last_ids(last_ids):
    """Sauvegarde la mémoire pour ne pas renvoyer 2 fois la même notif"""
    try:
        with open(DB_FILE, "w") as f:
            for name, vid_id in last_ids.items():
                f.write(f"{name}:{vid_id}\n")
    except Exception as e:
        print(f"Erreur sauvegarde: {e}")

def send_to_telegram(message):
    """Envoie le message sur ton téléphone via Telegram"""
    url = f"https://api.telegram.org/bot{TOKEN}/sendMessage"
    payload = {
        "chat_id": CHAT_ID, 
        "text": message, 
        "parse_mode": "Markdown",
        "disable_web_page_preview": False
    }
    try:
        requests.post(url, data=payload)
    except Exception as e:
        print(f"Erreur d'envoi Telegram: {e}")

def check_youtube():
    """Vérifie les chaînes une par une"""
    print(f"\n[{time.strftime('%H:%M:%S')}] Vérification des chaînes...")
    last_ids = load_last_ids()
    new_data_found = False

    for name, channel_id in CHANNELS.items():
        # URL RSS secrète de YouTube
        url_rss = f"https://www.youtube.com/feeds/videos.xml?channel_id={channel_id}"
        
        try:
            res = requests.get(url_rss, timeout=10)
            if res.status_code != 200:
                print(f"  ❌ Erreur accès {name} (Code {res.status_code})")
                continue

            # Analyse du XML
            soup = BeautifulSoup(res.content, 'xml')
            entry = soup.find('entry') # Trouve la dernière entrée

            if entry:
                # Récupération propre des données
                video_id = entry.find('yt:videoId').text
                video_title = entry.find('title').text
                video_url = entry.find('link')['href']

                # Comparaison avec la mémoire
                old_id = last_ids.get(name)

                if old_id != video_id:
                    print(f"  ✨ NOUVELLE VIDÉO : {name}")
                    
                    # Construction du message stylé
                    msg = (
                        f"🚨 **NOUVELLE VIDÉO : {name.upper()}**\n\n"
                        f"🎬 {video_title}\n"
                        f"🔗 [Regarder la vidéo]({video_url})"
                    )
                    
                    send_to_telegram(msg)
                    
                    # Mise à jour de la mémoire
                    last_ids[name] = video_id
                    new_data_found = True
                else:
                    print(f"  OK: {name} (Rien de nouveau)")
            else:
                print(f"  ⚠️ Pas de vidéo trouvée pour {name}")

        except Exception as e:
            print(f"  ❌ Bug sur {name}: {e}")

    # Sauvegarde seulement si on a trouvé des nouveautés
    if new_data_found:
        save_last_ids(last_ids)

# ==========================================
# LANCEMENT (BOUCLE INFINIE)
# ==========================================

if __name__ == "__main__":
    print("🤖 BOT ETAN YOUTUBE MONITOR - DÉMARRÉ")
    print("Appuie sur CTRL+C pour arrêter.")
    
    # Premier scan immédiat
    check_youtube()
    
    # Boucle infinie
    while True:
        try:
            # Pause de 600 secondes (10 minutes) pour ne pas se faire bloquer par YouTube
            temps_attente = 600 
            print(f"\n💤 Pause de {temps_attente} secondes...")
            time.sleep(temps_attente)
            check_youtube()
        except KeyboardInterrupt:
            print("\n🛑 Arrêt du bot.")
            break
        except Exception as e:
            print(f"\n❌ Erreur générale : {e}")
            time.sleep(60) # Si erreur, on attend 1 minute et on réessaie
