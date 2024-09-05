# data simulation
import random

# live weather data
import openmeteo_requests
import requests_cache
from retry_requests import retry

# colour gradient
import matplotlib.colors as mcolors

# dashboard
import dash
import dash_bootstrap_components as dbc
from dash import html, dcc, callback, Input, Output


# Setup variables

# Setup the Open-Meteo API client with cache and retry on error
cache_session = requests_cache.CachedSession('.cache', expire_after = 3600)
retry_session = retry(cache_session, retries = 5, backoff_factor = 0.2)
openmeteo = openmeteo_requests.Client(session = retry_session)

# Make sure all required weather variables are listed here
# The order of variables in hourly or daily is important to assign them correctly below
weather_url = "https://api.open-meteo.com/v1/forecast"
params = {
	"latitude": 55.967049727775326,
	"longitude": -3.1928189339319695,
	"current": ["temperature_2m", "apparent_temperature", "precipitation", "wind_speed_10m", "wind_direction_10m"],
	"daily": ["temperature_2m_max", "temperature_2m_min", "apparent_temperature_max", "apparent_temperature_min", "uv_index_max", "precipitation_sum", "wind_speed_10m_max"],
	"forecast_days": 1
}

# Setup functions

def randint(min=0, max=30):
    a = random.randint(min, max)
    return a

# use weather variables to choose background colours of cards
def interpolate_colour(value,
                       min_value=0,
                       max_value=100,
                       low_gradient = 'lightblue',
                       high_gradient = 'red'):

    # Normalize the value to be between 0 and 1
    normalized_value = (value - min_value) / (max_value - min_value)

    # Create color gradients from low to high
    colour1 = mcolors.to_rgba(low_gradient)
    colour2 = mcolors.to_rgba(high_gradient)

    interpolated_colour = mcolors.to_hex(
        [colour1[i] * (1 - normalized_value) + colour2[i] * normalized_value for i in range(4)]
    )
    return interpolated_colour

# use weather variables to choose appropriate icons
def map_temp_to_icon(value):
    if value < 0:
        return html.I(className="fa-solid fa-snowflake fa-10x", style={"justifyContent": "center"})
    elif 0 <= value < 5:
        return html.I(className="fa-solid fa-temperature-empty fa-10x", style={"justifyContent": "center"})
    elif 5 <= value < 10:
        return html.I(className="fa-solid fa-temperature-quarter fa-10x", style={"justifyContent": "center"})
    elif 10 <= value < 20:
        return html.I(className="fa-solid fa-temperature-half fa-10x", style={"justifyContent": "center"})
    elif 20 <= value < 25:
        return html.I(className="fa-solid fa-temperature-three-quarters fa-10x", style={"justifyContent": "center"})
    elif 25 <= value < 30:
        return html.I(className="fa-solid fa-temperature-full fa-10x", style={"justifyContent": "center"})
    else:
        return html.P("Get inside!", style={"fontSize": "40px"})

def map_rain_to_icon(value):
    if value == 0:
        return html.I(className="fa-solid fa-sun fa-10x", style={"justifyContent": "center"})
    elif 0 < value < 1:
        return html.I(className="fa-solid fa-cloud-sun fa-10x", style={"justifyContent": "center"})
    elif 1 <= value < 2:
        return html.I(className="fa-solid fa-cloud fa-10x", style={"justifyContent": "center"})
    elif 2 <= value < 4:
        return html.I(className="fa-solid fa-cloud-rain fa-10x", style={"justifyContent": "center"})
    elif 4 <= value < 8:
        return html.I(className="fa-solid fa-cloud-showers-heavy fa-10x", style={"justifyContent": "center"})
    else:
        return html.P("Get inside!", style={"fontSize": "40px"})


# Dash setup
app = dash.Dash(__name__, external_stylesheets=[dbc.themes.BOOTSTRAP, dbc.icons.FONT_AWESOME])

# Define the layout of the app
app.layout = dbc.Container(
    [
        dcc.Location(id='url', refresh=False),
        dbc.NavbarSimple(
            children=[
                dbc.NavItem(dbc.NavLink("Today's Weather", href="/page-1"), style={"marginRight": "20px"}),
                dbc.NavItem(dbc.NavLink("Tomorrow's Weather", href="/page-2"),style={"marginRight": "20px"}),
                dbc.NavItem(dbc.NavLink("Bus Times", href="/page-3")),
            ],
            brand="Kynan's Dashboard",
            brand_style={"fontSize": "2rem"},  # Increases brand text size
            style={"padding": "20px", "fontSize": "1.5rem", "height": "80px"},  # Increases overall navbar size
            color="dark",
            dark=True,
        ),
        html.Div(id='page-content'),
    ],
    fluid=True
)

page_1_layout = html.Div([
    dbc.Row([
        # First Interval and Div
        dcc.Interval(
            id='interval-component-1',
            interval=3600*1000,  # 1000 milliseconds = 1 second
            n_intervals=0
        ),
        dbc.Col(html.Div(id='live-update-text-1')),

        # Second Interval and Div
        dcc.Interval(
            id='interval-component-2',
            interval=5*1000,  # 5000 milliseconds = 5 seconds
            n_intervals=0
        ),
        dbc.Col(html.Div(id='live-update-text-2')),
    ]),
])

# Second page layout
page_2_layout = html.Div([
    html.H1('This is the Daily Weather page', style={'textAlign': 'center'}),
    dbc.Row([
        dbc.Col(html.Div("This is a column with some text")),
        dbc.Col(html.Div("This is another column with different content")),
    ])
])

# Second page layout
page_3_layout = html.Div([
    html.H1('This is the Bus Times page', style={'textAlign': 'center'}),
    dbc.Row([
        dbc.Col(html.Div("This is a column with some text")),
        dbc.Col(html.Div("This is another column with different content")),
    ])
])

# Callback for the first interval
@app.callback(
    Output('live-update-text-1', 'children'),
    Input('interval-component-1', 'n_intervals')
)
def update_text_1(n):
    responses = openmeteo.weather_api(weather_url, params=params)

    # Process first location. Add a for-loop for multiple locations or weather models
    response = responses[0]

    # Current values. The order of variables needs to be the same as requested.
    current = response.Current()
    ambient_temp = int(current.Variables(0).Value())
    real_feel = int(current.Variables(1).Value())

    temp_card = html.Div(
        [
            dbc.Card(
                dbc.CardBody(
                    [
                        html.H1("Temperature", className="text-center"),
                        html.P(
                            [
                                html.Br(),  # Line break
                                f"Ambient temperature: {ambient_temp}°C",
                                html.Br(),  # Line break
                                html.Br(),  # Line break
                                f"Real-feel: {real_feel}°C",
                            ],
                            style={"fontSize": "40px"},  # Smaller text size for temperature details
                            className="card-text",
                        ),
                        # Add the icon outside the <P> element for better control
                        html.Div(
                            map_temp_to_icon(ambient_temp),
                            style={
                                "textAlign": "center",  # Center the icon horizontally
                                "marginTop": "40px"  # Add some space above the icon
                            }
                        ),
                    ]
                ),
                color=interpolate_colour(ambient_temp, 0, 40, "lightblue", "red"),
                className="w-100 mb-1",  # fills the available width. has a margin on the bottom
            )
        ],
        style={"height": "95vh"},  # Set the height of the container to 95% of viewport height
        className="d-flex align-items-stretch"
    )

    return temp_card

# Callback for the second interval
@app.callback(
    Output('live-update-text-2', 'children'),
    Input('interval-component-2', 'n_intervals')
)
def update_text_2(n):
    rain_quant = randint(min=0, max=10)
    rain_prob = randint(min=0, max=40)

    rain_card = html.Div(
        [
            dbc.Card(
                dbc.CardBody(
                    [
                        html.H1("Precipitation", className="text-center"),
                        html.P(
                            [
                                html.Br(),  # line break
                                f"Rainfall: {rain_quant}mm",
                                html.Br(),  # line break
                                html.Br(),  # line break
                                f"Probability: {rain_prob}%",
                            ],
                            style={"fontSize": "40px"},
                            className="card-text",
                        ),
                        # Add the icon outside the <P> element for better control
                        html.Div(
                            map_rain_to_icon(rain_quant),
                            style={
                                "textAlign": "center",  # Center the icon horizontally
                                "marginTop": "40px"  # Add some space above the icon
                            }
                        ),
                    ]
                ),
                color=interpolate_colour(rain_quant, 0, 10,
                                         "skyblue", "dimgrey"),
                className="w-100 mb-1",
            )
        ],
        style={"height": "95vh"},  # Set the height of the container to 100% of the viewport height
        className="d-flex align-items-stretch"
    )
    return rain_card

@app.callback(
    Output('page-content', 'children'),
    Input('url', 'pathname')
)

def update_page(pathname):
    if pathname == '/page-1':
        return page_1_layout
    elif pathname == '/page-2':
        return page_2_layout
    elif pathname == '/page-3':
        return page_3_layout
    else:
        return '404 Page Not Found'

if __name__ == '__main__':
    app.run_server(debug=True)
