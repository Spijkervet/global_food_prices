import pandas as pd
import os
import numpy as np

from download import download

url_2 = "https://raw.githubusercontent.com/lukes/ISO-3166-Countries-with-Regional-Codes/master/all/all.csv"
regional_file_name = "regions.csv"

url = "http://vam.wfp.org/sites/data/WFPVAM_FoodPrices_05-12-2017.csv"
file_name = 'WFPVAM_FoodPrices.csv'

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
df['datetime'] = pd.to_datetime(df.mp_year*10000+df.mp_month*100+1, format='%Y%m%d')



countries = set(df['adm0_name'])
products = set(df['cm_name'])


# Visualization
from bokeh.io import curdoc
from bokeh.models.widgets import Tabs
from bokeh.layouts import row, column
from bokeh.models import Select, Panel
from bokeh.layouts import gridplot, layout

from panels.products_per_country import ProductsPerCountry
from panels.products_per_region import ProductsPerRegion

default_product = "Apples"

# Initialize plot
prod_per_country = ProductsPerCountry(df, default_product)
prod_per_region = ProductsPerRegion(df, default_product)

# Initialize selectors.
country_select = Select(value=default_product, title='Product', options=sorted(products))
country_select.on_change('value', prod_per_country.redraw_plot)
country_select.on_change('value', prod_per_region.redraw_plot)


# Put all the tabs into one application
grid = gridplot([[prod_per_country.plot, prod_per_region.plot]])

# Panels
prod_country_region = Panel(child=grid, title='Product per Region/Country')
new_tab = Panel(child=grid, title='Currency')

# Create tabs
tabs = Tabs(tabs = [prod_country_region])


# Put the tabs in the current document for display
curdoc().add_root(layout([[country_select], [tabs]]))
