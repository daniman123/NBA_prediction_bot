import requests
import pandas as pd
import numpy as np
from datetime import datetime
import logging

logger = logging.getLogger(__name__)
logger.setLevel(logging.INFO)

formatter = logging.Formatter('%(asctime)s: %(message)s')

file_handler = logging.FileHandler(r'C:\Users\Danie\Desktop\tests\EneBeA\NBA_prediction_bot\logs\schedule_update.log')
file_handler.setFormatter(formatter)

logger.addHandler(file_handler)

class GetSchedule(object):
    def __init__(self):

        self.url = f"https://cdn.nba.com/static/json/staticData/scheduleLeagueV2_51.json"
        # schedule request response
        self.response = requests.Session().get(url=self.url).json()
        
        self.sched_list = []

        self.schedule_df_headers = ['Date','Visitor/Neutral','PTS','Home/Neutral','PTS.1','Result']
    
    # > schedule_df
    def parse_response(self):
        for i,game_day in enumerate(self.response['leagueSchedule']['gameDates']):
            for i,game in enumerate(game_day['games']):
                # remove time from date
                date = game['gameDateEst'][:-10]
                # set date str as datetime obj
                datetimeobject = datetime.strptime(date,'%Y-%m-%d')
                # format datetime
                date = datetimeobject.strftime('%d-%m-%Y') 

                home_team_city = game['homeTeam']['teamCity']
                home_team_name = game['homeTeam']['teamName']
                home_team = home_team_city+' '+home_team_name
                home_team = home_team.replace('LA Clippers', 'Los Angeles Clippers')

                home_score = game['homeTeam']['score']

                away_team_city = game['awayTeam']['teamCity']
                away_team_name = game['awayTeam']['teamName']
                away_team = away_team_city+' '+away_team_name
                away_team = away_team.replace('LA Clippers', 'Los Angeles Clippers')

                away_score = game['awayTeam']['score']

                # log only regular season games
                season_start = datetime.strptime("18-10-2022","%d-%m-%Y")
                current_day = datetime.strptime(date,"%d-%m-%Y")
                if current_day >= season_start:
                    data_row = [date,away_team,away_score,home_team,home_score,'']
                    self.sched_list.append(data_row)
    # MAIN
    def schedule_df(self):
        # send request & parse response 
        self.parse_response()

        self.df = pd.DataFrame(self.sched_list,columns=self.schedule_df_headers)
        # determine game winner criteria 
        conditions = [(self.df['PTS'] > self.df['PTS.1']),(self.df['PTS'] < self.df['PTS.1'])]
        # create a list of the values we want to assign for each condition
        values = [self.df['Visitor/Neutral'], self.df['Home/Neutral']]
        # create a new column and use np.select to assign values to it using our lists as arguments
        self.df['Result'] = np.select(conditions, values)

        self.df.to_csv(r'C:\Users\Danie\Desktop\tests\EneBeA\NBA_prediction_bot\data\Schedule.csv',index=False)
        logger.info(f'{__class__.__name__} UPDATED!')
        self.first_gm_played()
        return self.df
    # > schedule_df
    def first_gm_played(self):
        self.first_hm_game = self.df.groupby('Home/Neutral').first()
        self.first_aw_game = self.df.groupby('Visitor/Neutral').first()

        self.first_hm_game['Date_aw'] = self.first_aw_game['Date']
        self.first_hm_game['first_game'] = np.where(self.first_hm_game['Date_aw'] < self.first_hm_game['Date'], self.first_hm_game['Date_aw'], self.first_hm_game['Date'])
        
        today = (datetime.today()).strftime('%d-%m-%Y')
        last_first_game = self.first_hm_game['first_game'].max()
        condition = last_first_game < today
        if not condition:
            print("\nNOT ALL TEAMS HAVE PLAYED THEIR FIRST GAME - ",last_first_game)
       
    # misc
    def first_hm_played(self):
        try:
            self.df.empty()
        except:
            self.schedule_df()
        return self.df.groupby('Home/Neutral').first()['Date'].max()
    
    def first_aw_played(self):
        try:
            self.df.empty()
        except:
            self.schedule_df()
        return self.df.groupby('Visitor/Neutral').first()['Date'].max()


# gs = GetSchedule()
# gs.schedule_df()
