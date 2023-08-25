import pandas as pd
import requests
import numpy as np
from datetime import datetime, timedelta
import logging


from frames.adj_fourfactors import AdjFourFactors
from frames.get_schedule import GetSchedule


logger = logging.getLogger(__name__)
logger.setLevel(logging.INFO)

formatter = logging.Formatter('%(asctime)s: %(message)s')

file_handler = logging.FileHandler(r'C:\Users\Danie\Desktop\tests\EneBeA\NBA_prediction_bot\logs\data_log_update.log')
file_handler.setFormatter(formatter)

logger.addHandler(file_handler)

data_log_path = r'C:\Users\Danie\Desktop\tests\EneBeA\NBA_prediction_bot\data\DataLog.csv'

class NBAPrediction(AdjFourFactors,GetSchedule):
    def __init__(self):
        AdjFourFactors.__init__(self)
        GetSchedule.__init__(self)

    def daily_4fac(self):
        adjusted_fourfactors_df = self.adj_ffac_calc()
        # self.df_to_html(adjusted_fourfactors_df)
        # OUPUT ADJUSTED FOURFACTORS
        print("\n",adjusted_fourfactors_df,"\n")

        self.sched_df = self.schedule_df()
        df = self.sched_df

        #navngiv dags dato funktion som string
        today = (datetime.today()).strftime('%d-%m-%Y')
        
        #filtrer dataframe til dags dato
        df = df[df['Date']==today]

        # empty dataset check
        cond = adjusted_fourfactors_df['base'].isnull().values.all()

        # check if games today
        if df.empty or cond:
            print("\nNO GAMES TODAY\n")
        elif not cond:
            
            #fjern kolonner med indeks
            df = df.iloc[:,:7]

            #fjern kolonner ved navn
            df = df.drop(columns=['PTS','PTS.1','Result'])

            #AWAY DAILY FILTER
            def aw_loc_4fac_col(z,i,x):
                #Away/VsEast/A500
                if self.adj_ffac.iloc[z]['Conf'] == 'East' and self.adj_ffac.iloc[z]['A/B'] == 'Y':
                    df.at[i,'4FacA'] = self.adj_ffac.iloc[x]['vse_a_a5'].astype(float)
                #Away/VsEast/B500
                elif self.adj_ffac.iloc[z]['Conf'] == 'East' and self.adj_ffac.iloc[z]['A/B'] == 'N':
                    df.at[i,'4FacA'] = self.adj_ffac.iloc[x]['vse_a_b5'].astype(float)
                #Away/VsWest/A500
                elif self.adj_ffac.iloc[z]['Conf'] == 'West' and self.adj_ffac.iloc[z]['A/B'] == 'Y':
                    df.at[i,'4FacA'] = self.adj_ffac.iloc[x]['vsw_a_a5'].astype(float)
                #Away/VsWest/B500
                elif self.adj_ffac.iloc[z]['Conf'] == 'West' and self.adj_ffac.iloc[z]['A/B'] == 'N':
                    df.at[i,'4FacA'] = self.adj_ffac.iloc[x]['vsw_a_b5'].astype(float)

            #Loop igennem daily_away_team_list
            for i, row in df['Visitor/Neutral'].iteritems():
                #Loop igennem 4fac_calc_list
                for x,j in self.adj_ffac['Team'].iteritems():
                    #Match begge loops
                    if row == j:
                    #Loop for home_team til match med kriterier
                        for y, rw in df['Home/Neutral'].iteritems():
                            #Loop 4fac_calc_list for home_team
                            for z,h in self.adj_ffac['Team'].iteritems():
                            #Match begge loops.2 
                                if rw == h and y==i:
                                    aw_loc_4fac_col(z,i,x)

            #HOME DAILY FILTER
            def hm_loc_4fac_col(z,i,x):
                #Home/VsEast/A500
                if self.adj_ffac.iloc[z]['Conf'] == 'East' and self.adj_ffac.iloc[z]['A/B'] == 'Y':
                    df.at[i,'4FacH'] = self.adj_ffac.iloc[x]['vse_h_a5'].astype(float)
                #Home/VsEast/B500
                elif self.adj_ffac.iloc[z]['Conf'] == 'East' and self.adj_ffac.iloc[z]['A/B'] == 'N':
                    df.at[i,'4FacH'] = self.adj_ffac.iloc[x]['vse_h_b5'].astype(float)
                #Home/VsWest/A500
                elif self.adj_ffac.iloc[z]['Conf'] == 'West' and self.adj_ffac.iloc[z]['A/B'] == 'Y':
                    df.at[i,'4FacH'] = self.adj_ffac.iloc[x]['vsw_h_a5'].astype(float)
                #Home/VsWest/B500
                elif self.adj_ffac.iloc[z]['Conf'] == 'West' and self.adj_ffac.iloc[z]['A/B'] == 'N':
                    df.at[i,'4FacH'] = self.adj_ffac.iloc[x]['vsw_h_b5'].astype(float)
                    
            #Loop igennem daily_home_team_list
            for i, row in df['Home/Neutral'].iteritems():
                #Loop igennem 4fac_calc_list
                for x,j in self.adj_ffac['Team'].iteritems():
                    #Match begge loops
                    if row == j:
                    #Loop for away_team til match med kriterier
                        for y, rw in df['Visitor/Neutral'].iteritems():
                            #Loop 4fac_calc_list for away_team
                            for z,h in self.adj_ffac['Team'].iteritems():
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
                    df.at[i,'>_%'] = (((df['4FacA'][i]-df['4FacH'][i])/df['4FacA'][i])*100).round(2)
                    df.at[i,'Loss_Pred'] = df['Home/Neutral'][i]
                    df.at[i,'Loss_4Fac'] = df['4FacH'][i]   
                else:
                    #home_4fac > away_4fac
                    df.at[i,'Win_Pred'] = df['Home/Neutral'][i]
                    df.at[i,'Win_4Fac'] = df['4FacH'][i]
                    #tilføj avg_4fac for home_team
                    df.at[i,'>_%'] = (((df['4FacH'][i]-df['4FacA'][i])/df['4FacH'][i])*100).round(2)
                    df.at[i,'Loss_Pred'] = df['Visitor/Neutral'][i]
                    df.at[i,'Loss_4Fac'] = df['4FacA'][i]
                    
                    
            #Fjern relevante kolonner
            df = df.drop(columns=['4FacA','4FacH'])
            df.reset_index(drop=True, inplace=True)

            self.daily_ffac_df = df

            # OUTPUT DAILY PREDICTIONS
            print("\n",df,"\n")
            df.to_csv(r'C:\Users\Danie\Desktop\tests\EneBeA\NBA_prediction_bot\data\daily_ffac.csv',index=False)
            df.to_json(r'C:\Users\Danie\Desktop\Apps\nba-react-electron-app\src\renderer\data\daily_ffac.json', orient='records')
            
            # store data log in csv
            self.data_log_df()

    def data_log_df(self):
        yesterday = (datetime.today()-timedelta(days=1)).strftime('%d-%m-%Y')
        today = (datetime.today()).strftime('%d-%m-%Y')

        # schedule to datalog
        data_log_out = pd.read_csv(data_log_path)
        data_log_out = data_log_out[data_log_out['Date']==yesterday]

        schedule = self.sched_df
        schedule = schedule[schedule['Date']==yesterday]
        data_log_out['Result'] = schedule['Result']
        # create a list of our conditions
        conditions = [(data_log_out['Result'] == data_log_out['Win_Pred']),(data_log_out['Result'] == data_log_out['Loss_Pred'])]
        # create a list of the values we want to assign for each condition
        values = ['True', 'False']
        # create a new column and use np.select to assign values to it using our lists as arguments
        data_log_out['Pred.Result'] = np.select(conditions, values)

        check = pd.read_csv(data_log_path)
        check = check[check['Date']==today]
        if len(check) > 0:
            from termcolor import colored
            print(colored('TODAYS VAlUES ARE ALREADY LOGGED\n', 'yellow'))
        else:
            # datalog to csv
            df = self.daily_ffac_df
            df.reset_index(drop=True, inplace=True)
            data_log_out = data_log_out.append(df)
            data_log_out.reset_index(drop=True, inplace=True)

            # data log 2
            data_log_out2 = data_log_out
            data_log_out2 = data_log_out2[data_log_out2['Date']<yesterday]
            data_log_out2 = data_log_out2.append(data_log_out)
            data_log_out2.reset_index(drop=True, inplace=True)
            data_log_out2.to_csv(data_log_path, mode='w', header=True,index=False)

            logger.info('DataLog UPDATED!')

    def getInj(self):
        url = "https://www.rotowire.com/basketball/tables/injury-report.php?team=ALL&pos=ALL"
        response = requests.Session().get(url=url).json()

        headers = [
            'Player',
            'Team',
            'Position',
            'Injury',
            'Status',]

        data = []

        for i in response:
            data_input = i['player'],i['team'],i['position'],i['injury'],i['status']
            data.append(data_input)

        df = pd.DataFrame(data, columns=headers)
        df.to_csv(r"C:\Users\Danie\Desktop\tests\EneBeA\NBA_prediction_bot\data\injuries.csv",index=False)
        df.to_json(r'C:\Users\Danie\Desktop\Apps\nba-react-electron-app\src\renderer\data\injuries.json', orient='records')

from timeit import default_timer as timer

if __name__ == '__main__': 
    start = timer()
    nbp = NBAPrediction()
    nbp.daily_4fac()
    nbp.getInj()
    end = timer()
    print(end - start)


from flask import Flask

