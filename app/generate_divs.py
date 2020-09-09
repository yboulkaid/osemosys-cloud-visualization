from collections import defaultdict
from app.generate_figures import GenerateFigures
from app.layout.checkboxes import Checkboxes
import functools
import os
import pandas as pd
import dash_core_components as dcc
import dash_html_components as html
pd.set_option('mode.chained_assignment', None)


class GenerateDivs:
    def __init__(self, configs):
        self.configs = configs
        self.ids_by_category = self.__ids_by_category()
        self.figures_by_category = self.__figures_by_category()

    def generate_divs(self):
        return [
                dcc.Loading(html.Div([
                    Checkboxes(self.__all_ids(), 'All').to_component(),
                    html.Div([figure.to_div() for figure in self.__all_figure_sets()])
                ]), fullscreen=True),
                html.Div([
                    Checkboxes(self.ids_by_category['Climate'], 'Climate').to_component(),
                    html.Div([figure.to_div() for figure in self.figures_by_category['Climate']])
                ]),
                html.Div([
                    Checkboxes(self.ids_by_category['Land'], 'Land').to_component(),
                    html.Div([figure.to_div() for figure in self.figures_by_category['Land']])
                ]),
                html.Div([
                    Checkboxes(self.ids_by_category['Energy'], 'Energy').to_component(),
                    html.Div([figure.to_div() for figure in self.figures_by_category['Energy']])
                ]),
                html.Div([
                    Checkboxes(self.ids_by_category['Water'], 'Water').to_component(),
                    html.Div([figure.to_div() for figure in self.figures_by_category['Water']])
                ]),
            ]

    def __all_ids(self):
        return [figure.id for figure in self.__all_figure_sets()]

    @functools.lru_cache(maxsize=128)
    def __all_figure_sets(self):
        return GenerateFigures(self.configs).all_figure_sets()

    def __ids_by_category(self):
        grouped = defaultdict(lambda: [])
        for dash_figure_set in self.__all_figure_sets():
            grouped[dash_figure_set.category].append(dash_figure_set.id)
        return grouped

    def __figures_by_category(self):
        grouped = defaultdict(lambda: [])
        for dash_figure_set in self.__all_figure_sets():
            grouped[dash_figure_set.category].append(dash_figure_set)
        return grouped
