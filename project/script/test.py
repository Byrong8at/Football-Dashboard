import requests
from bs4 import BeautifulSoup

# URL de l'équipe (Saison 2025/2026)
url = ["https://www.transfermarkt.com/jeonbuk-hyundai-motors/spielplan/verein/6502/saison_id/2025",
       "https://www.transfermarkt.com/losc-lille/spielplan/verein/1082/plus/0?saison_id=2025"]

headers = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/114.0.0.0 Safari/537.36"
}

def connection(url):
    response = requests.get(url, headers=headers)
    if response.status_code != 200:
        print(f"Erreur : {response.status_code}")
        return None
    return response

def get_competition_stats():
    for i in url:
        data = connection(i)
        if data:
            soup = BeautifulSoup(data.content, 'html.parser')
            
            # 1. On cherche le container "INFO" qui contient le bilan
            # Sur Transfermarkt, ces tableaux de bilan n'ont pas toujours d'ID unique, 
            # on cherche donc la table dans la box correspondante.
            stats_table = soup.find('table', class_='renditestatistik')
            
            if not stats_table:
                # Alternative si la classe change selon la version du site
                stats_table = soup.find('div', {'class': 'responsive-table'}).find('table')

            if stats_table:
                # On récupère toutes les lignes du corps du tableau
                    rows = stats_table.find('tfoot').find_all('tr')

                    print(f"{'COMPÉTITION (Type)':<40} | {'M':<3} | {'V':<3} | {'N':<3} | {'D':<3} | {'BUTS':<6}")
                    print("-" * 75)

                        

                    # 2. Récupérer le tbody correspondant (index i-1)
                    # Chaque tbody peut contenir une ou plusieurs lignes (Home, Away, Total)

                        
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

if __name__ == "__main__":
    get_competition_stats()