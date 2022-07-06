# This file will be where the dashboard is deployed from
import argparse
import os
import pickle
import warnings

warnings.filterwarnings("ignore")
import dash
from dash import dcc
from dash import html
from dash import dash_table
import sys
import pandas as pd
from dash.dependencies import Input, Output
import datetime

sys.path.append("../")
from CodeBase.Data.data_viz import Visualizer
from CodeBase.Model.logistic_model import RINYModel
from CodeBase.Model.linear_model import YURModel

app = dash.Dash()
vis = Visualizer(df=pd.read_csv('total_data.csv', index_col=0))
# vis.total_data.to_csv('total_data.csv')

available_years = list(vis.total_data.date.values)
available_years = list(set([datetime.datetime.strptime(x, '%Y-%m-%d').year for x in available_years]))

fig = vis.makePlot(['yield_diff', '36_mo_cpi_change_all'])

if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument('-r', '--rinymodel', default='load',
                        help='load or create. load riny model or create a new instance. '
                             'Create overwrites an existing model and saves the new instance')
    parser.add_argument('-y', '--yurmodel', default='load',
                        help='load or create. load yur model or create a new instance. '
                             'Create overwrites an existing model and saves the new instance')
    args = parser.parse_args()

    if args.rinymodel == 'load':
        try:
            riny_model = pickle.load(open('../CodeBase/Model/saved_models/riny_model.sav', 'rb'))
            riny_scaler = pickle.load(open('../CodeBase/Model/saved_models/riny_scaler.sav', 'rb'))
            riny = RINYModel(vis.total_data, model=riny_model, scaler=riny_scaler)
        except FileNotFoundError:
            print('Could not load RINY model, creating new one')
            riny = RINYModel(vis.total_data)
            pickle.dump(riny.logreg, open('../CodeBase/Model/saved_models/riny_model.sav', 'wb'))
            pickle.dump(riny.scaler, open('../CodeBase/Model/saved_models/riny_scaler.sav', 'wb'))
    else:
        riny = RINYModel(vis.total_data)
        pickle.dump(riny.logreg, open('../CodeBase/Model/saved_models/riny_model.sav', 'wb'))
        pickle.dump(riny.scaler, open('../CodeBase/Model/saved_models/riny_scaler.sav', 'wb'))

    if args.yurmodel == 'load':
        try:
            yur_model = pickle.load(open('../CodeBase/Model/saved_models/yur_model.sav', 'rb'))
            yur_scaler = pickle.load(open('../CodeBase/Model/saved_models/yur_scaler.sav', 'rb'))
            yur = YURModel(vis.total_data, train_indices=riny.get_train_indices(),
                           test_indices=riny.get_test_indices(), model=yur_model, scaler=yur_scaler)
        except FileNotFoundError:
            print('Could not load YUR model, creating new one')
            yur = YURModel(vis.total_data, train_indices=riny.get_train_indices(),
                           test_indices=riny.get_test_indices())
            pickle.dump(yur.linreg, open('../CodeBase/Model/saved_models/yur_model.sav', 'wb'))
            pickle.dump(yur.scaler, open('../CodeBase/Model/saved_models/yur_scaler.sav', 'wb'))
    else:
        yur = YURModel(vis.total_data, train_indices=riny.get_train_indices(),
                       test_indices=riny.get_test_indices())
        pickle.dump(yur.linreg, open('../CodeBase/Model/saved_models/yur_model.sav', 'wb'))
        pickle.dump(yur.scaler, open('../CodeBase/Model/saved_models/yur_scaler.sav', 'wb'))

    riny_preds = riny.get_present_data()
    yur_preds = yur.get_present_data()
    total_preds = riny_preds.merge(yur_preds, how='inner', on='date')
    total_preds.columns = ['Date', 'Recession in Next Year Binary',
                           'Recession in Next Year Probability', 'Years Until Recession']
    total_preds['Recession in Next Year Probability'] = round(total_preds['Recession in Next Year Probability'], 3)
    total_preds['Years Until Recession'] = round(total_preds['Years Until Recession'], 3)

    riny_last_date, riny_rec_val = (total_preds.iloc[-1]['Date'],
                                    total_preds.iloc[-1]['Recession in Next Year Probability'])
    riny_rec_pred = (datetime.datetime.strptime(riny_last_date, '%Y-%m-%d') +
                     datetime.timedelta(int(365 * (1 / riny_rec_val)))).strftime('%Y-%m-%d')

    yur_last_date, yur_rec_val = (total_preds.iloc[-1]['Date'],
                                  total_preds.iloc[-1]['Years Until Recession'])
    yur_rec_pred = (datetime.datetime.strptime(yur_last_date, '%Y-%m-%d') +
                    datetime.timedelta(int(365 * yur_rec_val))).strftime('%Y-%m-%d')

    if riny_rec_val < 0.5:
        likelihood_string = 'low'
    elif yur_rec_val <= 1:
        likelihood_string = 'high'
    elif riny_rec_val < 0.92:
        likelihood_string = 'possible'
    else:
        likelihood_string = 'high'

    app.layout = html.Div(
        [
            html.H1("Recession Tracker Dashboard"),
            html.H3('Created By: Seth Friman'),
            html.H4('Beta Version'),
            html.Div(
                [
                    html.Div(
                        [
                            html.Label("Values to Plot"),
                            dcc.Dropdown(
                                id="variable-dropdown",
                                options=[
                                    {"label": s.replace("_", " ").title(), "value": s} for s in
                                    list(vis.total_data.columns)
                                ],
                                className="dropdown",
                                value=['yield_diff', '36_mo_cpi_change_all'],
                                multi=True,
                            )
                        ], style={"width": '25%', "margin-top": "17%", 'zIndex': 2147483647}
                    ),
                    html.Div(
                        [
                            html.Label("Horizontal Axis Variable"),
                            dcc.Dropdown(
                                id="x-dropdown",
                                options=[
                                    {"label": s.replace("_", " ").title(), "value": s} for s in
                                    list(vis.total_data.columns)
                                ],
                                value='date',
                                className="dropdown"
                            )
                        ], style={"width": '25%', "margin-top": "17%", 'zIndex': 2147483647}
                    ),
                    html.Div(
                        [
                            html.H2("Latest Predictions", style={"text-decoration": "underline", "textAlign": "center"}),
                            html.H4("Logistic Predicts Recession Starting:", style={"textAlign": "center"}),
                            html.H3(riny_rec_pred, style={"textAlign": "center"}),
                            html.Br(),
                            html.H4("Linear Predicts Recession Starting:", style={"textAlign": "center"}),
                            html.H3(yur_rec_pred, style={"textAlign": "center"}),
                        ], style={"margin-left": "0.5%", "border": "2px black solid"}
                    ),
                    html.Div(
                        [
                            html.H2("Main Takeaways / Usability", style={"text-decoration": "underline",
                                                                         "textAlign": "center"}),
                            dcc.Markdown('''
                                - If the logistic model says there will not be a recession in the next year, there won't
                                be
                                - If there is a recession in the next year, the logistic model will most likely spot it
                                - Pay close attention to economy if logistic model prob hits 0.9 or higher
                                - If the linear model model predicts less than a year, there will most likely be a 
                                recession
                                
                                *Current scores indicate a **''' + likelihood_string + '''** likelihood of a recession 
                                within the next year*
                            '''),
                        ], style={"margin-left": "0.5%", "border": "2px black solid", "width": '30%'}
                    ),
                ],
                className="row",
                style={"display": 'flex', "margin-top": "-8%"}
            ),
            dcc.Graph(id='variable-plot', figure=fig, style={"position": "relative", "margin-top": "-2.5%"},
                      config={'displayModeBar': False}),
            dcc.RangeSlider(min(available_years), max(available_years), 1,
                            value=[min(available_years), max(available_years)],
                            marks={year: str(year) for year in range(min(available_years), max(available_years) + 1)},
                            id='year-range-slider'),
            html.Br(),
            html.Div(
                [
                    html.Div(
                        [
                            html.H2("Past Year Predictions"),
                            html.H4("Available as necessary data becomes available"),
                            dash_table.DataTable(total_preds.to_dict('records'),
                                                 [{"name": i, "id": i} for i in total_preds.columns]),
                        ], style=dict(width='55%')
                    ),
                    dcc.Markdown('''
                        # Summary
                        ##### Note: Values below will change as the model is run, these are not dynamic so they will \
                        not update with each run. Treat as approximates
                        
                        **These are just notes made from an observation of the model. They are in no way to be used to 
                        make financial decisions and should not be considered advice**
                        
                        ## Logistic Model
                        - Accurate about 87% (140/167) of the time on new data
                        - When predicting a recession will occur, accurate about 56% (22/39) of the time on new data
                        - When predicting a recession will not occur, accurate about 97% (118/122) of the time on new 
                        data
                        - When predicting a recession will occur, recession is median 0.9 years away
                        - When _incorrectly_ predicting a recession will occur, recession is median 1.6 years away
                        - When there is a recession in the next year, the model will identify it 94% (66/70) of the time 
                        - If the model gives a 0.9 probability or higher of a recession, accurate about 75% (16/20) of 
                        the time
                        
                        ## Linear Model
                        - Scores about a 65% on the test data
                        - When predicting recession in <= 1 years, accurate about 89% (51/57) of the time on new data
                        - Median difference between years until recession and predicted is -0.55 (model tends to 
                        overestimate distance)
                        - Mean difference between years until recession and predicted is -0.29 (model tends to 
                        overestimate distance)
                        
                        
                        ## Combined Uses
                        - When linear predicting recession in <= 1 year and prob >= 0.5, accurate about 89% (51/57) of 
                        the time on new data
                        - When linear predicting recession in <= 1 year and prob >= 0.8, accurate about 88% (46/52) of 
                        the time on new data
                        - When linear predicting recession in <= 1 year and prob >= 0.9, accurate about 86% (37/43) of 
                        the time on new data
                        - When linear predicting recession in <= 1 year and prob >= 0.95, accurate about 93% (26/28) of 
                        the time on new data
                        - When the logistic model predicts a recession, the linear model agrees just 37% (57/153) of the
                         time on new data
                    ''', style={"border": "2px black solid"})
                ], style=dict(display='flex')
            ),
        ],
        className="container",
        style={"background-image": 'url("/assets/stock_background_1.png")',
               'background-size': '100%',
               'width': '100%',
               'height': '100%'}
    )


    @app.callback(
        Output("variable-plot", "figure"),
        Input("variable-dropdown", "value"),
        Input("x-dropdown", "value"),
        Input("year-range-slider", "value"),
    )
    def update_figure(variables, x, year_range):
        fig = vis.makePlot(variables, x=x, start_date=str(year_range[0]) + '-01-01',
                           end_date=str(year_range[1]) + '-12-01')

        return fig


    app.run_server(debug=True, host='127.0.0.1')
