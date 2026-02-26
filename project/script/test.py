import requests
from bs4 import BeautifulSoup

# URL de l'équipe (Saison 2025/2026)
url = ["https://www.transfermarkt.com/yongin-fc/spielplan/verein/135830/saison_id/2025"]

headers = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/114.0.0.0 Safari/537.36"
}

def connection(url):
    response = requests.get(url, headers=headers)
    if response.status_code != 200:
        print(f"Erreur : {response.status_code}")
        return None
    return response

def score(data):
            soup = BeautifulSoup(data.content, 'html.parser')
        
            stats_table = soup.find('table', class_='renditestatistik')
            
            if not stats_table:
                stats_table = soup.find('div', {'class': 'responsive-table'}).find('table')

            if stats_table:
                    rows = stats_table.find('tfoot').find_all('tr')

                    print(f"{'COMPÉTITION (Type)':<40} | {'M':<3} | {'V':<3} | {'N':<3} | {'D':<3} | {'BUTS':<6}")
                    print("-" * 75)
                    

                        
                    for row in rows:
                            cols = row.find_all('td')
                            
                            if len(cols) >= 7:
                                # Si c'est juste le nom de la comp répété, on ne l'affiche pas deux fois
                                
                                matches = cols[1].text.strip()
                                wins    = cols[2].text.strip()
                                draws   = cols[3].text.strip()
                                losses  = cols[4].text.strip()
                                goals   = cols[6].text.strip()

                                # On évite d'afficher le bilan total "Overall balance"
                                print(f" {'BILAN':<40} | {matches:<3} | {wins:<3} | {draws:<3} | {losses:<3} | {goals:<6}")


def scores(data):
    soup = BeautifulSoup(data.content, 'html.parser')
    
    # 1. On récupère tous les blocs de compétition
    titres_h2 = soup.find_all('h2', class_='content-box-headline--inverted')
    
    if not titres_h2:
        print("Erreur : Aucun titre avec la classe inversée n'a été trouvé.")
        return

    # 2. On boucle sur chaque compétition trouvée
    for index, titre in enumerate(titres_h2, 1):
        
        # --- Extraction des infos de la compétition ---
        nom_competition = titre.get_text(strip=True)
        img_tag = titre.find('img')
        url_logo = img_tag['src'] if img_tag and 'src' in img_tag.attrs else "Pas de logo"

        # Affichage de l'en-tête de la compétition
        print(f"\n{'='*60}")
        print(f"🏆 COMPÉTITION : {nom_competition}")
        print(f"🔗 LOGO : {url_logo}")
        print(f"{'='*60}")
        
        # --- Recherche du tableau correspondant ---
        stats_table = titre.find_next('table')
        
        if stats_table:
            tbody = stats_table.find('tbody')
            
            if tbody: 
                rows = tbody.find_all('tr')
                for row in rows:
                    cols = row.find_all('td')
                    
                    # On s'assure qu'il y a au moins 10 colonnes (index 0 à 9)
                    if len(cols) >= 10:
                        matches = cols[0].text.strip()
                        date    = cols[1].text.strip()
                        time    = cols[2].text.strip()
                        Venu    = cols[3].text.strip()
                        rang    = cols[4].text.strip()
                        opp= cols[5].text.strip()#rien comme value
                        sys= cols[6].text.strip()
                        sup= cols[7].text.strip()
                        jsp= cols[8].text.strip()
                        
                        # --- Traitement de la colonne Adversaire (index 9) ---
                        cellule_adv = cols[9]
                        adv_texte = cellule_adv.text.strip()
                        
                        lien_adv = cellule_adv.find('a')
                        adv_href = lien_adv['href'] if lien_adv and 'href' in lien_adv.attrs else "Pas de lien"

                        # Petite sécurité : si la ligne contient vraiment des données (ex: une date)
                        if date:
                            print(f"{matches:<3} | {date:<10} | {time:<5} | {Venu:<3} | {rang:<3} | Adv: {opp:<3} | sys: {sys:<3} | supporter: {sup:<3} |jsp: {jsp:<3}|score: {adv_texte:<3} | Lien: {adv_href}")
            else:
                print("Pas de données (tbody) trouvées dans ce tableau.")
        else:
            print("Pas de tableau trouvé après ce titre.")
                  

def get_competition_stats():
    
    for i in url:
        data = connection(i)
        if data:
            scores(data)
            prefixe = url[0].rsplit('/', 1)[0]
            year=url[0].rsplit('/', 1)[1]
            year=int(year)
            year_=year-1
            nouvelle_url = f"{prefixe}/{year_}"
            while year-year_<=1:
                data_udp = connection(nouvelle_url)
                if data_udp:
                    scores(data_udp)
                year_-=1
                nouvelle_url = f"{prefixe}/{year_}"
            

if __name__ == "__main__":
    get_competition_stats()