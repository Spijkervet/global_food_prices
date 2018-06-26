import os
import pandas as pd
from WHO import WHO
from download import download


who = WHO()

causes = who.get_causes()

who_countries = who.load_df('who_all_countries.csv')
if who_countries is None:
    who_all = who.get_who()
    countries = who.get_who_countries()
    who_countries = pd.merge(who_all, countries, how='left', left_on='Country', right_on='country')
    who.save_df(who_countries, 'who_all_countries.csv')


from sqlalchemy import create_engine
import pandas as pd

engine = create_engine('mysql://root:root@mysql:3306/uva', echo=True)

who_countries.to_sql('who', engine, index=False)
