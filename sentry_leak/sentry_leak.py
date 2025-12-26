# --------------- Dépendances
from __future__ import annotations
from bs4 import BeautifulSoup
import requests
import argparse
import json
import subprocess
import re
import shlex


# --------------- Recherche des éléments importants.
""""
url = "https://bonjourlafuite.eu.org"
response = requests.get(url)
response.encoding = 'utf-8'
if response.status_code == 200:
    print(f"Status de la requête : {response.status_code} -OK")
    soup = BeautifulSoup(response.text, 'html.parser')
else:
    print(f"Status de la requête : {response.status_code} -FAIL")

# Fuite    
for h in soup.find_all('h2'):
    print(h.text)
    
# Via 
# Plus tard il faudras que je récupère aussi les h3 lorsqu'ils existent et que he les associes aux Fuites

# Date
for s in soup.find_all('span'):
    print(s.text)
    
# Source
for a in soup.find_all('a', target='_blank', href=True):
    print(f"{url}/{a['href']}" if a['href'].startswith('img/') else a['href'])
    
# Infos
for div in soup.find_all('div', class_='timeline-description'):
    Infos =[]
    for li in div.find_all('li'):
        if li.find('a') is None:  # Pas de source dedans
            Infos.append(li.text)
    print(Infos)
"""

# --------------- Dictionnaire si besoin

'''
# Dico avec toutes les fuites
fuites ={}
for h2 in soup.find_all('h2'):
    nom = h2.text.strip()
    fuites[nom] = {
        'Via': '',
        'Date': '',
        'Infos': [],
        'Source':''
    }

print("----------------")
print(fuites.keys())

'''

# --------------- check_response

def check_response(url: str) -> tuple[bool, BeautifulSoup | None]:
    '''Vérifie l'état de la requête'''
    response = requests.get(url)
    response.encoding = 'utf-8'
    if response.status_code == 200:
        print(f"Status de la requête : {response.status_code} -OK")
        soup = BeautifulSoup(response.text, 'html.parser')
        return True, soup
    else:
        print(f"Status de la requête : {response.status_code} -FAIL")
        return False, None
        
# --------------- check_mail

def is_valid_email(email: str) -> bool:
    """Valide strictement une adresse email"""
    pattern = r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$'
    return bool(re.match(pattern, email)) and len(email) < 254


# --------------- whats_new
def whats_new(soup: BeautifulSoup) -> tuple[bool, list[dict]]:
    """Extrait Noms, Dates ET Infos des fuites"""
    try:
        with open("fuites.json", "r", encoding="utf-8") as f:
            content = f.read().strip()
            if content:
                known = json.loads(content)
            else:
                known = []
    except (FileNotFoundError, json.JSONDecodeError):
        known = []

    known_keys = {(item["Nom"], item["Date"]) for item in known}

    fuites_page: list[dict] = []
    h2_list = soup.find_all("h2")
    span_list = soup.find_all("span")
    div_list = soup.find_all("div", class_="timeline-description")

    for i, (h, s) in enumerate(zip(h2_list, span_list)):
        nom = h.text.strip()
        date = s.text.strip()
        
        infos = []
        if i < len(div_list):
            div = div_list[i]
            for li in div.find_all('li'):
                if li.find('a') is None:
                    infos.append(li.text.strip())
        
        fuites_page.append({
            "Nom": nom, 
            "Date": date,
            "Infos": infos 
        })

    # 3. Trouver les nouvelles
    nouvelles: list[dict] = []
    for fuite in fuites_page:
        key = (fuite["Nom"], fuite["Date"])
        if key in known_keys:
            break
        nouvelles.append(fuite)

    return bool(nouvelles), nouvelles



# --------------- store_json

def store_json(news: list[dict]) -> None:
    """
    Met à jour fuites.json avec les 6 dernières fuites connues.
    Ajoute les nouvelles au début, garde max 6.
    """
    try:
        with open("fuites.json", "r", encoding="utf-8") as f:
            content = f.read().strip()
            if content:
                known = json.loads(content)
            else:
                known = []
    except (FileNotFoundError, json.JSONDecodeError):
        known = []

    all_fuites = news + known
    
    latest_6 = all_fuites[:6]
    
    with open("fuites.json", "w", encoding="utf-8") as f:
        json.dump(latest_6, f, ensure_ascii=False, indent=2)
    
    print(f"JSON mis à jour: {len(latest_6)} fuites stockées")


# --------------- safe_notifier

def safe_notifier(fuite_nom: str, fuite_date: str) -> bool:
    """Appel sécurisé du notifier.py"""
    NOTIFIER_PATH = "/PATH/Notifier/notifier.py"

    nom_clean = re.sub(r'[;&|`$(){}\\[\\]\\\\"]', '', fuite_nom)[:100]
    date_clean = re.sub(r'[;&|`$(){}\\[\\]\\\\"]', '', fuite_date)[:50]
    
    cmd = [NOTIFIER_PATH, 'LeakSentry', '-s', nom_clean, '-m', date_clean]
    
    try:
        result = subprocess.run(cmd, check=True, timeout=30, capture_output=True, text=True)
        print(f"Notifier OK: {nom_clean}")
        return True
    except (subprocess.CalledProcessError, subprocess.TimeoutExpired) as e:
        print(f"Notifier échoué: {e}")
        return False
        

# --------------- safe_mailer

def safe_mailer(to_email: str, fuite: dict) -> bool:
    """Appel sécurisé du mailer.py avec INFOS détaillées"""
    MAILER_PATH = "/PATH/Mailer/mailer.py"
    
    nom_clean = re.sub(r'[;&|`$(){}\\[\\]\\\\"]', '', fuite["Nom"])[:100]
    date_clean = re.sub(r'[;&|`$(){}\\[\\]\\\\"]', '', fuite["Date"])[:50]
    
    infos_text = "\n".join(fuite["Infos"][:5]) if fuite["Infos"] else "Aucune info disponible"
    infos_clean = re.sub(r'[;&|`$(){}\\[\\]\\\\"]', '', infos_text)[:500]
    
    subject = f"[LeakSentry] Nouvelle fuite : {nom_clean}"
    body = f"""Nouvelle fuite détectée le {date_clean}

INFOS :
{infos_clean}

Vérifiez : https://bonjourlafuite.eu.org"""
    
    cmd = [MAILER_PATH, to_email, '-s', subject, '-b', body]
    
    try:
        result = subprocess.run(cmd, check=True, timeout=60, capture_output=True, text=True)
        print(f"Mail envoyé: {nom_clean}")
        return True
    except (subprocess.CalledProcessError, subprocess.TimeoutExpired) as e:
        print(f"Mail échoué: {e}")
        return False





# --------------- sentry_leak

def sentry_leak(to_email: str | None, url: str) -> None:
    ok, soup = check_response(url)
    if not ok:
        print("Erreur requête")
        return
    
    is_new, news = whats_new(soup)
    if is_new:
        print(f"Nouvelles fuites trouvées: {len(news)}")
        store_json(news)
        
        for fuite in news:
            # Toujours notifier
            safe_notifier(fuite["Nom"], fuite["Date"])
            
            # Email SEULEMENT si --to fourni
            if to_email:
                safe_mailer(to_email, fuite)
    else:
        print("Rien de nouveau !")


# --------------- Main

def main() -> int:
    parser = argparse.ArgumentParser(description="Alerteur via BonjourLaFuite")
    parser.add_argument("--to", help="Adresse email à alerter")
    args = parser.parse_args()
    
    email = args.to if args.to and is_valid_email(args.to) else None
    
    url = "https://bonjourlafuite.eu.org"
    sentry_leak(email, url)
    return 0


if __name__ == '__main__':
    main()

