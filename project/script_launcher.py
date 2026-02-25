import os
from script.League_scrap import Get_League
from script.Team_scrap import Get_Team

club_list=Get_League()
Get_Team(club_list)
