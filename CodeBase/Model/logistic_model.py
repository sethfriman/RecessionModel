# This file will contain a class that represents the logistic regression model

# import machine learning packages
import numpy as np
import pandas as pd
from matplotlib import pyplot as plt
from sklearn.linear_model import LogisticRegression
from sklearn.model_selection import train_test_split
from sklearn.ensemble import RandomForestClassifier
from sklearn import preprocessing
from sklearn import metrics
from scipy.stats import ttest_ind
from CodeBase.Data import get_data


class RINYModel:

    def __init__(self, total_data=None):
        if total_data is None:
            self.total_data = get_data.get_total_table()
        else:
            self.total_data = total_data
        self.riny_columns = ['date', 'housing_climb_change', '36_mo_cpi_change_all',
                             'yield_diff', 'yield_below_zero', 'years_since_recession', 'years_until_recession',
                             'recession_in_next_year']
        self.riny_df = self.total_data[(self.total_data['in_recession'] == 0) &
                                       (~self.total_data['years_until_recession'].isnull())]
        self.riny_df = self.riny_df[self.riny_columns]
        self.sig_features = self.find_sig_features()
        self.X = self.riny_df.loc[:, self.riny_df.columns.isin(self.sig_features)]
        self.y = self.riny_df.loc[:, self.riny_df.columns == 'recession_in_next_year']
        self.X_train, self.X_test, self.y_train, self.y_test = train_test_split(self.X, self.y, test_size=0.3)
        self.scaler = preprocessing.StandardScaler().fit(self.X_train)
        X_scaled = self.scaler.transform(self.X_train)
        self.X_scaled = pd.DataFrame(data=X_scaled, columns=self.X_train.columns)
        self.logreg = self.fit_model(self.X_scaled, self.y_train)

    def find_sig_features(self):
        sig_features = []
        non_sig_features = []

        for feature in self.riny_df.loc[:,
                       ~self.riny_df.columns.isin(['date', 'recession_in_next_year', 'years_until_recession'])].columns:
            test_sample1 = self.riny_df[self.riny_df['recession_in_next_year'] == 1][feature]
            test_sample2 = self.riny_df[self.riny_df['recession_in_next_year'] == 0][feature]
            t_stat = ttest_ind(test_sample1, test_sample2, equal_var=False)
            if t_stat.pvalue < 0.05:
                sig_features.append(feature)
            else:
                non_sig_features.append(feature)

        return sig_features

    def plot_cov(self):
        return pd.DataFrame.cov(self.riny_df[self.sig_features])

    def retrain_model(self):
        self.X_train, self.X_test, self.y_train, self.y_test = train_test_split(self.X, self.y, test_size=0.3)
        self.logreg = self.fit_model()

    def rfc_model(self):
        rfc = RandomForestClassifier(n_estimators=500, n_jobs=-1)
        rfc.fit(self.X_train, self.y_train)

        importances = rfc.feature_importances_
        indices = np.argsort(importances)

        plt.figure(figsize=(10, 15))
        plt.title('Feature Importances, Score: ' + rfc.score(self.X_test, self.y_test))
        plt.barh(range(len(indices)), importances[indices], color='b', align='center')
        plt.yticks(range(len(indices)), [self.sig_features[i] for i in indices])
        plt.xlabel('Relative Importance')
        plt.show()

    def fit_model(self):
        logreg = LogisticRegression(class_weight='balanced')
        logreg.fit(self.X_scaled, self.y_train)
        return logreg

    def get_coefs(self):
        # Print coefficients for the model (based on standardized variables)
        coefs_df = pd.DataFrame()
        coefs_df['Feature'] = self.logreg.feature_names_in_
        coefs_df['Coefficient'] = self.logreg.coef_[0]
        coefs_df.reindex(coefs_df.Coefficient.abs().sort_values(ascending=False).index)
        return coefs_df

    def get_scores(self):
        test_accuracy = round(self.logreg.score(self.scaler.transform(self.X_test), self.y_test), 3)
        train_accuracy = round(self.logreg.score(self.X_scaled, self.y_train), 3)
        return test_accuracy, train_accuracy

    def get_confusion_matrix(self):
        y_pred = self.logreg.predict(self.scaler.transform(self.X_test))
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
        present_data['riny_pred_bin'] = self.logreg.predict(self.scaler.transform(present_data[self.sig_features]))
        prob_preds = self.logreg.predict_proba(self.scaler.transform(present_data[self.sig_features]))
        present_data['riny_pred_prob'] = [pred[1] for pred in prob_preds]
        return present_data

    def get_preds_table(self):
        # Makes a prediction for all entries in the table based on the model
        preds_table = self.total_data.copy()
        preds_table = preds_table[preds_table['in_recession'] == 0]
        log_preds = self.logreg.predict(self.scaler.transform(preds_table[self.sig_features]))
        prob_preds = self.logreg.predict_proba(self.scaler.transform(preds_table[self.sig_features]))
        prob_preds = [pred[1] for pred in prob_preds]
        preds_table['riny_pred_bin'] = log_preds
        preds_table['riny_pred_prob'] = prob_preds
        preds_table = preds_table[['date', 'recession_in_next_year', 'riny_pred_bin', 'riny_pred_prob']]
        return preds_table

    def get_train_indices(self):
        return list(self.X_train.index)
