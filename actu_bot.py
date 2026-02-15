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

def clean_text(text):
    """Nettoie le texte pour le rendu HTML de Telegram"""
    if not text: return ""
    text = re.sub('<.*?>', '', text) # Supprime les balises HTML résiduelles
    return text.replace('&', '&amp;').replace('<', '&lt;').replace('>', '&gt;').strip()

def scraper_actus():
    print("⏳ Création du journal haute définition...")
    headers = {'User-Agent': 'Mozilla/5.0'}
    date_str = datetime.now().strftime("%d %B %Y").upper()
    
    # Design de l'en-tête (Plus fin et moderne)
    message = (
        "┏" + "━" * 22 + "┓\n"
        f"  <b>✨ MON QUOTIDIEN</b>\n"
        f"  <pre>{date_str}</pre>\n"
        "┗" + "━" * 22 + "┛\n\n"
    )

    for categorie, urls in SOURCES.items():
        message += f"<b>{categorie}</b>\n"
        message += "─" * 15 + "\n"
        
        count = 0
        for url in urls:
            try:
                res = requests.get(url, headers=headers, timeout=10)
                soup = BeautifulSoup(res.content, 'xml')
                items = soup.find_all('item')[:2]
                
                for item in items:
                    titre = clean_text(item.title.text)
                    lien = item.link.text.strip()
                    desc = clean_text(item.description.text)[:110] + "..." if item.description else ""
                    
                    count += 1
                    # Mise en page aérée
                    message += f"<b>{count}. <a href='{lien}'>{titre}</a></b>\n"
                    message += f"<blockquote>{desc}</blockquote>\n"
            except:
                continue
        message += "\n"
    
    message += "<i>Bonne lecture sur ta tablette ! 👋</i>"
    return message

def envoyer_telegram(texte):
    url = f"https://api.telegram.org/bot{TOKEN}/sendMessage"
    payload = {
        "chat_id": CHAT_ID, 
        "text": texte, 
        "parse_mode": "HTML",
        "disable_web_page_preview": True 
    }
    r = requests.post(url, data=payload)
    if r.status_code == 200:
        print("✨ Journal envoyé !")
    else:
        print(f"❌ Erreur : {r.text}")

if __name__ == "__main__":
    contenu = scraper_actus()
    envoyer_telegram(contenu)
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
