import pandas as pd
import os
import numpy as np

from download import download

url_2 = "https://raw.githubusercontent.com/lukes/ISO-3166-Countries-with-Regional-Codes/master/all/all.csv"
regional_file_name = "regions.csv"

url = "http://vam.wfp.org/sites/data/WFPVAM_FoodPrices_05-12-2017.csv"
file_name = 'WFPVAM_FoodPrices_version2_Retail.csv'

def get_dataset(url, file_name):
    if not os.path.isfile(file_name):
        download(url, file_name)
    return pd.read_csv(file_name, encoding='latin-1')

# Add region and datetime cols.
df = get_dataset(url, file_name)

region_df = get_dataset(url_2, regional_file_name)
region_df.rename(columns={'name': 'adm0_name'}, inplace=True)
new_regions = region_df.loc[:, ['adm0_name', 'sub-region']]
df_regions = pd.merge(df, new_regions, on='adm0_name', how='left')
df = df_regions.copy()

df['date'] = pd.to_datetime(df.date, format='%Y-%m')


countries = set(df['adm0_name'])
products = set(df['cm_name'])


# Visualization
from bokeh.io import curdoc
from bokeh.models.widgets import Tabs
from bokeh.layouts import row, column
from bokeh.models import Select, Panel
from bokeh.layouts import gridplot, layout

from panels.products_per_region import ProductsPerCountry

default_product = "Apples"
default_country = "Afghanistan"

#
# Initialize plot
prod_per_country = ProductsPerCountry(df, default_country)

# # Initialize selectors.
country_select = Select(value=default_country, title='Country', options=sorted(countries))
country_select.on_change('value', prod_per_country.redraw_plot)


# Put all the tabs into one application
grid = gridplot([[prod_per_country.plot]])

# Panels
prod_country_region = Panel(child=grid, title='Product per Region/Country')

# Put the tabs in the current document for display
curdoc().add_root(layout([[country_select], [prod_per_country.plot]]))
