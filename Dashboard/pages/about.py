import dash
from dash import html, dcc, callback, Input, Output

dash.register_page(__name__)

layout = html.Div(
    [
        html.H1('About Page', style={"margin-top": "3%"}),

        dcc.Markdown('''
            Hey there! I'm Seth and welcome to my project. This was a passion project I created because I was annoyed
            that I had no idea what was happening with the US economy. This was the simplest way to reconcile. So 
            explore, learn a bit (hopefully), and enjoy!
            
            This application was designed as a tool to help predict the likelihood of an economic recession
            occurring in the United States. It was created by employing many different economic variables over the 
            past 50+ years and using a logistic and linear regression model to make estimates about the state of
            the US economy in the coming years. 
            
            The data is obtained from a combination of [St. Louis Federal Reserve of Economic Data 
            (FRED)](https://fred.stlouisfed.org/), the [List of recessions in the United States]( 
            https://en.wikipedia.org/wiki/List_of_recessions_in_the_United_States) Wikipedia page, 
            and [multpl.com](https://www.multpl.com/s-p-500-historical-prices/table/by-month).
            
            This project is created in Python using packages such as pandas, sci-kit learn, fredapi, bs4, numpy,
            and many more. The repository for the code can be found on GitHub [here](
            https://github.com/sethfriman/RecessionModel).
        ''', style={"width": "70%", "font-size": "18px", "textAlign": "justify"}),
    ], style={"height": "100vh", 'width': '100vw'}
)
