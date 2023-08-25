import pandas as pd
import numpy as np
import logging

from frames.base_fourfactors import BaseFourFactors
from frames.above_below_500 import AboveBelow500

logger = logging.getLogger(__name__)
logger.setLevel(logging.INFO)

formatter = logging.Formatter('%(asctime)s: %(message)s')

file_handler = logging.FileHandler(r'C:\Users\Danie\Desktop\tests\EneBeA\NBA_prediction_bot\logs\adj_ffac_update.log')
file_handler.setFormatter(formatter)

logger.addHandler(file_handler)


class AdjFourFactors(BaseFourFactors,AboveBelow500):
    def __init__(self):
        BaseFourFactors.__init__(self)
        AboveBelow500.__init__(self)

        # create and fill fourfactors dictionaries
        self.base_ffac_df_generator()

        # teamnames and conf used as frame for main df 
        self.adj_ffac = pd.read_csv(r'C:\Users\Danie\Desktop\tests\EneBeA\NBA_prediction_bot\data\TeamName.csv')

        # add win% col to main df
        self.adj_ffac['Win%'] = self.dict_of_df['df_1']['WIN%']

        # MAIN_FOUR_FACTORS_CALC
        self.szn = self.dict_of_df['df_1']['Total_4fac']
        self.l5 = self.dict_of_df['df_2']['Total_4fac']
        self.l15 = self.dict_of_df['df_3']['Total_4fac']
        self.vse = self.dict_of_df['df_4']['Total_4fac']
        self.vsw = self.dict_of_df['df_5']['Total_4fac']
        self.hm = self.dict_of_df['df_6']['Total_4fac']
        self.aw = self.dict_of_df['df_7']['Total_4fac']

        # generate above and below 500 dataframe
        self.parse_request_ab5()['vsaf']

        self.a5 = self.above_below_500['vsaf']
        self.b5 = self.above_below_500['vsbf']

    def adj_ffac_calc(self):
        #SET A/B 500 MARKER FOR DF
        # create a list of our conditions
        conditions = [(self.adj_ffac['Win%'] >= 0.5),(self.adj_ffac['Win%'] < 0.5)]
        # create a list of the values we want to assign for each condition
        values = ['Y', 'N']
        # create a new column and use np.select to assign values to it using our lists as arguments
        self.adj_ffac['A/B'] = np.select(conditions, values)

        #ADJUSTED FOURFACTORS
        self.adj_ffac['base'] = (self.szn+self.l5+self.l15)/3
        self.adj_ffac['vse'] = self.vse/2
        self.adj_ffac['vsw'] = self.vsw/2
        self.adj_ffac['h'] = self.hm/2
        self.adj_ffac['a'] = self.aw/2
        self.adj_ffac['a5'] = self.a5+1
        self.adj_ffac['b5'] = self.b5+1

        #ADJUSTED SUM FOURFACTORS
        self.adj_ffac['vse_h_a5'] = ((self.adj_ffac['base']+self.adj_ffac['vse']+self.adj_ffac['h'])*self.adj_ffac['a5'])/2
        self.adj_ffac['vse_h_b5'] = ((self.adj_ffac['base']+self.adj_ffac['vse']+self.adj_ffac['h'])*self.adj_ffac['b5'])/2
        self.adj_ffac['vsw_h_a5'] = ((self.adj_ffac['base']+self.adj_ffac['vsw']+self.adj_ffac['h'])*self.adj_ffac['a5'])/2
        self.adj_ffac['vsw_h_b5'] = ((self.adj_ffac['base']+self.adj_ffac['vsw']+self.adj_ffac['h'])*self.adj_ffac['b5'])/2
        self.adj_ffac['vse_a_a5'] = ((self.adj_ffac['base']+self.adj_ffac['vse']+self.adj_ffac['a'])*self.adj_ffac['a5'])/2
        self.adj_ffac['vse_a_b5'] = ((self.adj_ffac['base']+self.adj_ffac['vse']+self.adj_ffac['a'])*self.adj_ffac['b5'])/2
        self.adj_ffac['vsw_a_a5'] = ((self.adj_ffac['base']+self.adj_ffac['vsw']+self.adj_ffac['a'])*self.adj_ffac['a5'])/2
        self.adj_ffac['vsw_a_b5'] = ((self.adj_ffac['base']+self.adj_ffac['vsw']+self.adj_ffac['a'])*self.adj_ffac['b5'])/2

        self.adj_ffac.to_csv(fr'C:\Users\Danie\Desktop\tests\EneBeA\NBA_prediction_bot\data\Adj_FFAC.csv',index=False)
        self.adj_ffac.to_json(r'C:\Users\Danie\Desktop\Apps\nba-electron-app\src\backend\data\Adj_FFAC.json', orient='records')
        self.adj_ffac.to_json(r'C:\Users\Danie\Desktop\Apps\nba-react-electron-app\src\renderer\data\Adj_FFAC.json', orient='records')
        

        logger.info(f'{__class__.__name__} UPDATED!')
        return self.adj_ffac
    
