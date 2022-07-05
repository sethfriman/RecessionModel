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

    app.layout = html.Div(
        [
            html.H1("Recession Tracker Dashboard"),
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
                        ], style={"width": '25%', "margin-top": "2.5%"}
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
                        ], style={"width": '25%', "margin-top": "2.5%"}
                    ),
                    html.Div(
                        [
                            html.H2("Latest Predictions"),
                            html.H4("Logistic Predicts Recession Starting: " + riny_rec_pred),
                            html.H4("Linear Predicts Recession Starting: " + yur_rec_pred),
                        ], style={"margin-left": "10%"}
                    ),
                ],
                className="row",
                style={"display": 'flex'}
            ),
            dcc.Graph(id='variable-plot', figure=fig, style={"position": "relative", "margin-top": "-5%"}),
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
                ], style=dict(display='flex')
            ),
        ],
        className="container",
        style={"background-image": 'url("/assets/stock_background_1.png")', "background-position": "left top"}
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
