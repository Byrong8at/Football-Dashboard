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
    """
    Get statistic like Wins,matches overall the season
    """
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
                if len(cols) >= 3:
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

def Get_Matches(data):
    """
    Get information from all matchs during the season
    """
    Detail=[]
    soup = BeautifulSoup(data.content, 'html.parser')
    titres_h2 = soup.find_all('h2', class_='content-box-headline--inverted')
    
    if not titres_h2:
        print("Error: no data find.")
        return ["No data found"]
    for index, titre in enumerate(titres_h2, 1):
        
        competition = titre.get_text(strip=True)
        img_tag = titre.find('img')
        icon = img_tag['src'] if img_tag and 'src' in img_tag.attrs else "Pas de logo"
        
        stats_table = titre.find_next('table')
        
        if stats_table:
            tbody = stats_table.find('tbody')
            
            if tbody: 
                rows = tbody.find_all('tr')
                for row in rows:
                    cols = row.find_all('td')
                    
                    if len(cols) >= 9:
                        #No value for col 5
                        matches = cols[0].text.strip()
                        date    = cols[1].text.strip()
                        time    = cols[2].text.strip()
                        Venu    = cols[3].text.strip()
                        rang    = cols[4].text.strip()
                        opp= cols[6].text.strip()
                        sys= cols[7].text.strip()
                        sup= cols[8].text.strip()
                        if competition=="K League 2" or competition=="K League 1" or competition=="K league 3":
                            champ=competition
                        score_cel = cols[9]
                        score = score_cel.text.strip()
                        
                        link_score = score_cel.find('a')
                        link_href = link_score['href'] if link_score and 'href' in link_score.attrs else "Pas de lien"
                        Detail.append({
                            "Type":competition,
                            "Icon":icon,
                            "Matches": matches,
                            "Date": date,
                            "Time": time,
                            "Venue":Venu,
                            "Rank": rang,
                            "Opponent": opp,
                            "System": sys,
                            "Attendance": sup,
                            "Score":score,
                            "Match_Link" : link_href
                        })
            else:
                return ["No data"]
        else:
            return ["No data"]
    return Detail,champ     

def Csv_creation(data,chemin,year):
    """
    Creation for each CSV file 
    Data: Content from data extract
    Chemin: Path to upload files
    year: Year of the data
    """
    try:
        df = pd.DataFrame(data)
        filename = os.path.join(chemin, f'Clubs_{year+1}.csv')
        df.to_csv(filename, index=False)
        print(f"\nSuccess! Data saved to {filename}")
    except Exception as e:
        print("Error",e)

def Get_Team(clubs,years):
    """
    Get Team from request from club information
    List:
    - Club Name: Name
    - Link: Link Club Transfermarkt
    - League: Name of the League

    Club_info: List
    """
    print("Fetch Club data")
    data_by_year = {year: [] for year in years}
    
    for club in clubs:
        url = club.get("Link")
        name = club.get("Club Name")
        if url:
            link_url = f"https://www.transfermarkt.com{url}"
            data = connection(link_url)
            #two file one with club one with player
            if data:
                    print(club)
                    link,icon=Get_Rows(data)
                    prefixe = link_url.replace("/startseite/", "/spielplan/").rsplit('/', 1)[0]
                    for y in years:
                        nouvelle_url = f"{prefixe}/{y}"
                        data_udp = connection(nouvelle_url)
                        if data_udp:
                            try:
                                detail=Get_Detail_Goal(data_udp)
                                matches,champ=Get_Matches(data_udp)
                            except:
                                champ="No champ define"
                                detail=["No data"]
                                matches=["No data"]
                                print(f"no data for{club} in {y}")
                        else:
                            detail=["No data"]
                            matches=["No data"]
                            print(f"no data for{club} in {y}") 

                        data_by_year[y].append({
                                "Year": y,
                                "Club": name,
                                "Team_Icon": icon,
                                "League": champ,
                                "Stat":detail,
                                "Player_Link": link,
                                "Match_Stat":matches
                            })
                    
        time.sleep(15)

    base_dir = os.path.dirname(os.path.abspath(__file__))
    data_dir = os.path.join(base_dir, '..', 'data')

    if not os.path.exists(data_dir):
        os.makedirs(data_dir)

    for year,clubs in data_by_year.items():
        if clubs:
            Csv_creation(clubs,data_dir,year)
            
    return 200