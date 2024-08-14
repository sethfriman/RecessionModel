# import machine learning packages
import pandas as pd
from sklearn.model_selection import train_test_split
from autogluon.tabular import TabularPredictor


class YURModel:

    def __init__(self, total_data, model=None):
        self.total_data = total_data
        self.yur_columns = ['date', 'housing_climb_change', '36_mo_cpi_change_all', 'un_rate',
                            'yield_diff', 'yield_below_zero', 'years_since_recession', 'years_until_recession',
                            'recession_in_next_year']
        self.yur_df = self.total_data[~self.total_data['years_until_recession'].isnull()]
        self.yur_df = self.yur_df[self.yur_columns]
        self.X = self.yur_df[['housing_climb_change', '36_mo_cpi_change_all', 'un_rate',
                               'yield_diff', 'yield_below_zero',
                               'years_since_recession']]
        self.y = self.yur_df[['years_until_recession']]
        self.X_train, self.X_test, self.y_train, self.y_test = self.train_test()
        if model is None:
            self.linreg = self.fit_model()
        else:
            self.linreg = model

    def train_test(self):
        return train_test_split(self.X, self.y)

    def retrain_model(self):
        self.X_train, self.X_test, self.y_train, self.y_test = train_test_split(self.X, self.y)
        self.linreg = self.fit_model()

    def fit_model(self):
        linreg = TabularPredictor(label='recession_in_next_year').fit(train_data=self.X_train,
                                                                      presets='best_quality',
                                                                      hyperparameters={'GBM': {},
                                                                                       'CAT': {},
                                                                                       'RF': {},
                                                                                       'XT': {},
                                                                                       'KNN': {}})
        return linreg

    def get_scores(self):
        test_accuracy = self.linreg.evaluate(self.X_train)['r2']
        train_accuracy = self.linreg.evaluate(self.X_test)['r2']
        return test_accuracy, train_accuracy

    def get_present_data(self):
        # Predictions for the most recent year
        present_data = self.total_data[self.total_data['recession_in_next_year'].isnull()].copy()
        present_data.loc[:, 'yur_pred'] = self.linreg.predict(present_data)
        return present_data[['date', 'yur_pred']]

    def get_preds_table(self, preds_df=None):
        # Makes a prediction for all entries in the table based on the model
        if preds_df is None:
            preds_table = self.total_data.copy()
            preds_table = preds_table[preds_table['in_recession'] == 0]
            lin_preds = self.linreg.predict(preds_table)
            preds_table['yur_pred'] = lin_preds
            preds_table = preds_table[['date', 'recession_in_next_year', 'years_until_recession', 'yur_pred']]
            return preds_table
        else:
            preds_table = self.total_data.copy()
            lin_preds = self.linreg.predict(preds_table)
            preds_table['yur_pred'] = lin_preds
            preds_table = preds_table[['date', 'recession_in_next_year', 'years_until_recession', 'yur_pred']]
            preds_df = preds_df.merge(preds_table, on=['date', 'recession_in_next_year'], how='inner')
            return preds_df

    def make_pred(self, house=0, cpi=0, yd=0, ysr=0, un=0):
        if house == float('NaN'):
            house = 0
        if cpi == float('NaN'):
            cpi = 0
        if yd == float('NaN'):
            yd = 0
        if ysr == float('NaN'):
            ysr = 0
        if un == float('NaN'):
            un = 0
        pred_dict = {'un_rate': [un],
                     'housing_climb_change': [house],
                     '36_mo_cpi_change_all': [cpi],
                     'yield_diff': [yd],
                     'yield_below_zero': [int(yd < 0)],
                     'years_since_recession': [ysr]}
        pred = self.linreg.predict(pd.DataFrame(pred_dict))
        return round(pred[0], 3)
