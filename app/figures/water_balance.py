from app.utilities import df_plot, df_filter
from app.constants import det_col, color_dict
import pandas as pd


class WaterBalance:

    def __init__(self, all_params, years, plot_title):
        self.all_params = all_params
        self.years = years
        self.plot_title = plot_title

    def figure(self):
        wat_bal_df = self.__calculate_wat_bal_df()
        return wat_bal_df.iplot(asFigure=True,
                                x='y',
                                kind='bar',
                                barmode='relative',
                                xTitle='Year',
                                yTitle='Billion m3',
                                color=[color_dict[x] for x in wat_bal_df.columns if x != 'y'],
                                title=self.plot_title,
                                showlegend=True,
                                )

    def __calculate_wat_bal_df(self):
        production_by_technology_annual = self.all_params['ProductionByTechnologyAnnual']
        wat_bal_df = production_by_technology_annual[
            production_by_technology_annual.f.str.startswith('WTR')
            ].drop('r', axis=1)
        wat_bal_df['f'] = wat_bal_df['f'].str[3:6]
        wat_bal_df['value'] = wat_bal_df['value'].astype('float64')
        wat_bal_df = wat_bal_df.pivot_table(index='y',
                                            columns='f',
                                            values='value',
                                            aggfunc='sum').reset_index().fillna(0)
        wat_bal_df = (wat_bal_df.reindex(sorted(wat_bal_df.columns), axis=1)
                                .set_index('y')
                                .reset_index()
                                .rename(columns=det_col))
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
                                .rename(columns=det_col))
        wat_bal_df['Irrigation'] = wat_dem_df['Agriculture']
        wat_bal_df['y'] = self.years
        for each in wat_bal_df.columns:
            if each in ['Evapotranspiration', 'Groundwater recharge', 'Surface water run-off']:
                wat_bal_df[each] = wat_bal_df[each].mul(-1)
        return wat_bal_df