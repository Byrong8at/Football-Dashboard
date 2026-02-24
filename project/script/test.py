import requests
from bs4 import BeautifulSoup

# URL from the league
url = [
    "https://www.transfermarkt.com/k-league-1/startseite/wettbewerb/RSK1"
]

# Transfermarkt bloque les bots par défaut. Nous avons besoin d'un faux User-Agent pour simuler un vrai navigateur.
headers = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/114.0.0.0 Safari/537.36"
}

def connection(url):
    response = requests.get(url, headers=headers)
    
    if response.status_code != 200:
        print(f"Error : {response.status_code}")
        return None
    return response

def Get_value(soup,types,classe):
    data = soup.find(types, class_=classe)
    if data == None:
        return None
    return data

def Get_Clubs():
    global url
    clubs = {}
    for i in url:
        data = connection(i)
        if data != None:
            soup = BeautifulSoup(data.content, 'html.parser')
            table = Get_value(soup,'table','items')
            
            league=Get_value(soup,'h1','data-header__headline-wrapper')
            print(league.text.strip())
            if table:
                rows = table.find('tbody').find_all('tr', recursive=False)
                
                for row in rows:
                    # Extraire le nom du club (situé dans un lien à l'intérieur de td.hauptlink)
                    name_tag = row.find('td', class_='hauptlink')
                    if name_tag and name_tag.a:
                        club_name = name_tag.a.text.strip()
                        if club_name and club_name not in clubs:
                            link = name_tag.a['href']
                            clubs[club_name] = link

    # Affichage des résultats
    #for keys, values in clubs.items():
     #   print(keys, "link:", values)

    return clubs

# Pour lancer l'extraction
if __name__ == "__main__":
    Get_Clubs()