import pandas as pd

df = pd.read_csv('WFPVAM_FoodPrices_version1.csv')
df_currencies = pd.read_csv('all_currencies.csv')
df_currencies.columns = ['cur_name', 'date', 'rate']

merged_currencies = pd.DataFrame.merge(df, df_currencies,
                        on=['cur_name', 'date'],
                        how='left')


merged_currencies.to_csv('WFPVAM_FoodPrices_with_rates.csv')
