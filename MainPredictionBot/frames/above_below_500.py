from urllib.request import urlopen as ureq
from bs4 import BeautifulSoup as soup
import pandas as pd
import requests
import logging

logger = logging.getLogger(__name__)
logger.setLevel(logging.INFO)

formatter = logging.Formatter('%(asctime)s: %(message)s')

file_handler = logging.FileHandler(r'C:\Users\Danie\Desktop\tests\EneBeA\NBA_prediction_bot\logs\ab_500_update.log')
file_handler.setFormatter(formatter)

logger.addHandler(file_handler)


class AboveBelow500(object):
    def __init__(self):
        self.url_ab5 = "https://www.espn.co.uk/nba/table/_/group/league/view/expanded"
        self.table_teams_CSS = "tbody tr td:nth-child(1) div:nth-child(1) span:nth-child(3) a"
        self.table_row_CSS = "table:nth-child(1) > tbody:nth-child(6) > tr > td > span"

    def team_sts_loop(self,teamstats_css):
        teamstats = []
        team_data = []
        for i in teamstats_css:
            team_data.append(i.text)
            if len(team_data) == 9:
                data = team_data[-3:]
                data = data[:2]
                data = [j.split('-') for j in data]
                data  = [val for sublist in data for val in sublist]
                
                teamstats.append(data)
                team_data = []
        return teamstats

    def team_nm_loop(self,teamnames_css):
        teamnames = []
        for i in teamnames_css:
            data = i.text
            data = data.replace('LA Clippers', 'Los Angeles Clippers')
            teamnames.append(data)
        return teamnames

    def parse_request_ab5(self):
        r = requests.Session().get(self.url_ab5)
        page_soup = soup(r.text,"lxml")

        teamnames_css = page_soup.select(self.table_teams_CSS)
        teamstats_css = page_soup.select(self.table_row_CSS)
        df = pd.DataFrame(self.team_sts_loop(teamstats_css),columns=None)
        df.insert(0,'Team',self.team_nm_loop(teamnames_css))

        a = df.Team.values.astype(str).argsort()
        a = pd.DataFrame(df.values[a], df.index[a], df.columns)    
        a['vsaf'] = a[0].astype(float)/(a[0].astype(float) + a[1].astype(float))
        a['vsbf'] = a[2].astype(float)/(a[2].astype(float) + a[3].astype(float))
        a['vsaf'] = a['vsaf'].astype(float)
        a['vsbf'] = a['vsbf'].astype(float)
            
        a = a.drop(columns=[0,1,2,3])
        a.reset_index(drop=True, inplace=True)

        a.to_csv(fr'C:\Users\Danie\Desktop\tests\EneBeA\NBA_prediction_bot\data\A5B5.csv',index=False)
        logger.info(f'{__class__.__name__} UPDATED!')

        self.above_below_500 = a
        return a

# ab5 = AboveBelow500()
# print(ab5.parse_request_ab5())