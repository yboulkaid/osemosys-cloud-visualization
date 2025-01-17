from app.utilities import df_plot, df_filter
import pandas as pd
from app.constants import agg_col
import i18n
import functools


class PowerGenerationCapacityAggregate:

    def __init__(self, all_params, years, plot_title):
        self.all_params = all_params
        self.years = years
        self.plot_title = plot_title
        self.index_column = 'y'

    def figure(self):
        return df_plot(self.data(), i18n.t('label.gigawatts_gw'), self.plot_title)

    @functools.lru_cache()
    def data(self):
        cap_agg_df = pd.DataFrame(columns=agg_col)
        cap_agg_df.insert(0, 'y', self.__cap_df()['y'])
        cap_agg_df = cap_agg_df.fillna(0.00)

        for each in agg_col:
            for tech_exists in agg_col[each]:
                if tech_exists in self.__cap_df().columns:
                    cap_agg_df[each] = cap_agg_df[each] + self.__cap_df()[tech_exists]
                    cap_agg_df[each] = cap_agg_df[each].round(2)

        cap_agg_df = cap_agg_df.loc[:, (cap_agg_df != 0).any(axis=0)]
        return cap_agg_df

    def __cap_df(self):
        total_capacity_annual_params = self.all_params['TotalCapacityAnnual']
        cap_df = total_capacity_annual_params[total_capacity_annual_params.t.str.startswith('PWR')]\
            .drop('r', axis=1)
        return df_filter(cap_df, 3, 6, ['CNT', 'TRN', 'DIS', 'CST', 'CEN', 'SOU', 'NOR'], self.years)
