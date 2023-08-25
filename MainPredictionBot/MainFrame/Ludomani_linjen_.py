
class Ludomani_linjen():

        def __init__(self):

                #IMPORTS
                import pandas as pd
                import numpy as np

                from selenium import webdriver
                from selenium.webdriver.chrome.options import Options
                from selenium.webdriver.common.by import By
                from selenium.webdriver.support.ui import WebDriverWait
                from selenium.webdriver.support import expected_conditions as EC
                from selenium.webdriver.common.action_chains import ActionChains
                from selenium.webdriver.chrome.service import Service
                from datetime import datetime, timedelta

                
         #ABOVE_BELOW_500

                self.url_ab5 = "https://www.espn.co.uk/nba/table/_/group/league/view/expanded"

                self.table_teams_CSS_SELECTOR_ab5 = "tbody tr td:nth-child(1) div:nth-child(1) span:nth-child(3) a"
                self.table_row_CSS_SELECTOR_ab5 = "table:nth-child(1) > tbody:nth-child(6) > tr > td > span"


         #FOURFACTORS

                szn = {
                        'LastNGames':0,
                        'Location':' ',
                        'Conf':' ',
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

                self.dict_of_df = {}

         #DAILY_4FAC

                self.fofac_d_4fac = pd.read_csv(r'C:\Users\Danie\Desktop\tests\EneBeA\NBA_prediction_bot\fourfacs\TeamName.csv')

                self.a5_d_4fac = pd.read_csv(r'C:\Users\Danie\Desktop\tests\EneBeA\NBA_prediction_bot\fourfacs\A5B5.csv',usecols=['vsaf'])
                self.b5_d_4fac = pd.read_csv(r'C:\Users\Danie\Desktop\tests\EneBeA\NBA_prediction_bot\fourfacs\A5B5.csv',usecols=['vsbf'])

        def sched(self):
                        
                import requests
                import pandas as pd
                import numpy as np

                url = f"https://cdn.nba.com/static/json/staticData/scheduleLeagueV2_51.json"

                response = requests.Session().get(url=url).json()

                #importer datetime
                from datetime import datetime, timedelta

                sched_yesterday = []

                for i,game_day in enumerate(response['leagueSchedule']['gameDates']):
                # date = game_day['games'][i]['gameDateEst']
                        for i,game in enumerate(game_day['games']):

                                date = game['gameDateEst'][:-10]
                                datetimeobject = datetime.strptime(date,'%Y-%m-%d')
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

                                # log regular season games
                                season_start = datetime.strptime("18-10-2022","%d-%m-%Y")
                                current_day = datetime.strptime(date,"%d-%m-%Y")
                                if current_day >= season_start:
                                        data_row = [date,away_team,away_score,home_team,home_score,'']
                                        sched_yesterday.append(data_row)


                headers = ['Date','Visitor/Neutral','PTS','Home/Neutral','PTS.1','Result']
                df = pd.DataFrame(sched_yesterday,columns=headers)

                #kriterier 
                conditions = [(df['PTS'] > df['PTS.1']),(df['PTS'] < df['PTS.1'])]
                # create a list of the values we want to assign for each condition
                values = [df['Visitor/Neutral'], df['Home/Neutral']]
                # create a new column and use np.select to assign values to it using our lists as arguments
                df['Result'] = np.select(conditions, values)
                
                df.to_csv(r'C:\Users\Danie\Desktop\tests\EneBeA\NBA_prediction_bot\Scheds\Schedule.csv',index=False)
                print('sched : FINISHED')

        def above_below_500(self):
                from urllib.request import urlopen as ureq
                from bs4 import BeautifulSoup as soup
                import pandas as pd
                import requests

                def team_sts_loop(teamstats_css):
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

                def team_nm_loop(teamnames_css):
                        teamnames = []
                        for i in teamnames_css:
                                data = i.text
                                data = data.replace('LA Clippers', 'Los Angeles Clippers')
                                teamnames.append(data)
                        return teamnames    

                r = requests.Session().get(self.url_ab5)
                page_soup = soup(r.text,"lxml")
                teamnames_css = page_soup.select("tbody tr td:nth-child(1) div:nth-child(1) span:nth-child(3) a")
                teamstats_css = page_soup.select("table:nth-child(1) > tbody:nth-child(6) > tr > td > span")
                df = pd.DataFrame(team_sts_loop(teamstats_css),columns=None)
                df.insert(0,'Team',team_nm_loop(teamnames_css))
                a = df.Team.values.astype(str).argsort()
                a = pd.DataFrame(df.values[a], df.index[a], df.columns)    
                a['vsaf'] = a[0].astype(float)/(a[0].astype(float) + a[1].astype(float))
                a['vsbf'] = a[2].astype(float)/(a[2].astype(float) + a[3].astype(float))
                a['vsaf'] = a['vsaf'].astype(float)
                a['vsbf'] = a['vsbf'].astype(float)
                a.reset_index(drop=True, inplace=True)    
                a.to_csv(fr'C:\Users\Danie\Desktop\tests\EneBeA\NBA_prediction_bot\fourfacs\A5B5.csv',index=False)
                
                print('above_below_500 : FINISHED')
                
        def base_fourfactors(self):
                
                import requests
                import pandas as pd
                import concurrent.futures

                def req(params):
                        # XHR fetch-url
                        url = f"https://stats.nba.com/stats/leaguedashteamstats?Conference=&DateFrom=&DateTo=&Division=&GameScope=&GameSegment=&LastNGames={params['LastNGames']}&LeagueID=00&Location={params['Location']}&MeasureType=Four+Factors&Month=0&OpponentTeamID=0&Outcome=&PORound=0&PaceAdjust=N&PerMode=PerGame&Period=0&PlayerExperience=&PlayerPosition=&PlusMinus=N&Rank=N&Season=2022-23&SeasonSegment=&SeasonType=Regular+Season&ShotClockRange=&StarterBench=&TeamID=0&TwoWay=0&VsConference={params['Conf']}&VsDivision="
                        # pirate headers
                        headers  = {
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

                        response = requests.Session().get(url=url,headers=headers).json()
                        # parse request response
                        team_info = response['resultSets'][0]['rowSet']
                        team_info = [i[:-15] for i in team_info]
                        team_info = [i[2:] for i in team_info]

                        return team_info

                def params_url_loop(params):
                        import copy

                        csv_nm = self.params_dicts_lst.index(params)+1

                        # produce FourFactors Dataframe
                        HEADER_LIST = ['GP','W','L','WIN%','MIN','eFG%','FTARate','TOV%','OREB%','OppeFG%','OppFTARate','OppTOV%','OppOREB%']
                        df = pd.DataFrame(req(params), columns=HEADER_LIST)
                        # set col type as float
                        for column in df:
                                df[column] = df[column].astype(float)

                        # FourFactors calculation constants
                        SHT = 0.448673
                        TOT = 0.386925
                        REB = 0.098396
                        FT = 0.066006

                        #Off_4Fac
                        df['Off_4fac'] = \
                                SHT * (df['eFG%'].astype(float) ) + \
                                TOT * (1 - (df['TOV%'].astype(float))) + \
                                REB * (df['OREB%'].astype(float) ) + \
                                FT * (df['FTARate'].astype(float))
                        #Def 4Fac
                        df['Def_4fac'] = \
                                SHT * (1-(df['OppeFG%'].astype(float) )) + \
                                TOT * (df['OppTOV%'].astype(float)) + \
                                REB * (1-(df['OppOREB%'].astype(float))) + \
                                FT * (1-(df['OppFTARate'].astype(float)))
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
                        df.to_csv(fr'C:\Users\Danie\Desktop\tests\EneBeA\NBA_prediction_bot\fourfacs\{csv_nm}.csv',index=False)

                with concurrent.futures.ThreadPoolExecutor() as executor:
                        executor.map(params_url_loop,self.params_dicts_lst)

        def daily_4fac(self):
                import pandas as pd
                import numpy as np
                import datetime


                fofac=self.fofac_d_4fac
                win_pct=self.dict_of_df['df_1']

                # MAIN_FOUR_FACTORS_CALC
                szn = self.dict_of_df['df_1']['Total_4fac']
                l5 = self.dict_of_df['df_2']['Total_4fac']
                l15 = self.dict_of_df['df_3']['Total_4fac']
                vse = self.dict_of_df['df_4']['Total_4fac']
                vsw = self.dict_of_df['df_5']['Total_4fac']
                h = self.dict_of_df['df_6']['Total_4fac']
                a = self.dict_of_df['df_7']['Total_4fac']

                a5 = self.a5_d_4fac
                b5 = self.b5_d_4fac


                #FOURFACTORS A/B 500 MARKER
                fofac['Win%'] = win_pct['WIN%']
                # create a list of our conditions
                conditions = [(fofac['Win%'] >= 0.5),(fofac['Win%'] < 0.5)]
                # create a list of the values we want to assign for each condition
                values = ['Y', 'N']
                # create a new column and use np.select to assign values to it using our lists as arguments
                fofac['A/B'] = np.select(conditions, values)

                #ADJUSTED FOURFACTORS
                fofac['base'] = (szn+l5+l15)/3
                fofac['vse'] = vse/2
                fofac['vsw'] = vsw/2
                fofac['h'] = h/2
                fofac['a'] = a/2
                fofac['a5'] = a5+1
                fofac['b5'] = b5+1

                #ADJUSTED SUM FOURFACTORS
                fofac['vse_h_a5'] = ((fofac['base']+fofac['vse']+fofac['h'])*fofac['a5'])/2
                fofac['vse_h_b5'] = ((fofac['base']+fofac['vse']+fofac['h'])*fofac['b5'])/2
                fofac['vsw_h_a5'] = ((fofac['base']+fofac['vsw']+fofac['h'])*fofac['a5'])/2
                fofac['vsw_h_b5'] = ((fofac['base']+fofac['vsw']+fofac['h'])*fofac['b5'])/2
                fofac['vse_a_a5'] = ((fofac['base']+fofac['vse']+fofac['a'])*fofac['a5'])/2
                fofac['vse_a_b5'] = ((fofac['base']+fofac['vse']+fofac['a'])*fofac['b5'])/2
                fofac['vsw_a_a5'] = ((fofac['base']+fofac['vsw']+fofac['a'])*fofac['a5'])/2
                fofac['vsw_a_b5'] = ((fofac['base']+fofac['vsw']+fofac['a'])*fofac['b5'])/2
                
                #KAMPE I DAG
                df = pd.read_csv(r'C:\Users\Danie\Desktop\tests\EneBeA\NBA_prediction_bot\Scheds\Schedule.csv',sep=",")

                #importer datetime
                from datetime import datetime, timedelta
                yesterday = (datetime.today()-timedelta(days=1)).strftime('%d-%m-%Y')
                #navngiv dags dato funktion som string
                today = (datetime.today()).strftime('%d-%m-%Y')
                
                #filtrer dataframe til dags dato
                df = df[df['Date']==today]
                #fjern kolonner med indeks
                df = df.iloc[:,:7]
                #df = df.iloc[:,2:]

                #fjern kolonner ved navn
                # df = df.drop(columns=['Conf','A/B 500','PTS'])
                df = df.drop(columns=['PTS','PTS.1','Result'])

                #AWAY DAILY FILTER
                def aw_loc_4fac_col(z,i,x):
                        #Away/VsEast/A500
                        if fofac.iloc[z]['Conf'] == 'East' and fofac.iloc[z]['A/B'] == 'Y':
                                df.at[i,'4FacA'] = fofac.iloc[x]['vse_a_a5'].astype(float)
                        #Away/VsEast/B500
                        elif fofac.iloc[z]['Conf'] == 'East' and fofac.iloc[z]['A/B'] == 'N':
                                df.at[i,'4FacA'] = fofac.iloc[x]['vse_a_b5'].astype(float)
                        #Away/VsWest/A500
                        elif fofac.iloc[z]['Conf'] == 'West' and fofac.iloc[z]['A/B'] == 'Y':
                                df.at[i,'4FacA'] = fofac.iloc[x]['vsw_a_a5'].astype(float)
                        #Away/VsWest/B500
                        elif fofac.iloc[z]['Conf'] == 'West' and fofac.iloc[z]['A/B'] == 'N':
                                df.at[i,'4FacA'] = fofac.iloc[x]['vsw_a_b5'].astype(float)

                #Loop igennem daily_away_team_list
                for i, row in df['Visitor/Neutral'].iteritems():
                        #Loop igennem 4fac_calc_list
                        for x,j in fofac['Team'].iteritems():
                                #Match begge loops
                                if row == j:
                                #Loop for home_team til match med kriterier
                                        for y, rw in df['Home/Neutral'].iteritems():
                                                #Loop 4fac_calc_list for home_team
                                                for z,h in fofac['Team'].iteritems():
                                                #Match begge loops.2 
                                                        if rw == h and y==i:
                                                                aw_loc_4fac_col(z,i,x)

                #HOME DAILY FILTER
                def hm_loc_4fac_col(z,i,x):
                        #Home/VsEast/A500
                        if fofac.iloc[z]['Conf'] == 'East' and fofac.iloc[z]['A/B'] == 'Y':
                                df.at[i,'4FacH'] = fofac.iloc[x]['vse_h_a5'].astype(float)
                        #Home/VsEast/B500
                        elif fofac.iloc[z]['Conf'] == 'East' and fofac.iloc[z]['A/B'] == 'N':
                                df.at[i,'4FacH'] = fofac.iloc[x]['vse_h_b5'].astype(float)
                        #Home/VsWest/A500
                        elif fofac.iloc[z]['Conf'] == 'West' and fofac.iloc[z]['A/B'] == 'Y':
                                df.at[i,'4FacH'] = fofac.iloc[x]['vsw_h_a5'].astype(float)
                        #Home/VsWest/B500
                        elif fofac.iloc[z]['Conf'] == 'West' and fofac.iloc[z]['A/B'] == 'N':
                                df.at[i,'4FacH'] = fofac.iloc[x]['vsw_h_b5'].astype(float)
                        
                #Loop igennem daily_home_team_list
                for i, row in df['Home/Neutral'].iteritems():
                        #Loop igennem 4fac_calc_list
                        for x,j in fofac['Team'].iteritems():
                                #Match begge loops
                                if row == j:
                                #Loop for away_team til match med kriterier
                                        for y, rw in df['Visitor/Neutral'].iteritems():
                                                #Loop 4fac_calc_list for away_team
                                                for z,h in fofac['Team'].iteritems():
                                                #Match begge loops.2 
                                                        if rw == h and y==i:
                                                                hm_loc_4fac_col(z,i,x)

                #WINNER PREDICTION TO DATAFRAME
                for i, row in df.iterrows():
                        #hvis away_4fac > home_4fac
                        if df['4FacA'][i] > df['4FacH'][i]:
                                #away_4fac > home_4fac 
                                df.at[i,'Win_Pred'] = df['Visitor/Neutral'][i]
                                df.at[i,'Win_4Fac'] = df['4FacA'][i]
                                #tilføj avg_4fac for away_team
                                #df['Avg_A'] = fofac.iloc[x]['Avg_4Fac'].astype(float)
                                df.at[i,'>_%'] = (((df['4FacA'][i]-df['4FacH'][i])/df['4FacA'][i])*100).round(2)
                                df.at[i,'Loss_Pred'] = df['Home/Neutral'][i]
                                df.at[i,'Loss_4Fac'] = df['4FacH'][i]   
                        else:
                                #home_4fac > away_4fac
                                df.at[i,'Win_Pred'] = df['Home/Neutral'][i]
                                df.at[i,'Win_4Fac'] = df['4FacH'][i]
                                #tilføj avg_4fac for home_team
                                #df['Avg_H'] = fofac.iloc[x]['Avg_4Fac'].astype(float)
                                df.at[i,'>_%'] = (((df['4FacH'][i]-df['4FacA'][i])/df['4FacH'][i])*100).round(2)
                                df.at[i,'Loss_Pred'] = df['Visitor/Neutral'][i]
                                df.at[i,'Loss_4Fac'] = df['4FacA'][i]
                        
                        
                #Fjern relevante kolonner
                try:
                        df = df.drop(columns=['4FacA','4FacH'])
                except:
                        pass

                df.reset_index(drop=True, inplace=True)

                self.df = df
                self.fofac = fofac

                return df

        def data_log_update(self):

                import pandas as pd
                import numpy as np
                #importer datetime
                from datetime import datetime, timedelta
                #navngiv dags dato funktion som string
                ystr_yesterday = (datetime.today()-timedelta(days=2)).strftime('%d-%m-%Y')
                yesterday = (datetime.today()-timedelta(days=1)).strftime('%d-%m-%Y')
                today = (datetime.today()).strftime('%d-%m-%Y')

                #mod sched til datalog
                def sched_to_datalog():
                        data_log_out = pd.read_csv(r'C:\Users\Danie\Desktop\tests\EneBeA\NBA_prediction_bot\logs\data_logs\DataLog.csv')
                        data_log_out = data_log_out[data_log_out['Date']==yesterday]

                        # data_log_out = data_log_out.set_index(schedule.index)

                        #definér sched_idag
                        schedule = pd.read_csv(r'C:\Users\Danie\Desktop\tests\EneBeA\NBA_prediction_bot\Scheds\Schedule.csv')
                        schedule = schedule[schedule['Date']==yesterday]

                        data_log_out['Result'] = schedule['Result']
                        # create a list of our conditions
                        conditions = [(data_log_out['Result'] == data_log_out['Win_Pred']),(data_log_out['Result'] == data_log_out['Loss_Pred'])]
                        # create a list of the values we want to assign for each condition
                        values = ['True', 'False']
                        # create a new column and use np.select to assign values to it using our lists as arguments
                        data_log_out['Pred.Result'] = np.select(conditions, values)
                       
                        return data_log_out
                                
                #datalog to csv
                def datalog_to_csv():
                        df = self.daily_4fac()
                        df.reset_index(drop=True, inplace=True)
                        data_log_out = sched_to_datalog().append(df)
                        data_log_out.reset_index(drop=True, inplace=True)

                        # data log 2
                        data_log_out2 = pd.read_csv(r'C:\Users\Danie\Desktop\tests\EneBeA\NBA_prediction_bot\logs\data_logs\DataLog.csv')
                        data_log_out2 = data_log_out2[data_log_out2['Date']<yesterday]
                        data_log_out2 = data_log_out2.append(data_log_out)
                        data_log_out2.reset_index(drop=True, inplace=True)
                        data_log_out2.to_csv(r'C:\Users\Danie\Desktop\tests\EneBeA\NBA_prediction_bot\logs\data_logs\DataLog.csv', mode='w', header=True,index=False)

                check = pd.read_csv(r'C:\Users\Danie\Desktop\tests\EneBeA\NBA_prediction_bot\logs\data_logs\DataLog.csv')
                check = check[check['Date']==today]
                if len(check) > 0:
                        from termcolor import colored
                        print()
                        print(colored('TODAYS VAlUES ARE ALREADY LOGGED', 'yellow'))
                        print()
                else:
                        datalog_to_csv()

        def df_to_html(self):
                #self.df fra DAILY_4FAC()
                html = self.df.to_html(index=False,justify='center')
                # write html to file    
                text_file = open(r"C:\Users\Danie\Desktop\tests\EneBeA\NBA_prediction_bot\HTML\table.html", "w")
                text_file.write(html)
                text_file.close()

                html = self.fofac.to_html(index=False,justify='center')
                # write html to file    
                text_file = open(r"C:\Users\Danie\Desktop\tests\EneBeA\NBA_prediction_bot\HTML\table.html", "a")
                text_file.write(html)
                text_file.close()

                with open(r"C:\Users\Danie\Desktop\tests\EneBeA\NBA_prediction_bot\HTML\table.html","r") as file:
                        file = file.read()
                file = file.replace('<table border="1" class="dataframe">','<table border=1, style= "color: white;background-color: blue;padding: 5px;border: 1px solid black;text-align:center;margin:5px">')

                with open(r"C:\Users\Danie\Desktop\tests\EneBeA\NBA_prediction_bot\HTML\table.html","w") as file_to_write:
                        file_to_write.write(file)
        
        def prnt_val(self):

                print(self.fofac)
                print()
                if not self.df.empty:
                        print(self.df)
                else:
                        print("NO GAMES TODAY")

        def run(self):
                import concurrent.futures
                print() 
                with concurrent.futures.ThreadPoolExecutor() as executor:     
                        executor.submit(self.sched(),self.above_below_500())

                self.base_fourfactors()
                print('fourfactors : FINISHED') 
                self.daily_4fac()
                print('daily_4fac : FINISHED')
                self.data_log_update() 
                print('data_log_update : FINISHED')
                self.df_to_html()
                print('df_to_html : FINISHED') 
                self.prnt_val() 
                print()



from timeit import default_timer as timer

if __name__ == '__main__': 
        start = timer()
        l = Ludomani_linjen()
        l.run()
        end = timer()
        print(end - start)