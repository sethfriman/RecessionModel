import dash
from dash import html, dcc

dash.register_page(__name__)

layout = html.Div(children=[
    html.H1(children='Data Descriptions', style={"margin-top": "2%", 'margin-left': "2%"}),
    html.H3("""Below are descriptions of the data used in this project. Consult this to better understand what you
    are looking at. The variables at the top are the variables that are used in the models, the variables below are
    either raw values used in creating model variables, or are just interesting values to compare against recession
    periods.""", style={'margin-left': "2%"}),
    html.Div([
        html.H2("Model Variables", style={"text-decoration": "underline", "margin-top": "3%"}),
        dcc.Markdown("**Housing Climb Change**: The change in the percentage median housing price change over 1 year. "
                     "Ex. Consider the housing prices at the beginning of the year from 2000-2002: 2000-$100, "
                     "2001-$110, 2002-$126.5. The pct change from 2000 - 2001 is 10% ((110 - 100) / 100), "
                     "and the percentage change from 2001 - 2002 is 15% ((126.5 - 110) / 110). The 2002 Housing Climb "
                     "Change is then the current percentage change less the percentage change from the year before: "
                     "15-10 = 5. The hypothesis is that a sudden spike in the rate that housing prices are increasing "
                     "is an indication of a recession."),
        dcc.Markdown("**36 Mo Cpi Change All (36 Month Change in Cpi Change All)**: The difference in yearly percentage "
                     "change in CPI over a 36 month period. Ex. If the yearly percentage change in CPI in Jan 2000 was a "
                     "10% increase, and the yearly percentage change in CPI in Jan 2003 was 5%, the 36 month CPI Change "
                     "All would be 5-10 = -5. The hypothesis is that a sudden spike in the rate that CPI is increasing "
                     "is an indication of a recession."),
        dcc.Markdown("**Un Rate (Unemployment Rate)**: The percentage of people in the workforce that are unable to find "
                     "employment"),
        dcc.Markdown("**Yield Diff**: The difference between the 10 Year Yield Rate and the 1 Year Yield Rate. Ex. If at "
                     "the current point in time the 10 Year Yield Rate 5% and the 1 Yer Yield Rate is 6%, the Yield Diff "
                     "would be 5-6 = -1. The hypothesis is that as the yield difference gets smaller, confidence in the "
                     "far future is less certain than the nearer future, and if the short term yield is better than the "
                     "long term yield, a recession is likely. This is a strong indicator in both models."),
        dcc.Markdown("**Yield Below Zero**: Returns 1 if Yield Diff is less than 0, 0 otherwise. The hypothesis is that "
                     "when an inverted yield curve appears, a recession is very likely, thus the model should empphasize "
                     "these data points more."),
        dcc.Markdown("**Years Since Recession**: The number of years since the end of the most recent recession. Economic "
                     "cycles are indeed cyclical, and recessions are a normal part of "
                     "the lifecycle. Thus, as time between recessions increases, the more likely a recession is to occur. "
                     "This is also used to help the model differentiate between data points just before a recession and "
                     "those right after a recession has ended."),
        dcc.Markdown("**Years Until Recession**: The number of years until the next recession. This is the target "
                     "variable for the linear regression model to help it predict how far out a recession may be."),
        dcc.Markdown("**Recession in Next Year**: 1 if a recession starts within the next year, 0 otherwise. This is the "
                     "target variable for the logistic regression model which outputs both a binary and probability "
                     "prediction of this variable."),
        dcc.Markdown("**Yur Prediction**: The YUR model's predicted number of years until the start of the next "
                     "recession. This value is calculated and returned as a continuous variable. "),
        dcc.Markdown("**Riny Prediction**: The RINY model's prediction for if there will be a recession in the next "
                     "year. 1 if a recession is predicted to start within the next year, 0 otherwise."),
        dcc.Markdown("**Riny Prediction Probability**: The RINY model's predicted probability of a recession "
                     "starting within the next year. It has a value bounded between 0 and 1."),
        html.H2("Other Variables", style={"text-decoration": "underline", "margin-top": "5%"}),
        dcc.Markdown("**Date**: All dates are anchored to the first of that month, and data is calculated using monthly "
                     "snapshots. Date format is YYYY-mm-dd"),
        dcc.Markdown("**12 Mo Unemp Change (12 month unemployment change)**: The change in the unemployment rate over the "
                     "previous 12 months. Ex. If Un Rate on 2000-01-01 was 10% and Un Rate on 2001-01-01 was 5%, "
                     "12 Mo Unemp Change on 2001-01-01 would be -5%"),
        dcc.Markdown("**Median Household Price**: The median household price for all houses sold in that month"),
        dcc.Markdown("**Pct House Change Year (Yearly Percentage Median Household Price Change)**: The percentage change "
                     "in median household price over the past year."),
        dcc.Markdown("**Cpi Change All (Percentage Change in CPI)**: The year over year percentage change in the Consumer "
                     "Price Index for all commodities"),
        dcc.Markdown("**Cpi Change Less Food And Energy (Percentage Change in CPI Less Food and Energy)**: The year over "
                     "year percentage change in the Consumer Price Index for all commodities except food and energy. ("
                     "Typically lags behind CPI with food and energy)"),
        dcc.Markdown("**Average Sp Price (Average S&P 500 price)**: The average price of the S&P 500 index during the "
                     "given month. (Not used in the model or analysis)"),
        dcc.Markdown("**Pct Monthly Sp Chnage (Monthly Percentage Change in S&P 500 price)**: Percentage change in the "
                     "S&P 500 price over a one month period (Not used in the model or analysis)"),
        dcc.Markdown("**Pct Bimonthly Sp Chnage (Bi-monthly Percentage Change in S&P 500 price)**: Percentage change in the"
                     " S&P 500 price over a two month period. (Not used in the model or analysis)"),
        dcc.Markdown("**Ten Yr Yield (10 Year Yield Rate)**: The return on a US treasury note that matures over a "
                     "ten year period"),
        dcc.Markdown("**One Yr Yield (1 Year Yield Rate)**: The return on a US treasury note that matures over a "
                     "one year period"),
        dcc.Markdown("**In Recession**: 1 if the given date is during of a determined recession, 0 otherwise.")
    ], style={'margin-left': "3%", "width": "1300px"}),
])
