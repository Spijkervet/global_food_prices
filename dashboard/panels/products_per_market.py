import numpy as np

from extended_viz import remove_renderers
from bokeh.models import ColumnDataSource, Panel
from bokeh.plotting import figure
from bokeh.palettes import Dark2_5 as palette

class ProductsPerMarket():

    def __init__(self, df, default_product):
        self.df = df

        # Pre-processing
        avg_price = self.df.groupby(['mkt_name', 'cm_name', 'date'])['mp_price']
        df_means = avg_price.mean().reset_index()
        normalized = df_means.groupby(['mkt_name', 'cm_name'])['mp_price'].apply(lambda x: (x - np.mean(x)) / (np.max(x) - np.min(x)))
        df_means['mp_price_norm'] = normalized
        self.df = df_means.copy()

        self.default_product = default_product

        self.source = self.get_datasource(df, self.default_product)
        self.plot = self.make_plot(self.source, self.default_product)
        self.tab = Panel(child = self.plot, title='Product per Market')

    def get_datasource(self, src, product):
        product_group = src.loc[src['cm_name'] == product]
        return ColumnDataSource(data=product_group)


    def make_plot(self, src, title):
        plot = figure(x_axis_type='datetime')
        plot.title.text = title + " - per Market"
        plot.legend.click_policy = "hide"
        plot.legend.location = "top_left"
        return plot

    def redraw_plot(self, attrname, old, new):
        self.plot.title.text = new  + " - per Market"
        self.plot.legend.click_policy = "hide"
        self.plot.legend.location = "top_left"
        # Remove all renderers.
        remove_renderers(self.plot)
        product_group = self.df.loc[self.df['cm_name'] == new]
        country_group = product_group.groupby(['mkt_name'])
        color_idx = 0
        for group, row in country_group:
            datetime = []
            prices = []
            for i, data in row.iterrows():
                datetime.append(data['date'])
                prices.append(data['mp_price_norm'])
            self.plot.line(datetime, prices, line_width=4, legend=data['mkt_name'], color=palette[color_idx % 5])
            color_idx += 1
