import os
from script.League_scrap import Get_League
from script.Team_scrap import Get_Team

club_list=Get_League()
annees_a_extraire = [2021,2022,2023,2024,2025]
Get_Team(club_list, years=annees_a_extraire)