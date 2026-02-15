import requests
from bs4 import BeautifulSoup
from datetime import datetime
import os

# --- CONFIGURATION (GitHub Secrets) ---
TOKEN = os.getenv("TELEGRAM_TOKEN")
CHAT_ID = os.getenv("TELEGRAM_CHAT_ID")

# Sources organisées par catégories
SOURCES = {
    "🌍 INTERNATIONAL": [
        "https://www.lemonde.fr/international/rss_full.xml",
        "https://www.france24.com/fr/rss"
    ],
    "💻 TECH & INNOVATION": [
        "https://www.clubic.com/feed/news.rss",
        "https://www.journaldugeek.com/feed/"
    ],
    "🔬 SCIENCES & FUTUR": [
        "https://www.sciencesetavenir.fr/rss.xml",
        "https://www.futura-sciences.com/rss/actualites.xml"
    ],
    "⚽ SPORT": [
        "https://rmcsport.bfmtv.com/rss/info-rmc-sport/",
        "https://www.lequipe.fr/rss/actu_rss.xml"
    ]
}

def scraper_actus():
    print("⏳ Préparation du journal...")
    headers = {'User-Agent': 'Mozilla/5.0'}
    date_str = datetime.now().strftime("%d %B %Y").upper()
    
    # Construction du message (Design Harmonieux)
    message = (
        "╔════════════════════╗\n"
        f"  📰  *MON JOURNAL DU JOUR* \n"
        f"  _Le {date_str}_ \n"
        "╚════════════════════╝\n\n"
    )

    for categorie, urls in SOURCES.items():
        message += f"*{categorie}*\n"
        message += "────────────────────\n"
        
        titres_trouves = []
        for url in urls:
            try:
                res = requests.get(url, headers=headers, timeout=10)
                # On utilise 'xml' pour lire les flux RSS proprement
                soup = BeautifulSoup(res.content, 'xml')
                items = soup.find_all('item')[:2] # 2 titres par source
                for item in items:
                    t = item.title.text.strip()
                    if t not in titres_trouves:
                        titres_trouves.append(t)
            except:
                continue
        
        if titres_trouves:
            for i, t in enumerate(titres_trouves, 1):
                message += f"*{i}.* {t}\n"
        else:
            message += "_Aucune actu disponible_\n"
        message += "\n"

    message += "______________________________\n_Bonne lecture ! ✨_"
    return message

def envoyer_telegram(texte):
    url = f"https://api.telegram.org/bot{TOKEN}/sendMessage"
    payload = {"chat_id": CHAT_ID, "text": texte, "parse_mode": "Markdown"}
    r = requests.post(url, data=payload)
    if r.status_code == 200:
        print("✨ Journal envoyé !")
    else:
        print(f"❌ Erreur Telegram : {r.text}")

if __name__ == "__main__":
    contenu = scraper_actus()
    envoyer_telegram(contenu)

  
