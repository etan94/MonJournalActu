import requests
from bs4 import BeautifulSoup
from datetime import datetime

# --- CONFIGURATION ---
import os
TOKEN = os.getenv("TELEGRAM_TOKEN")
CHAT_ID = os.getenv("TELEGRAM_CHAT_ID") 

SOURCES = {
    # --- CONFIGURATION FRANCOPHONE ---
CATEGORIES = {
    "🌍 INTERNATIONAL": [
        "https://www.lemonde.fr/international/rss_full.xml",
        "https://www.france24.com/fr/rss"
    ],
    "💻 TECH & INNOVATION": [
        "https://www.clubic.com/feed/news.rss",
        "https://www.journaldugeek.com/feed/"
    ],
    "🔬 SCIENCES & ENVIRONNEMENT": [
        "https://www.sciencesetavenir.fr/rss.xml",
        "https://www.futura-sciences.com/rss/actualites.xml"
    ],
    "⚽ SPORT": [
        "https://rmcsport.bfmtv.com/rss/info-rmc-sport/",
        "https://www.lequipe.fr/rss/actu_rss.xml"
    ]
}

def formater_message(data):
    """Crée une mise en page élégante et aérée"""
    date_str = datetime.now().strftime("%d %B %Y").upper()
    
    # En-tête du journal
    header = (
        "╔════════════════════╗\n"
        f"  📰  *MON JOURNAL DU JOUR* \n"
        f"  _Le {date_str}_ \n"
        "╚════════════════════╝\n\n"
    )
    
    corps = ""
    for nom, infos in data.items():
        corps += f"{infos['emoji']}  *__ {nom} __*\n" # Titre de la source souligné
        for i, titre in enumerate(infos['titres'], 1):
            corps += f"*{i}.* {titre}\n" # Numérotation en gras
        corps += "\n" # Espace entre les blocs
        
    footer = "────────────────────\n_Bonne lecture ! ✨_"
    
    return header + corps + footer

def scraper_et_envoyer():
    print("⏳ Préparation de ton journal harmonieux...")
    data_finale = {}
    headers = {'User-Agent': 'Mozilla/5.0'}

    for nom, config in SOURCES.items():
        try:
            res = requests.get(config['url'], headers=headers, timeout=10)
            soup = BeautifulSoup(res.text, 'html.parser')
            # On récupère les 3 meilleurs titres
            titres = [t.get_text(strip=True) for t in soup.select(config['selector'])[:3]]
            data_finale[nom] = {"titres": titres, "emoji": config['emoji']}
        except:
            data_finale[nom] = {"titres": ["⚠️ Erreur de connexion"], "emoji": "❌"}

    # Génération du message stylé
    message_propre = formater_message(data_finale)
    
    # Envoi via l'API Telegram
    url = f"https://api.telegram.org/bot{TOKEN}/sendMessage"
    payload = {
        "chat_id": CHAT_ID,
        "text": message_propre,
        "parse_mode": "Markdown" # Utilisation de Markdown classique pour la stabilité
    }
    
    response = requests.post(url, data=payload)
    if response.status_code == 200:
        print("✨ Journal envoyé avec succès !")
    else:
        print(f"❌ Erreur : {response.text}")

if __name__ == "__main__":
    scraper_et_envoyer()
  
