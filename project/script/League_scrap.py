import requests
from bs4 import BeautifulSoup
import pandas as pd 
import os

# URL from the league
urls = ["https://www.transfermarkt.com/k-league-1/startseite/wettbewerb/RSK1",
        "https://www.transfermarkt.com/k-league-2/startseite/wettbewerb/RSK2"
        #,"https://www.transfermarkt.com/k3-league/startseite/wettbewerb/K3L",
        #"https://www.transfermarkt.com/k4-league/startseite/wettbewerb/K4L"
        ]

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

def Get_League():
    print("Fetch League data")
    clubs = [] 
    
    for url in urls:
        data = connection(url)
        if data:
            soup = BeautifulSoup(data.content, 'html.parser')
            table = Get_value(soup,'table','items')
            league=Get_value(soup,'h1','data-header__headline-wrapper').text.strip()

            if not table:
                continue
                
            rows = table.find('tbody').find_all('tr', recursive=False)
            
            for row in rows:
                name_tag = row.find('td', class_='hauptlink')
                if name_tag and name_tag.a:
                    club_name = name_tag.a.text.strip()
                    link =  name_tag.a['href']
                    clubs.append({
                            "Club Name": club_name,
                            "Link": link,
                            "League":league
                        })
                    
    return clubs
