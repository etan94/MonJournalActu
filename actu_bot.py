import requests
from bs4 import BeautifulSoup
from datetime import datetime
import os
import re

# --- CONFIGURATION (GitHub Secrets) ---
TOKEN = os.getenv("TELEGRAM_TOKEN")
CHAT_ID = os.getenv("TELEGRAM_CHAT_ID")

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

def clean_html(text):
    """Enlève les balises HTML qui s'invitent parfois dans les descriptions"""
    clean = re.compile('<.*?>')
    return re.sub(clean, '', text)

def scraper_actus():
    print("⏳ Génération du journal avec résumés...")
    headers = {'User-Agent': 'Mozilla/5.0'}
    date_str = datetime.now().strftime("%d %B %Y").upper()
    
    message = (
        "╔════════════════════╗\n"
        f"  📰  *MON JOURNAL DU JOUR* \n"
        f"  _Le {date_str}_ \n"
        "╚════════════════════╝\n\n"
    )

    for categorie, urls in SOURCES.items():
        message += f"📦 *{categorie}*\n"
        message += "━━━━━━━━━━━━━━━━━━━━\n"
        
        count = 0
        for url in urls:
            try:
                res = requests.get(url, headers=headers, timeout=10)
                soup = BeautifulSoup(res.content, 'xml')
                items = soup.find_all('item')[:2] # 2 articles par source
                
                for item in items:
                    titre = item.title.text.strip()
                    lien = item.link.text.strip()
                    # On récupère la description et on la nettoie
                    desc = item.description.text.strip() if item.description else ""
                    desc = clean_html(desc)[:120] + "..." # On coupe pour pas que ce soit trop long
                    
                    count += 1
                    # Formatage : Titre en gras (cliquable) + description en italique
                    message += f"📍 *[{titre}]({lien})*\n"
                    message += f"└ _{desc}_\n\n"
            except:
                continue
        
        if count == 0:
            message += "_Aucune actu disponible_\n\n"

    message += "────────────────────\n_✨ Bonne lecture ! (Liens cliquables)_"
    return message

def envoyer_telegram(texte):
    url = f"https://api.telegram.org/bot{TOKEN}/sendMessage"
    payload = {
        "chat_id": CHAT_ID, 
        "text": texte, 
        "parse_mode": "Markdown",
        "disable_web_page_preview": True 
    }
    r = requests.post(url, data=payload)
    if r.status_code == 200:
        print("✨ Journal complet envoyé !")
    else:
        # Si le message est trop long, on essaie de l'envoyer par morceaux
        print(f"❌ Erreur : {r.text}")

if __name__ == "__main__":
    contenu = scraper_actus()
    envoyer_telegram(contenu)
