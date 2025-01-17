from app.utilities import df_plot, df_filter
import i18n
import functools


class PowerGenerationCapacity:

    def __init__(self, all_params, years, plot_title):
        self.all_params = all_params
        self.years = years
        self.plot_title = plot_title
        self.index_column = 'y'

    def figure(self):
        return self.plot(self.data(), self.plot_title)

    def plot(self, data, title):
        return df_plot(data, i18n.t('label.gigawatts_gw'), title)

    @functools.lru_cache()
    def data(self):
        total_capacity_annual_params = self.all_params['TotalCapacityAnnual']
        cap_df = total_capacity_annual_params[total_capacity_annual_params.t.str.startswith('PWR')]\
            .drop('r', axis=1)
        return df_filter(cap_df, 3, 6, ['CNT', 'TRN', 'DIS', 'CST', 'CEN', 'SOU', 'NOR'], self.years)
