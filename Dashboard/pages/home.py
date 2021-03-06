import pickle
import dash
import pandas as pd
from dash import html, dcc, callback, Input, Output, dash_table
import datetime
from CodeBase.Data.data_viz import Visualizer
from CodeBase.Model.logistic_model import RINYModel
from CodeBase.Model.linear_model import YURModel

dash.register_page(__name__, path='/')

vis = Visualizer(df=pd.read_csv('CodeBase/Data/total_data.csv', index_col=0))

riny_model = pickle.load(open('CodeBase/Model/saved_models/riny_model.sav', 'rb'))
riny_scaler = pickle.load(open('CodeBase/Model/saved_models/riny_scaler.sav', 'rb'))
riny = RINYModel(vis.total_data, model=riny_model, scaler=riny_scaler)

yur_model = pickle.load(open('CodeBase/Model/saved_models/yur_model.sav', 'rb'))
yur_scaler = pickle.load(open('CodeBase/Model/saved_models/yur_scaler.sav', 'rb'))
yur = YURModel(vis.total_data, train_indices=riny.get_train_indices(),
               test_indices=riny.get_test_indices(), model=yur_model, scaler=yur_scaler)

available_years = list(vis.total_data.date.values)
available_years = list(set([datetime.datetime.strptime(x, '%Y-%m-%d').year for x in available_years]))

fig = vis.makePlot(['yield_diff', '36_mo_cpi_change_all'])

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

log_pred = riny.make_pred(0, 0, 0, 0)
lin_pred = yur.make_pred(0, 0, 0, 0)
if riny_rec_val < 0.5:
    likelihood_string = 'low'
elif yur_rec_val <= 1:
    likelihood_string = 'high'
elif riny_rec_val < 0.92:
    likelihood_string = 'possible'
else:
    likelihood_string = 'high'

most_recent_data = vis.total_data.iloc[-1]

layout = html.Div(
    [
        dcc.Markdown('For variable descriptions click [here](/data-description)', style={"margin-top": "8%"}),
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
                            persistence=True
                        )
                    ], style={"width": '25%', 'zIndex': 2147483647}
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
                            className="dropdown",
                            persistence=True
                        )
                    ], style={"width": '25%', 'zIndex': 2147483647}
                ),
                html.Div(
                    [
                        html.H2("Latest Predictions",
                                style={"text-decoration": "underline", "textAlign": "center"}),
                        html.H4("Logistic Predicts Recession Starting:", style={"textAlign": "center"}),
                        html.H3(riny_rec_pred, style={"textAlign": "center"}),
                        html.Br(),
                        html.H4("Linear Predicts Recession Starting:", style={"textAlign": "center"}),
                        html.H3(yur_rec_pred, style={"textAlign": "center"}),
                    ], style={"margin-left": "0.5%", "border": "2px black solid", "margin-top": "-17%"}
                ),
                html.Div(
                    [
                        html.H2("Main Takeaways / Usability", style={"text-decoration": "underline",
                                                                     "textAlign": "center"}),
                        dcc.Markdown('''
                            - If the logistic model says there will not be a recession in the next year, there probably won't be 
                            - If there is a recession in the next year, the logistic model will most likely spot it 
                            - Pay close attention to economy if logistic model prob hits 0.9 or higher 
                            - If the linear model model predicts less than a year, there will most likely be a recession 
    
                            *Current scores indicate a **''' + likelihood_string + '''** likelihood of a recession 
                            within the next year*
                        '''),
                    ], style={"margin-left": "0.5%", "border": "2px black solid", "width": '30%', "margin-top": "-17%"}
                ),
            ],
            className="row",
            style={"display": 'flex'}
        ),
        dcc.Checklist([{"label": 'Include Data During Recessions ' +
                                 '(Notes: Model does not look at this data, line plots include this data regardless)',
                        "value": 1}],
                      id='recession-checklist', style={"zIndex": 2147483648, "margin-bottom": "2%"},
                      persistence=True),
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
                    ], style={"width": '55%'}
                ),
                dcc.Markdown('''
                    # Summary 
                    ##### Note: Values below will change as the model is run, these are not dynamic so they will not \
                    update with each run. Treat as approximates 

                    **These are just notes made from an observation of the model. They are in no way to 
                    be used to make financial decisions and should not be considered advice** 

                    ## Logistic Model 
                    - Accurate about 87% (140/167) of the time on new data 
                    - When predicting a recession will occur, accurate about 56% (22/39) of the time on new data 
                    - When predicting a recession will not occur, accurate about 97% (118/122) of the time on new data 
                    - When predicting a recession will occur, recession is median 0.9 years away 
                    - When _incorrectly_ predicting a recession will occur, recession is median 1.6 years away 
                    - When there is a recession in the next year, the model will identify it 94% (66/70) of the time 
                    - If the model gives a 0.9 probability or higher of a recession, accurate about 75% (16/20) of the 
                    time 

                    ## Linear Model 
                    - Scores about a 65% on the test data 
                    - When predicting recession in <= 1 years, accurate about 89% (51/57) of the time on new data 
                    - Median difference between years until recession and predicted is -0.55 (model tends to 
                    overestimate distance) 
                    - Mean difference between years until recession and predicted is -0.29 (model tends to overestimate 
                    distance) 


                    ## Combined Uses 
                    - When linear predicting recession in <= 1 year and prob >= 0.5, accurate about 89% (51/57) of the 
                    time on new data 
                    - When linear predicting recession in <= 1 year and prob >= 0.8, accurate about 88% (46/52) of the 
                    time on new data 
                    - When linear predicting recession in <= 1 year and prob >= 0.9, accurate about 86% (37/43) of the 
                    time on new data 
                    - When linear predicting recession in <= 1 year and prob >= 0.95, accurate about 93% (26/28) of the 
                    time on new data 
                    - When the logistic model predicts a recession, the linear model agrees just 37% (57/153) of the 
                    time on new data''', style={"border": "2px black solid"})
            ], style={"display": 'flex', "margin-top": "5%"}
        ),
        html.Div(
            [
                html.H2("Model Calculator", style={"text-decoration": "underline", "margin-left": "1%"}),
                dcc.Markdown("#### Customize the boxes below to see how the model operates. Have some fun with it! ["
                             "Data Descriptions](/data-description)",
                             style={"margin-left": "1%"}),
                html.Div(
                    [
                        html.Label('1 Year Housing Climb Change',
                                   style={"font-size": "12px", "margin-left": "7%"}),
                        html.Label('3 Year CPI Change', style={"font-size": "12px", "margin-left": "5.5%"}),
                        html.Label('Yield Curve Difference', style={"font-size": "12px", "margin-left": "8%"}),
                        html.Label('Years Since Recession', style={"font-size": "12px", "margin-left": "7%"})
                    ], style={"verticalAlign": "middle"}
                ),
                html.Div(
                    [
                        dcc.Input(id='housing-change-input', type="number", value=0,
                                  style={"width": "7%", "margin-left": "14%"}, persistence=True),
                        dcc.Input(id='cpi-change-input', type="number", value=0,
                                  style={"width": "7%", "margin-left": "14%"}, persistence=True),
                        dcc.Input(id='yield-diff', type="number", value=0,
                                  style={"width": "7%", "margin-left": "14%"}, persistence=True),
                        dcc.Input(id='years-since-recession', type="number", value=0,
                                  style={"width": "7%", "margin-left": "14%"}, persistence=True)
                    ], style={"verticalAlign": "middle"}
                ),
                html.Div(
                    [
                        html.Label('Current Value: ' + str(round(most_recent_data['housing_climb_change'], 3)),
                                   style={"font-size": "12px", "margin-left": "11%"}),
                        html.Label('Current Value: ' + str(round(most_recent_data['36_mo_cpi_change_all'], 3)),
                                   style={"font-size": "12px", "margin-left": "8%"}),
                        html.Label('Current Value: ' + str(round(most_recent_data['yield_diff'], 3)),
                                   style={"font-size": "12px", "margin-left": "8%"}),
                        html.Label('Current Value: ' + str(round(most_recent_data['years_since_recession'], 3)),
                                   style={"font-size": "12px", "margin-left": "8%"})
                    ], style={"verticalAlign": "middle"}
                ),
                html.H3(id="log-pred", style={"margin-left": "1%"}),
                html.H3(id="lin-pred", style={"margin-left": "1%"}),
            ], style={"border": "2px black solid",
                      "margin-top": "-21%",
                      "width": "50%",
                      "margin-left": "1%"}
        ),
        html.Div(
            [
                html.H2("Credits", style={"text-decoration": "underline", "margin-left": "1%"}),
                dcc.Markdown("""
                    Data is obtained from a combination of [St. Louis Federal Reserve of Economic Data 
                    (FRED)](https://fred.stlouisfed.org/), the [List of recessions in the United States]( 
                    https://en.wikipedia.org/wiki/List_of_recessions_in_the_United_States) Wikipedia page, 
                    and [multpl.com](https://www.multpl.com/s-p-500-historical-prices/table/by-month). 
    
                    Data shown here was often aggregated or calculated for use in the model and may not 
                    be a direct representation of the source it was pulled from. 
    
                    I would also like to acknowledge the mortada [fredapi](
                    https://github.com/mortada/fredapi) package for allowing simple retrievals of some 
                    FRED data.""")
            ], style={"border": "2px black solid",
                      "margin-top": "1%",
                      "width": "50%",
                      "margin-left": "1%",
                      "margin-bottom": "1%"},
        ),
    ]
)


@callback(
    Output("variable-plot", "figure"),
    Input("variable-dropdown", "value"),
    Input("x-dropdown", "value"),
    Input("year-range-slider", "value"),
    Input("recession-checklist", "value")
)
def update_figure(variables, x, year_range, in_rec):
    if len(variables) == 0:
        fig = vis.scatPlot(variables, x, start_date=str(year_range[0]) + '-01-01',
                           end_date=str(year_range[1]) + '-12-01', in_rec=in_rec)
    elif (len(variables) == 1) & (variables[0] == x):  # if one variable --> 1 var histogram
        fig = vis.soloHist(x, start_date=str(year_range[0]) + '-01-01',
                           end_date=str(year_range[1]) + '-12-01', in_rec=in_rec)
    elif x == 'date':  # if date is on x --> line plot
        fig = vis.makePlot(variables, x=x, start_date=str(year_range[0]) + '-01-01',
                           end_date=str(year_range[1]) + '-12-01')
    elif (((vis.total_data[x].values == 0) | (vis.total_data[x].values == 1) |
           (vis.total_data[x].values != vis.total_data[x].values)).all()):
        # if binary x and one y
        fig = vis.histPlot(variables, x, start_date=str(year_range[0]) + '-01-01',
                           end_date=str(year_range[1]) + '-12-01', in_rec=in_rec)

    else:
        fig = vis.scatPlot(variables, x, start_date=str(year_range[0]) + '-01-01',
                           end_date=str(year_range[1]) + '-12-01', in_rec=in_rec)
    return fig


@callback(
    Output("log-pred", "children"),
    Output("lin-pred", "children"),
    Input("housing-change-input", "value"),
    Input("cpi-change-input", "value"),
    Input("yield-diff", "value"),
    Input("years-since-recession", "value"),
)
def make_preds(house, cpi, yd, ysr):
    if house is None:
        house = 0
    if cpi is None:
        cpi = 0
    if yd is None:
        yd = 0
    if ysr is None:
        ysr = 0
    log_pred = riny.make_pred(house, cpi, yd, ysr)
    lin_pred = yur.make_pred(house, cpi, yd, ysr)
    return 'Probability of Recession: ' + str(log_pred), 'Years Until Recession: ' + str(lin_pred)
