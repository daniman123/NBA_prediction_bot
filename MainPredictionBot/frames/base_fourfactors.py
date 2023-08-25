import requests
import pandas as pd
import concurrent.futures
import copy
import logging

logger = logging.getLogger(__name__)
logger.setLevel(logging.INFO)

formatter = logging.Formatter('%(asctime)s: %(message)s')

file_handler = logging.FileHandler(r'C:\Users\Danie\Desktop\tests\EneBeA\NBA_prediction_bot\logs\base_ffac_update.log')
file_handler.setFormatter(formatter)

logger.addHandler(file_handler)


class BaseFourFactors(object):
    def __init__(self):
        # set season year
        YEAR_END = 23
        YEAR_START = YEAR_END-1
        self.SEASON_YEAR = f"{YEAR_START}-{YEAR_END}"
        # request url params 
        szn = {
            'LastNGames':0,
            'Location':'',
            'Conf':'',
        }
        l5 = {
            'LastNGames':5,
            'Location':'',
            'Conf':'',
        }
        l15 = {
            'LastNGames':15,
            'Location':'',
            'Conf':'',
        }
        vseast = {
            'LastNGames':0,
            'Location':'',
            'Conf':'East',
        }
        vswest = {
            'LastNGames':0,
            'Location':'',
            'Conf':'West',
        }
        home = {
            'LastNGames':0,
            'Location':'Home',
            'Conf':'',
        }
        away = {
            'LastNGames':0,
            'Location':'Road',
            'Conf':'',
        }

        self.params_dicts_lst = [szn,l5,l15,vseast,vswest,home,away]
        # pirate headers for request
        self.headers  = {
            'Connection': 'keep-alive',
            'Accept': 'application/json, text/plain, */*',
            'x-nba-stats-token': 'true',
            'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_14_6) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/79.0.3945.130 Safari/537.36',
            'x-nba-stats-origin': 'stats',
            'Sec-Fetch-Site': 'same-origin',
            'Sec-Fetch-Mode': 'cors',
            'Referer': 'https://stats.nba.com/',
            'Accept-Encoding': 'gzip, deflate, br',
            'Accept-Language': 'en-US,en;q=0.9',}
        # base ffac df headers
        self.base_ffac_HEADER_LIST = ['GP','W','L','WIN%','MIN','eFG%','FTARate','TOV%','OREB%','OppeFG%','OppFTARate','OppTOV%','OppOREB%']

        # IMPORTANT 
        # FourFactors calculation constants
        self.SHT = 0.448673
        self.TOT = 0.386925
        self.REB = 0.098396
        self.FT = 0.066006
        # IMPORTANT

        self.dict_of_df = {}

    def request_parse(self,params):
        # XHR fetch-url
        url = f"https://stats.nba.com/stats/leaguedashteamstats?Conference=&DateFrom=&DateTo=&Division=&GameScope=&GameSegment=&LastNGames={params['LastNGames']}&LeagueID=00&Location={params['Location']}&MeasureType=Four+Factors&Month=0&OpponentTeamID=0&Outcome=&PORound=0&PaceAdjust=N&PerMode=PerGame&Period=0&PlayerExperience=&PlayerPosition=&PlusMinus=N&Rank=N&Season=20{self.SEASON_YEAR}&SeasonSegment=&SeasonType=Regular+Season&ShotClockRange=&StarterBench=&TeamID=0&TwoWay=0&VsConference={params['Conf']}&VsDivision="
        
        response = requests.Session().get(url=url,headers=self.headers).json()
        # parse request response
        team_info = response['resultSets'][0]['rowSet']
        team_info = [i[:-15] for i in team_info]
        team_info = [i[2:] for i in team_info]
        return team_info

    def params_url_loop(self,params):
        # set csv file num based on dict index
        csv_nm = self.params_dicts_lst.index(params)+1

        # produce FourFactors Dataframe
        df = pd.DataFrame(self.request_parse(params), columns=self.base_ffac_HEADER_LIST)
        # set col type as float
        for column in df:
            df[column] = df[column].astype(float)

        # FFAC BASE CALCULATIONS
        #Off_4Fac
        df['Off_4fac'] = \
            self.SHT * (df['eFG%'].astype(float) ) + \
            self.TOT * (1 - (df['TOV%'].astype(float))) + \
            self.REB * (df['OREB%'].astype(float) ) + \
            self.FT * (df['FTARate'].astype(float))
        #Def 4Fac
        df['Def_4fac'] = \
            self.SHT * (1-(df['OppeFG%'].astype(float) )) + \
            self.TOT * (df['OppTOV%'].astype(float)) + \
            self.REB * (1-(df['OppOREB%'].astype(float))) + \
            self.FT * (1-(df['OppFTARate'].astype(float)))
        #Total 4fac
        df['Total_4fac'] = \
            df['Off_4fac'].astype(float) + \
            df['Def_4fac'].astype(float)
        
        # multiply third FourFactors w/ win%
        if csv_nm == 3:
            df['Total_4fac'] = df['Total_4fac']*(df['WIN%']+1)
        
        # multiply Total_4fac with correlation to win%
        cor = df.corr(method='pearson').loc['WIN%'].tail(1)
        df['Total_4fac'] = df['Total_4fac'].multiply(float(cor))

        # name dictionary
        key_name = 'df_'+str(csv_nm)    
        self.dict_of_df[key_name] = copy.deepcopy(df)

        df.to_csv(fr'C:\Users\Danie\Desktop\tests\EneBeA\NBA_prediction_bot\data\fourfacs\{csv_nm}.csv',index=False)
    # MAIN 
    def base_ffac_df_generator(self):
        with concurrent.futures.ThreadPoolExecutor() as executor:
            executor.map(self.params_url_loop,self.params_dicts_lst)
        logger.info(f'{__class__.__name__} UPDATED!')

# bff = BaseFourFactors()
# bff.base_ffac_df_generator()