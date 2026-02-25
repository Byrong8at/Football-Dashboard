import requests
from bs4 import BeautifulSoup
import pandas as pd 
import os
import time

headers = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/114.0.0.0 Safari/537.36"
}

def connection(url):
    try:
        response = requests.get(url, headers=headers)
        if response.status_code != 200:
            print(f"Error : {response.status_code}")
            return None
        return response
    except Exception as e:
        print(f"Connection error: {e}")
        return None
    
def Get_value(soup,types,classe):
    data = soup.find(types, class_=classe)
    if data == None:
        return None
    return data

def Get_Rows(data):
    """
    data: HTML content

    return:
    - Link: List of href player
    - icon: Icon of the team
    """
    link=[]
    soup = BeautifulSoup(data.content, 'html.parser')
    table = Get_value(soup, 'table', 'items')
    icon = soup.find("div", class_="data-header__profile-container").find("img")["src"]

    if not table:
        return

    rows = table.find('tbody').find_all('tr', recursive=False)

    for row in rows:
        name_tag = row.find('td', class_='hauptlink')
        if name_tag and name_tag.a:
            link.append(name_tag.a['href'])

    return link, icon

def Get_Detail_Goal(data):
    Detail=[]
    soup = BeautifulSoup(data.content, 'html.parser')
    
        
    stats_table = soup.find('table', class_='renditestatistik')
    if not stats_table:
        stats_table = soup.find('div', {'class': 'responsive-table'}).find('table')

    if stats_table:
        try:
            rows = stats_table.find('tfoot').find_all('tr')                
            for row in rows:
                cols = row.find_all('td')                        
                if len(cols) >= 6:
                    score_raw = cols[6].text.strip()
                    goals_for, goals_against = score_raw.split(":")
                    Detail.append({"matches" : cols[1].text.strip(),
                                    "wins" : cols[2].text.strip(),
                                    "draws" : cols[3].text.strip(),
                                    "losses" : cols[4].text.strip(),
                                    "Goals_for" :goals_for,
                                    "Goal_Again" : goals_against})
        except:
            Detail.append({"matches" :0,
                                    "wins" : 0,
                                    "draws" : 0,
                                    "losses" : 0,
                                    "Goals_for" :0,
                                    "Goal_Again" : 0})
    return Detail


def Get_Team(clubs):
    """
    Get Team from request from club information
    List:
    - Club Name: Name
    - Link: Link Club Transfermarkt
    - League: Name of the League

    Club_info: List
    """
    print("Fetch Club data")
    Club_info = []
    for club in clubs:
        url = club.get("Link")
        name = club.get("Club Name")
        league = club.get("League")

        if url:
            link_url = f"https://www.transfermarkt.com{url}"
            data = connection(link_url)
            #two file one with club one with player
            if data:
                    link,icon=Get_Rows(data)
                    link_url = link_url.replace("/startseite/", "/spielplan/")
                    data_club = connection(link_url)
                    if data_club:
                        detail=Get_Detail_Goal(data_club)

                    Club_info.append({
                            "Club": name,
                            "Team_Icon": icon,
                            "League": league,
                            "Stat":detail,
                            "Player_Link": link
                        })
                    
        time.sleep(5)

    # Creation of the dataframe
    if Club_info:
        df = pd.DataFrame(Club_info)
        base_dir = os.path.dirname(os.path.abspath(__file__))
        data_dir = os.path.join(base_dir, '..', 'data')

        if not os.path.exists(data_dir):
            os.makedirs(data_dir)

        filename = os.path.join(data_dir, 'Clubs.csv')
        df.to_csv(filename, index=False)

        print(f"\nSuccess! Data saved to {filename}")
    else:
        print("No data found.")

    return Club_info