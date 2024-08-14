# This file will be where the dashboard is deployed from
import warnings

warnings.filterwarnings("ignore")
import dash
from dash import dcc
from dash import html


app = dash.Dash(__name__, use_pages=True, pages_folder="Dashboard/pages", assets_folder="Dashboard/assets")
server = app.server

app.index_string = '''
                    <!DOCTYPE html>
                    <html>
                        <head>
                            {%metas%}
                            <title>{%title%}</title>
                            <script async src="https://pagead2.googlesyndication.com/pagead/js/adsbygoogle.js?client=ca-pub-7650410102976500"
                                crossorigin="anonymous"></script>
                            {%favicon%}
                            {%css%}
                        </head>
                        <body>
                            {%app_entry%}
                            <footer>
                                {%config%}
                                {%scripts%}
                                {%renderer%}
                            </footer>
                        </body>
                    </html>
                    '''

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
            ], style={'backgroundColor': '#088CA9', "display": "flex"}
        ),
        html.H1("Recession Tracker Dashboard", style={"margin-left": "1%"}),
        html.H3('Created By: Seth Friman', style={"margin-left": "1%"}),
        html.H4('Version 1.3', style={"margin-left": "1%"}),
        dcc.Markdown('*Disclaimer: Nothing on this site is financial advice. This is purely for research and '
                     'entertainment purposes*', style={"margin-left": "1%"}),
        dash.page_container
    ],
    className="container",
    style={"background-image": 'url("/assets/stock_background_1.png")',
               'background-size': '100%',
               'width': '1512px',
               'height': '100%'}
)

if __name__ == '__main__':

    app.run_server(debug=True)
