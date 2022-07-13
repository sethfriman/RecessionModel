import dash
from dash import html, dcc, callback, Input, Output
import smtplib, ssl

dash.register_page(__name__)

output_text = ""
successColor = "green"

layout = html.Div(
    [
        html.Div(
            [
                html.H1('Contact Us... or just me!'),
                html.Div(
                    [
                        html.Div(
                            [
                                html.Div(
                                    [
                                        html.Label('Email'),
                                    ], style={"margin-left": "10%"}
                                ),
                                html.Div(
                                    [
                                        html.Label('Name'),
                                    ], style={"margin-top": "15%", "margin-left": "10%"}
                                ),
                                html.Div(
                                    [
                                        html.Label('Message Type'),
                                    ], style={"margin-top": "15%", "margin-left": "10%"}
                                ),
                                html.Div(
                                    [
                                        html.Label('Message'),
                                    ], style={"margin-top": "15%", "margin-left": "10%"}
                                ),
                            ], style={"width": "33%", "verticalAlign": "top"}
                        ),
                        html.Div(
                            [
                                dcc.Input(type="email", id="email-row",
                                          placeholder="Enter email", style={"margin-left": "2%", "width": "90%"}),
                                dcc.Input(type="text", id="name-row",
                                          placeholder="Enter name", style={"margin-left": "2%", "width": "90%",
                                                                           "margin-top": "7%"}),
                                dcc.Dropdown(
                                    id="contact-dropdown",
                                    options=[
                                        'Suggestion',
                                        'Report Bug',
                                        'Question about Data',
                                        'General Feedback',
                                        'Help',
                                        'Other'
                                    ],
                                    value='text',
                                    className="dropdown",
                                    placeholder="Select a Reason for Contacting...",
                                    style={"margin-left": "1%", "width": "96%", "margin-top": "5%"}
                                ),
                                dcc.Textarea(id="message-row",
                                             placeholder="Enter your message here",
                                             required=True,
                                             style={"margin-left": "2%", "width": "90%", "height": "70px",
                                                    "margin-top": "4%", 'font-family': 'sans-serif'}),
                            ], style={"width": "66%"}
                        ),
                    ], style={"display": "flex", "margin-top": "5%"}
                ),
                html.Div(id='submit-button', children=
                [
                    html.Button('Send Message', id='send-contact', n_clicks=0,
                                style={"backgroundColor": "blue", 'color': "white",
                                       "margin-left": "43%", "margin-top": "5%", "margin-bottom": "5%",
                                       "border-radius": "6px"}),
                ]
                         ),
                html.Div(id='output-text', children=[],
                         style={"margin-bottom": "3%"}),
            ], style={"margin-left": "4%", "margin-top": "4%", "border": "2px black solid", "width": "50%"}
        ),
    ], style={"height": "100vh", 'width': '100vw'}
)


@callback(
    Output('submit-button', 'children'),
    Output('output-text', 'children'),
    Output('email-row', 'value'),
    Output('name-row', 'value'),
    Output('contact-dropdown', 'value'),
    Output('message-row', 'value'),
    Input('email-row', 'value'),
    Input('name-row', 'value'),
    Input('contact-dropdown', 'value'),
    Input('message-row', 'value'),
    Input('send-contact', 'n_clicks'),
)
def contact(email, name, drop, message, clicks):
    port = 465  # For SSL
    sender_email = email
    receiver_email = '<your email address here>'

    # Create a secure SSL context
    context = ssl.create_default_context()

    if clicks > 0:
        try:
            # with smtplib.SMTP_SSL("smtp.gmail.com", port, context=context) as server:
            #     server.login("<you email address here>", '<you email password here>')
            #     server.sendmail(sender_email, receiver_email, message)
            #     server.quit()
            return [html.Button('Send Message', id='send-contact', n_clicks=0,
                                style={"backgroundColor": "blue", 'color': "white",
                                       "margin-left": "43%", "margin-top": "5%", "margin-bottom": "5%",
                                       "border-radius": "6px"})], \
                   [html.Div("Thanks for contacting! Message sent successfully!",
                             style={"color": "green"})], '', '', '', ''
        except:
            return [html.Button('Send Message', id='send-contact', n_clicks=0,
                                style={"backgroundColor": "blue", 'color': "white",
                                       "margin-left": "43%", "margin-top": "5%", "margin-bottom": "5%",
                                       "border-radius": "6px"})], \
                   [html.Div("Message unable to send. Please Make sure all fields were entered correctly",
                             style={"color": "red"})], email, name, drop, message
    else:
        return [html.Button('Send Message', id='send-contact', n_clicks=0,
                            style={"backgroundColor": "blue", 'color': "white",
                                   "margin-left": "43%", "margin-top": "5%", "margin-bottom": "5%",
                                   "border-radius": "6px"})], \
               [html.Div("",
                         style={"color": "red"})], email, name, drop, message
