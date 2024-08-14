import pandas as pd
from sklearn.model_selection import train_test_split #splitting the dataset
from autogluon.tabular import TabularDataset, TabularPredictor #to handle tabular data and train models

# Classification Model
total_data = pd.read_csv('mysite/CodeBase/Data/total_data.csv', index_col=0)
riny_model_data = total_data[(~total_data['recession_in_next_year'].isnull())]
yur_model_data = total_data[(~total_data['years_until_recession'].isnull())]

riny_model_data = riny_model_data[['un_rate','housing_climb_change', '36_mo_cpi_change_all',
                                   'yield_diff', 'yield_below_zero', 'years_since_recession',
                                   'recession_in_next_year']]

riny_train, riny_test = train_test_split(riny_model_data)
riny_test_data = riny_test.drop(['recession_in_next_year'],axis=1)

predictor = TabularPredictor(label='recession_in_next_year',
                             path='mysite/CodeBase/Model/saved_models/AutogluonModels/riny_model').fit(
    train_data = riny_train, presets='best_quality')

print(predictor.fit_summary())

print(predictor.leaderboard(riny_train, silent=True))

print(predictor.feature_importance(data=riny_train))

print(predictor.evaluate(riny_test))


# Linear Model
yur_model_data = yur_model_data[['un_rate','housing_climb_change', '36_mo_cpi_change_all',
                                 'yield_diff', 'yield_below_zero', 'years_since_recession',
                                 'years_until_recession']]

yur_train,yur_test = train_test_split(yur_model_data)
yur_test_data=yur_test.drop(['years_until_recession'],axis=1)
predictor= TabularPredictor(label='years_until_recession',
                            path='mysite/CodeBase/Model/saved_models/AutogluonModels/yur_model').fit(
    train_data = yur_train, presets='best_quality'
)

print(predictor.fit_summary())

print(predictor.leaderboard(yur_train, silent=True))

print(predictor.feature_importance(data=yur_train))

print(predictor.evaluate(yur_test))