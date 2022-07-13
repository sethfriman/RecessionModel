# import machine learning packages
import numpy as np
import pandas as pd
from sklearn.model_selection import train_test_split
from sklearn.linear_model import LinearRegression
from sklearn import preprocessing
from scipy.stats import ttest_ind


class YURModel:

    def __init__(self, total_data, train_indices=None, test_indices=None, model=None, scaler=None):
        self.total_data = total_data
        self.yur_columns = ['date', 'housing_climb_change', '36_mo_cpi_change_all',
                            'yield_diff', 'yield_below_zero', 'years_since_recession', 'years_until_recession',
                            'recession_in_next_year']
        self.yur_df = self.total_data[(self.total_data['in_recession'] == 0) &
                                      (~self.total_data['years_until_recession'].isnull())]
        self.yur_df = self.yur_df[self.yur_columns]
        self.sig_features = self.find_sig_features()
        self.X = self.yur_df.loc[:, self.yur_df.columns.isin(self.sig_features)]
        self.y = self.yur_df.loc[:, self.yur_df.columns == 'years_until_recession']
        self.X_train, self.X_test, self.y_train, self.y_test = self.train_test(train_indices, test_indices)
        if scaler is None:
            self.scaler = preprocessing.StandardScaler().fit(self.X_train)
        else:
            self.scaler = scaler
        X_scaled = self.scaler.transform(self.X_train)
        self.X_scaled = pd.DataFrame(data=X_scaled, columns=self.X_train.columns)
        if model is None:
            self.linreg = self.fit_model()
        else:
            self.linreg = model

    def find_sig_features(self):
        sig_features = []
        non_sig_features = []

        for feature in self.yur_df.loc[:,
                       ~self.yur_df.columns.isin(['date', 'recession_in_next_year', 'years_until_recession'])].columns:
            test_sample1 = self.yur_df[self.yur_df['recession_in_next_year'] == 1][feature]
            test_sample2 = self.yur_df[self.yur_df['recession_in_next_year'] == 0][feature]
            t_stat = ttest_ind(test_sample1, test_sample2, equal_var=False)
            if t_stat.pvalue < 0.05:
                sig_features.append(feature)
            else:
                non_sig_features.append(feature)

        return sig_features

    def plot_cov(self):
        return pd.DataFrame.cov(self.yur_df[self.sig_features])

    def train_test(self, train_indices=None, test_indices=None):
        if (train_indices is None) | (test_indices is None):
            return train_test_split(self.X, self.y, test_size=0.3)
        else:
            return (self.X.filter(train_indices, axis=0),
                    self.X.filter(test_indices, axis=0),
                    self.y.filter(train_indices, axis=0),
                    self.y.filter(test_indices, axis=0))

    def retrain_model(self, train_indices=None, test_indices=None):
        self.X_train, self.X_test, self.y_train, self.y_test = self.train_test(train_indices, test_indices)
        self.linreg = self.fit_model()

    def fit_model(self):
        linreg = LinearRegression()
        linreg.fit(self.X_scaled, self.y_train)
        return linreg

    def get_coefs(self):
        # Print coefficients for the model (based on standardized variables)
        coefs_df = pd.DataFrame()
        coefs_df['Feature'] = self.linreg.feature_names_in_
        coefs_df['Coefficient'] = self.linreg.coef_[0]
        coefs_df = coefs_df.reindex(coefs_df.Coefficient.abs().sort_values(ascending=False).index)
        return coefs_df

    def get_scores(self):
        test_accuracy = round(self.linreg.score(self.scaler.transform(self.X_test), self.y_test), 3)
        train_accuracy = round(self.linreg.score(self.X_scaled, self.y_train), 3)
        return test_accuracy, train_accuracy

    def get_present_data(self):
        # Predictions for the most recent year
        present_data = self.total_data[(self.total_data['recession_in_next_year'].isnull())]
        present_data['yur_pred'] = self.linreg.predict(self.scaler.transform(present_data[self.sig_features]))
        return present_data[['date', 'yur_pred']]

    def get_preds_table(self, preds_df=None):
        # Makes a prediction for all entries in the table based on the model
        if preds_df is None:
            preds_table = self.total_data.copy()
            preds_table = preds_table[preds_table['in_recession'] == 0]
            lin_preds = self.linreg.predict(self.scaler.transform(preds_table[self.sig_features]))
            preds_table['yur_pred'] = lin_preds
            preds_table = preds_table[['date', 'recession_in_next_year', 'years_until_recession', 'yur_pred']]
            return preds_table
        else:
            preds_table = self.total_data.copy()
            lin_preds = self.linreg.predict(self.scaler.transform(preds_table[self.sig_features]))
            preds_table['yur_pred'] = lin_preds
            preds_table = preds_table[['date', 'recession_in_next_year', 'years_until_recession', 'yur_pred']]
            preds_df = preds_df.merge(preds_table, on=['date', 'recession_in_next_year'], how='inner')
            return preds_df

    def make_pred(self, house=0, cpi=0, yd=0, ysr=0):
        if house == float('NaN'):
            house = 0
        if cpi == float('NaN'):
            house = 0
        if yd == float('NaN'):
            house = 0
        if ysr == float('NaN'):
            house = 0
        pred = self.linreg.predict(self.scaler.transform(np.array([house, cpi, yd, int(yd < 0), ysr]).reshape(1, -1)))
        return round(pred[0][0], 3)
