import numpy as np

from extended_viz import remove_renderers
from bokeh.models import ColumnDataSource, Panel
from bokeh.plotting import figure
from bokeh.palettes import Dark2_5 as palette

class ProductsPerCountry():

    def __init__(self, df, default_country):
        self.df = df
        self.default_country = default_country

        # Pre-processing
        # avg_price = self.df.groupby(['sub-region', 'cm_name', 'date'])['mp_price']
        # df_means = avg_price.mean().reset_index()
        # normalized = df_means.groupby(['sub-region', 'cm_name'])['mp_price'].apply(lambda x: (x - np.mean(x)) / (np.max(x) - np.min(x)))
        # df_means['mp_price_norm'] = normalized
        # self.df = df_means.copy()

        self.source = self.get_datasource(self.df, self.default_country)
        self.plot = self.make_plot(self.source, self.default_country)
        self.plot.title.text = self.default_country + " - Product Correlation"
        self.plot.legend.click_policy = "hide"
        self.plot.legend.location = "top_left"

    def get_datasource(self, src, country):
        group = src.loc[src['adm0_name'] == country]
        return ColumnDataSource(data=group)


    def make_plot(self, src, title):
        self.plot = figure(x_axis_type='datetime')
        country_group = self.df.loc[self.df['adm0_name'] == title]
        product_group = country_group.groupby(['cm_name'])

        color_idx = 0
        for group, row in product_group:
            print(group)
            datetime = []
            prices = []
            for i, data in row.iterrows():
                datetime.append(data['date'])
                prices.append(data['mp_price'])
            self.plot.line(datetime, prices, line_width=4, legend=data['cm_name'], color=palette[color_idx % 5])
            color_idx += 1

        return self.plot


    def redraw_plot(self, attrname, old, new):
        self.plot.title.text = new  + " - per sub-region"
        self.plot.legend.click_policy = "hide"
        self.plot.legend.location = "top_left"
        # Remove all renderers.
        remove_renderers(self.plot)
        country_group = self.df.loc[self.df['adm0_name'] == new]
        product_group = country_group.groupby(['cm_name'])

        color_idx = 0
        for group, row in product_group:
            print(group)
            datetime = []
            prices = []
            for i, data in row.iterrows():
                datetime.append(data['date'])
                prices.append(data['mp_price'])
            self.plot.line(datetime, prices, line_width=4, legend=data['cm_name'], color=palette[color_idx % 5])
            color_idx += 1
        return self.plot
