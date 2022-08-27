# This file will contain a class that represents the RINY model

# import machine learning packages
import pandas as pd
from sklearn.model_selection import train_test_split
from sklearn import metrics
from autogluon.tabular import TabularPredictor


class RINYModel:

    def __init__(self, total_data, model=None):
        self.total_data = total_data
        self.riny_columns = ['date', 'housing_climb_change', '36_mo_cpi_change_all', 'un_rate',
                             'yield_diff', 'yield_below_zero',
                             'years_since_recession', 'years_until_recession',
                             'recession_in_next_year']
        self.riny_df = self.total_data[~self.total_data['years_until_recession'].isnull()]
        self.riny_df = self.riny_df[self.riny_columns]

        self.X = self.riny_df[['housing_climb_change', '36_mo_cpi_change_all', 'un_rate',
                               'yield_diff', 'yield_below_zero',
                               'years_since_recession']]
        self.y = self.riny_df[['recession_in_next_year']]
        self.X_train, self.X_test, self.y_train, self.y_test = self.train_test()
        if model is None:
            self.logreg = self.fit_model()
        else:
            self.logreg = model

    def train_test(self):
        return train_test_split(self.X, self.y)

    def retrain_model(self):
        self.X_train, self.X_test, self.y_train, self.y_test = train_test_split(self.X, self.y)
        self.logreg = self.fit_model()

    def fit_model(self):
        logreg = TabularPredictor(label='recession_in_next_year').fit(
                                  train_data=self.X_train, presets='best_quality')
        return logreg

    def get_scores(self):
        test_accuracy = self.logreg.evaluate(self.X_train)['f1']
        train_accuracy = self.logreg.evaluate(self.X_test)['f1']
        return test_accuracy, train_accuracy

    def get_confusion_matrix(self):
        y_pred = self.logreg.predict(self.X_test)
        tn, fp, fn, tp = metrics.confusion_matrix(self.y_test, y_pred).ravel()
        print('--Confusion Matrix--')
        print('True Positives: ', tp)
        print('False Positives: ', fp)
        print('True Negatives: ', tn)
        print('False Negatives: ', fn)
        return tp, fp, tn, fn

    def get_present_data(self):
        # Predictions for the most recent year
        present_data = self.total_data[(self.total_data['recession_in_next_year'].isnull())]
        present_data['riny_pred_bin'] = self.logreg.predict(present_data)
        prob_preds = self.logreg.predict_proba(present_data)
        present_data['riny_pred_prob'] = prob_preds[1].values
        return present_data[['date', 'riny_pred_bin', 'riny_pred_prob']]

    def get_preds_table(self):
        # Makes a prediction for all entries in the table based on the model
        preds_table = self.total_data.copy()
        log_preds = self.logreg.predict(preds_table)
        prob_preds = self.logreg.predict_proba(preds_table)
        prob_preds = prob_preds[1].values
        preds_table['riny_pred_bin'] = log_preds
        preds_table['riny_pred_prob'] = prob_preds
        preds_table = preds_table[['date', 'recession_in_next_year', 'riny_pred_bin', 'riny_pred_prob']]
        return preds_table

    def get_train_indices(self):
        return list(self.X_train.index)

    def get_test_indices(self):
        return list(self.X_test.index)

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
        pred = self.logreg.predict_proba(pd.DataFrame(pred_dict))
        return round(pred.iloc[0][1], 3)
