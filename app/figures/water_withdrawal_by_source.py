from app.utilities import df_plot, df_filter
import functools
import i18n


class WaterWithdrawalBySource:

    def __init__(self, all_params, years, plot_title):
        self.all_params = all_params
        self.years = years
        self.plot_title = plot_title
        self.index_column = 'y'

    def figure(self):
        return self.plot(self.data(), self.plot_title)

    def plot(self, data, title):
        return df_plot(data, i18n.t('label.billion_m3'), title)

    @functools.lru_cache()
    def data(self):
        production_by_technology_annual = self.all_params['ProductionByTechnologyAnnual']
        wat_list = ['AGRWAT', 'PUBWAT', 'PWRWAT', 'INDWAT', 'LVSWAT']
        wat_source_df = production_by_technology_annual[
            production_by_technology_annual.f.str[0:6].isin(wat_list)
        ].drop('r', axis=1)
        return df_filter(wat_source_df, 6, 9, [], self.years)
