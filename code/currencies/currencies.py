import pandas as pd
import matplotlib.pyplot as plt


df = pd.read_csv('all_currencies.csv')


curr = set(df['base_currency'])
print(curr)

for i in curr:
    d = df.loc[df['base_currency'] == i, 'datetime']
    print(i, min(d), max(d))

# plt.plot(amd_df['datetime'], amd_df['rate'])
# plt.show()
