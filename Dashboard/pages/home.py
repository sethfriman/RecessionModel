import dash
import pandas as pd
from dash import html, dcc, callback, Input, Output, dash_table
import datetime
from CodeBase.Data.data_viz import Visualizer
from CodeBase.Model.logistic_model import RINYModel
from CodeBase.Model.linear_model import YURModel
from autogluon.tabular import TabularPredictor

dash.register_page(__name__, path='/')

total_data=pd.read_csv('/home/recessionmodel/mysite/CodeBase/Data/total_data.csv', index_col=0)

yur_model = TabularPredictor.load("/home/recessionmodel/mysite/CodeBase/Model/saved_models/AutogluonModels/yur_model/")
yur = YURModel(total_data, model=yur_model)

riny_model = TabularPredictor.load("/home/recessionmodel/mysite/CodeBase/Model/saved_models/AutogluonModels/riny_model/")
riny = RINYModel(total_data, model=riny_model)

total_data['YUR_Prediction'] = yur.linreg.predict(total_data)
total_data['RINY_prediction'] = riny.logreg.predict(total_data)
total_data['RINY_prediction_probability'] = riny.logreg.predict_proba(total_data)[1].values

vis = Visualizer(total_data)

available_years = list(vis.total_data.date.values)
available_years = list(set([datetime.datetime.strptime(x, '%Y-%m-%d').year for x in available_years]))

fig = vis.makePlot(['yield_diff', '36_mo_cpi_change_all'])

riny_preds = riny.get_present_data()
yur_preds = yur.get_present_data()
total_preds = riny_preds.merge(yur_preds, how='inner', on='date')
total_preds.columns = ['Date', 'Recession in Next Year Binary',
                       'Recession in Next Year Probability', 'Years Until Recession']
total_preds['Recession in Next Year Probability'] = round(total_preds['Recession in Next Year Probability'], 3)
total_preds['Years Until Recession'] = total_preds['Years Until Recession'].apply(lambda x: float('{:,.3}'.format(x)))

riny_rec_val = total_preds.iloc[-1]['Recession in Next Year Probability']
riny_rec_pred = (datetime.datetime.today() +
                 datetime.timedelta(int(365 * ((1 / riny_rec_val) - 1)))).strftime('%Y-%m-%d')

yur_rec_val = total_preds.iloc[-1]['Years Until Recession']
yur_rec_pred = (datetime.datetime.today() +
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
                        html.H4("RINY Predicts Recession Starting:", style={"textAlign": "center"}),
                        html.H3(riny_rec_pred, style={"textAlign": "center"}),
                        html.Br(),
                        html.H4("YUR Predicts Recession Starting:", style={"textAlign": "center"}),
                        html.H3(yur_rec_pred, style={"textAlign": "center"}),
                    ], style={"margin-left": "0.5%", "border": "2px black solid", "margin-top": "-17%",
                              "width": "250px"}
                ),
                html.Div(
                    [
                        html.H2("What to Know", style={"text-decoration": "underline",
                                                       "textAlign": "center"}),
                        dcc.Markdown('''
                            - The **RINY** (recession in next year) Model predicts whether or not there will be a
                              recession in the next year, and returns a value of either 0 (there will not be) or 1
                              (there will be) as well as the probability of a recession occurring. It has an accuracy
                              score of 98%, a recall score of 95%, a precision score of 98%, and an f1 score of 96%
                              all on new data.
                            - The **YUR** (years until recession) Model predicts the number of years until the start of
                              the next recession. This model has an R2 value of 0.94 on new data.

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
                    ], style={"width": '50%'}
                ),
                html.Div(
                    [
                        html.H2("Model Calculator", style={"text-decoration": "underline", "margin-left": "1%"}),
                        dcc.Markdown("#### Customize the boxes below to see how the model operates. Have some fun with "
                                     "it! [Data Descriptions](/data-description)",
                                     style={"margin-left": "1%"}),
                        html.Div(
                            [
                                html.Label('1 Year Housing Climb Change',
                                           style={"font-size": "12px"}),
                                html.Label('3 Year CPI Change', style={"font-size": "12px", "margin-left": "3.5%"}),
                                html.Label('Yield Curve Difference', style={"font-size": "12px", "margin-left": "5%"}),
                                html.Label('Years Since Recession', style={"font-size": "12px", "margin-left": "4.5%"}),
                                html.Label('Unemployment Rate', style={"font-size": "12px", "margin-left": "5%"})
                            ], style={"verticalAlign": "middle"}
                        ),
                        html.Div(
                            [
                                dcc.Input(id='housing-change-input', type="number", value=0,
                                          style={"width": "7%", "margin-left": "7%"}, persistence=True),
                                dcc.Input(id='cpi-change-input', type="number", value=0,
                                          style={"width": "7%", "margin-left": "11.2%"}, persistence=True),
                                dcc.Input(id='yield-diff', type="number", value=0,
                                          style={"width": "7%", "margin-left": "11.2%"}, persistence=True),
                                dcc.Input(id='years-since-recession', type="number", value=0,
                                          style={"width": "7%", "margin-left": "11.2%"}, persistence=True),
                                dcc.Input(id='un-rate', type="number", value=0,
                                          style={"width": "7%", "margin-left": "11.2%"}, persistence=True)
                            ], style={"verticalAlign": "middle"}
                        ),
                        html.Div(
                            [
                                html.Label('Current Value: ' + str(round(most_recent_data['housing_climb_change'], 3)),
                                           style={"font-size": "12px", "margin-left": "3%"}),
                                html.Label('Current Value: ' + str(round(most_recent_data['36_mo_cpi_change_all'], 3)),
                                           style={"font-size": "12px", "margin-left": "5.5%"}),
                                html.Label('Current Value: ' + str(round(most_recent_data['yield_diff'], 3)),
                                           style={"font-size": "12px", "margin-left": "5.5%"}),
                                html.Label('Current Value: ' + str(round(most_recent_data['years_since_recession'], 3)),
                                           style={"font-size": "12px", "margin-left": "5.5%"}),
                                html.Label('Current Value: ' + str(round(most_recent_data['un_rate'], 3)),
                                           style={"font-size": "12px", "margin-left": "6.5%"})
                            ], style={"verticalAlign": "middle"}
                        ),
                        html.H3(id="log-pred", style={"margin-left": "1%"}),
                        html.H3(id="lin-pred", style={"margin-left": "1%"}),
                    ], style={"border": "2px black solid",
                              "margin-top": "10%",
                              "width": "50%",
                              "margin-left": "1%",
                              "max-width": "720px",
                              "min-width": "720px"}
                ),
            ], style={"display": 'flex', "margin-top": "5%"}
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

                    Crediting the autogluon package with the technology utilized to create these models.

                    I would also like to acknowledge the mortada [fredapi](
                    https://github.com/mortada/fredapi) package for allowing simple retrievals of some
                    FRED data.""", style={"margin-left": "3%"})
            ], style={"border": "2px black solid",
                      "margin-top": "1%",
                      "width": "80%",
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
    Input("un-rate", "value"),
)
def make_preds(house, cpi, yd, ysr, un):
    if house is None:
        house = 0
    if cpi is None:
        cpi = 0
    if yd is None:
        yd = 0
    if ysr is None:
        ysr = 0
    if un is None:
        un = 0
    log_pred = riny.make_pred(house, cpi, yd, ysr, un)
    lin_pred = yur.make_pred(house, cpi, yd, ysr, un)
    return 'Probability of Recession: ' + str(log_pred), 'Years Until Recession: ' + str(lin_pred)
