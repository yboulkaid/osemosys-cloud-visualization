from app.utilities import df_plot, df_filter
import app.constants
import i18n
import pandas as pd
import functools


class WaterDemand:

    def __init__(self, all_params, years, plot_title):
        self.all_params = all_params
        self.years = years
        self.plot_title = plot_title
        self.index_column = 'y'

    def figure(self):
        return self.plot(self.data(), self.plot_title)

    def plot(self, data, title):
        return data.iplot(
                asFigure=True,
                x='y',
                kind='bar',
                barmode='stack',
                xTitle=i18n.t('label.year'),
                yTitle=i18n.t('label.billion_m3'),
                color=[app.constants.color_dict[x] for x in data.columns if x != 'y'],
                title=title,
                showlegend=True,
                )

    @functools.lru_cache()
    def data(self):
        wat_dem_df = self.__calculate_wat_dem_df()
        wat_dem_df['y'] = self.years
        return wat_dem_df


    def __calculate_wat_dem_df(self):
        production_by_technology_annual = self.all_params['ProductionByTechnologyAnnual']
        wat_list = ['AGRWAT', 'PUBWAT', 'PWRWAT', 'INDWAT', 'LVSWAT']
        wat_dem_df = production_by_technology_annual[
            production_by_technology_annual.f.str[0:6].isin(wat_list)
        ].drop('r', axis=1)
        wat_dem_df['f'] = wat_dem_df['f'].str[0:3]
        wat_dem_df['value'] = wat_dem_df['value'].astype('float64')
        wat_dem_df = wat_dem_df.pivot_table(index='y',
                                            columns='f',
                                            values='value',
                                            aggfunc='sum').reset_index().fillna(0)
        wat_dem_df = (wat_dem_df.reindex(sorted(wat_dem_df.columns), axis=1)
                                .set_index('y')
                                .reset_index()
                                .rename(columns=app.constants.det_col))
        return wat_dem_df
