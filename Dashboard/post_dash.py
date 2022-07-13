# This file will be where the dashboard is deployed from
import argparse
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

app = dash.Dash(__name__, use_pages=True)
vis = Visualizer(df=pd.read_csv('total_data.csv', index_col=0))
# df=pd.read_csv('total_data.csv', index_col=0)

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

    app.layout = html.Div(
        [
            html.Div(
                [
                    dcc.Link(
                        "Home", href='/', style={"margin-left": "1%", "margin-right": "1%",
                                                     "font-weight": "bold", "color": "white",
                                                     'font-size': "30px", "width": "20%"}
                    ),
                    html.Div(
                        [
                            dcc.Link(
                                f"{page['name']}".title(), href=page["relative_path"],
                                style={"margin-left": "1%", "margin-right": "1%",
                                       "font-weight": "bold", "color": "white",
                                       'font-size': "30px"}
                            ) for page in dash.page_registry.values() if page['name'] != 'Home'
                        ], style={"textAlign": "right", "width": "80%"}
                    )
                ], style={'backgroundColor': 'blue', "display": "flex"}
            ),
            html.H1("Recession Tracker Dashboard", style={"margin-left": "1%"}),
            html.H3('Created By: Seth Friman', style={"margin-left": "1%"}),
            html.H4('Beta Version', style={"margin-left": "1%"}),
            dash.page_container
        ],
        className="container",
        style={"background-image": 'url("/assets/stock_background_1.png")',
               'background-size': '100%',
               'width': '100%',
               'height': '100%',
               "min-width": "1438px",
               "max-width": "1462px"}
    )

    app.run_server(debug=True, host='127.0.0.1')
