
from bokeh.models.renderers import GlyphRenderer
def remove_renderers(plot):
    renderers = plot.select(dict(type=GlyphRenderer))
    for r in renderers:
        plot.renderers.remove(r)
        plot.legend[0].items.pop()
