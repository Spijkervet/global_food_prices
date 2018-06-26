
import sys

sys.path.append('../')

import os
import pandas as pd
import numpy as np
from download import download

class WHO():
    def __init__(self):
        self.DATA_DIR = "./WHO/data"

    def load_df(self, file_name):
        path = os.path.join(self.DATA_DIR, file_name)
        if os.path.isfile(path):
            print("### LOADING {} ###".format(file_name))
            return pd.read_csv(path)
        return None

    def save_df(self, df, file_name):
        df.to_csv(os.path.join(self.DATA_DIR, file_name))

    def get_causes(self):
        WHO_CAUSES = os.path.join(self.DATA_DIR, 'who_cause_codes.csv')
        return pd.read_csv(WHO_CAUSES, dtype={'code': np.object_})

    def get_who_countries(self):
        WHO_COUNTRIES = os.path.join(self.DATA_DIR, 'country_codes')
        if not os.path.isfile(WHO_COUNTRIES):
            download('http://www.who.int/healthinfo/statistics/country_codes.zip', WHO_COUNTRIES + '.zip')

        return pd.read_csv(WHO_COUNTRIES)


    def get_who(self):
        who_all = self.load_df('who_all.csv')
        if who_all is None:
            WHO_PART_PATH_1 = os.path.join(self.DATA_DIR, 'Morticd10_part1')
            WHO_PART_PATH_2 = os.path.join(self.DATA_DIR, 'Morticd10_part2')
            if not os.path.isfile(WHO_PART_PATH_1) or not os.path.isfile(WHO_PART_PATH_2):
                print("### DOWNLOADING WHO DATASETS ###")
                download('http://www.who.int/healthinfo/statistics/Morticd10_part1.zip', WHO_PART_PATH_1 + '.zip')
                download('http://www.who.int/healthinfo/statistics/Morticd10_part2.zip', WHO_PART_PATH_2 + '.zip')

            print("### APPENDING WHO DATASETS ###")
            who_1 = pd.read_csv(WHO_PART_PATH_1, dtype={'Cause': np.object_})
            who_2 = pd.read_csv(WHO_PART_PATH_2, dtype={'Cause': np.object_})
            who_all = who_1.append(who_2)

            self.save_df(who_all, 'who_all.csv')

        return who_all
