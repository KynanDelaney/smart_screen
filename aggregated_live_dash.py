# live weather data
import openmeteo_requests
import requests_cache
from retry_requests import retry

# live bus data
import requests
import pandas as pd
import json
import re

# colour gradient
import matplotlib.colors as mcolors

# dashboard
import dash
import dash_bootstrap_components as dbc
from dash import html, dcc, callback, Input, Output, dash_table


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
	"current": ["temperature_2m", "apparent_temperature", "precipitation", "cloud_cover", "wind_speed_10m", "wind_direction_10m"],
	"daily": ["temperature_2m_max", "temperature_2m_min", "apparent_temperature_max", "apparent_temperature_min", "uv_index_max", "precipitation_sum", "wind_speed_10m_max"],
	"forecast_days": 2
}

bus_url = "https://lothianapi.co.uk/departureBoards/website?stops=6200206810"


# Setup functions
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
app = dash.Dash(__name__, external_stylesheets=[dbc.themes.BOOTSTRAP, dbc.icons.FONT_AWESOME], suppress_callback_exceptions=True)

# Define the layout of the app
app.layout = dbc.Container(
    [
        dcc.Location(id='url', refresh=False, pathname='/page-1'),
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
            interval=3600*1000,  # 1000 milliseconds = 1 second. Hourly
            n_intervals=0
        ),
        dbc.Col(html.Div(id='live-update-text-1')),
    ]),
])

# Second page layout
page_2_layout = html.Div([
    dcc.Interval(
            id='interval-component-2',
            interval=21600*1000,  # 1000 milliseconds = 1 second. 6 hour intervals
            n_intervals=0
        ),
        dbc.Col(html.Div(id='live-update-text-2')),
])

# Tird page layout
page_3_layout = html.Div([
    dcc.Interval(
            id='interval-component-3',
            interval=60*1000,  # 1000 milliseconds = 1 second. 1 minute intervals
            n_intervals=0
        ),
        dbc.Col(html.Div(id='live-update-text-3')),
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
    current_temperature_2m = int(current.Variables(0).Value())
    current_apparent_temperature = int(current.Variables(1).Value())
    current_precipitation = int(current.Variables(2).Value())
    current_cloud_cover = int(current.Variables(3).Value())
    #current_wind_speed_10m = current.Variables(4).Value()
    #current_wind_direction_10m = current.Variables(5).Value()

    temp_card = html.Div(
        [
            dbc.Card(
                dbc.CardBody(
                    [
                        html.H1("Temperature", className="text-center"),
                        html.P(
                            [
                                html.Br(),  # Line break
                                f"Ambient temperature: {current_temperature_2m}°C",
                                html.Br(),  # Line break
                                html.Br(),  # Line break
                                f"Real-feel: {current_apparent_temperature}°C",
                            ],
                            style={"fontSize": "40px"},  # Smaller text size for temperature details
                            className="card-text",
                        ),
                        # Add the icon outside the <P> element for better control
                        html.Div(
                            map_temp_to_icon(current_temperature_2m),
                            style={
                                "textAlign": "center",  # Center the icon horizontally
                                "marginTop": "40px"  # Add some space above the icon
                            }
                        ),
                    ]
                ),
                color=interpolate_colour(current_temperature_2m, 0, 40, "lightblue", "red"),
                className="w-100 mb-1",  # fills the available width. has a margin on the bottom
            )
        ],
        style={"height": "95vh"},  # Set the height of the container to 95% of viewport height
        className="d-flex align-items-stretch"
    )

    rain_card = html.Div(
        [
            dbc.Card(
                dbc.CardBody(
                    [
                        html.H1("Precipitation", className="text-center"),
                        html.P(
                            [
                                html.Br(),  # line break
                                f"Rainfall: {current_precipitation}mm",
                                html.Br(),  # line break
                                html.Br(),  # line break
                                f"Cloud Cover: {current_cloud_cover}%",
                            ],
                            style={"fontSize": "40px"},
                            className="card-text",
                        ),
                        # Add the icon outside the <P> element for better control
                        html.Div(
                            map_rain_to_icon(current_precipitation),
                            style={
                                "textAlign": "center",  # Center the icon horizontally
                                "marginTop": "40px"  # Add some space above the icon
                            }
                        ),
                    ]
                ),
                color=interpolate_colour(current_precipitation, 0, 10,
                                         "skyblue", "dimgrey"),
                className="w-100 mb-1",
            )
        ],
        style={"height": "95vh"},  # Set the height of the container to 100% of the viewport height
        className="d-flex align-items-stretch"
    )

    hourly_weather_card = dbc.Row(
        [
            dbc.Col(temp_card),
            dbc.Col(rain_card)
        ]
    )
    return hourly_weather_card

@app.callback(
    Output('live-update-text-2', 'children'),
    Input('interval-component-2', 'n_intervals')
)
def update_text_2(n):
    responses = openmeteo.weather_api(weather_url, params=params)

    # Process first location. Add a for-loop for multiple locations or weather models
    response = responses[0]

    # Current values. The order of variables needs to be the same as requested.
    daily = response.Daily()
    daily_temperature_2m_max = int(daily.Variables(0).ValuesAsNumpy()[1])
    daily_temperature_2m_min = int(daily.Variables(1).ValuesAsNumpy()[1])
    daily_apparent_temperature_max = int(daily.Variables(2).ValuesAsNumpy()[1])
    daily_apparent_temperature_min = int(daily.Variables(3).ValuesAsNumpy()[1])
    daily_uv_index_max = int(daily.Variables(4).ValuesAsNumpy()[1])
    daily_precipitation_sum = int(daily.Variables(5).ValuesAsNumpy()[1])
    daily_wind_speed_10m_max = int(daily.Variables(6).ValuesAsNumpy()[1])

    weather_forecast_card = html.Div(
        [
            dbc.Card(
                dbc.CardBody(
                    [
                        html.H1("Tomorrow's Weather", className="text-center"),
                        html.P(
                            [
                                html.Br(),  # Line break
                                f"Ambient temperature: {daily_temperature_2m_min}°C - {daily_temperature_2m_max}°C",
                                html.Br(),  # Line break
                                f"Real-feel: {daily_apparent_temperature_min}°C - {daily_apparent_temperature_max}°C",
                                html.Br(),  # Line break

                                f"Precipitation: {daily_precipitation_sum}",
                                html.Br(),  # Line break
                                f"Wind speed: {daily_wind_speed_10m_max}",
                                html.Br(),  # Line break
                                f"UV index: {daily_uv_index_max}"
                            ],
                            style={"fontSize": "40px"},  # Smaller text size for temperature details
                            className="card-text",
                        ),
                    ]
                ),
                color=interpolate_colour(((int(daily_temperature_2m_min) + int(daily_temperature_2m_max)) / 2.0), 0, 40, "lightblue", "red"),
                className="w-100 mb-1",  # fills the available width. has a margin on the bottom
            )
        ],
        style={"height": "95vh"},  # Set the height of the container to 95% of viewport height
        className="d-flex align-items-stretch"
    )

    return weather_forecast_card

@app.callback(
    Output('live-update-text-3', 'children'),
    Input('interval-component-3', 'n_intervals')
)
def update_text_3(n):
    # Fetch the page content
    response = requests.get(bus_url)
    html_content = response.text

    # Print a snippet of the HTML content to confirm it's fetched correctly
    # print(html_content[:2000])  # Print the first 2000 characters

    json_match = re.search(r'{.*}', html_content, re.DOTALL)
    json_data = json_match.group(0)

    # print(json_data)

    # Parse and print the JSON data if found
    if json_data:
        try:
            data = json.loads(json_data)
            #print(json.dumps(data, indent=4))
        except json.JSONDecodeError as e:
            print("Failed to parse JSON data:", e)
    else:
        print("No JSON data found.")

    # Extracting the first two departure times for each service
    bus_services = []
    for service in data['services']:
        service_name = service['service_name']
        departures = service['departures'][:3]  # Get the first two departures
        for departure in departures:
            bus_services.append({
                'Service Name': service_name,
                'Minutes Until Departure': departure['minutes'],
                'Departure Time': departure['departure_time']
            })

    # Creating a DataFrame for easy display
    df = pd.DataFrame(bus_services)

    bus_card = html.Div(
        [
            dbc.Card(
                [
                    dbc.CardHeader("Bus Departure Times", style={"color": "white", "fontSize": "40px"}),
                    dbc.CardBody(
                        dash_table.DataTable(
                            columns=[{"name": i, "id": i} for i in df.columns],
                            data=df.to_dict('records'),
                            style_table={'overflowX': 'auto'},
                            style_cell={'textAlign': 'left'},
                            style_header={'backgroundColor': 'rgb(30, 30, 30)', 'color': 'white'},
                            style_data={'backgroundColor': 'rgb(50, 50, 50)', 'color': 'white'},
                        )
                    )
                ],
                style={"width": "100%", "fontSize": "32px"},
                color='rgb(50, 50, 50)'
            )
        ],
    className = "d-flex align-items-stretch"
    )

    return bus_card

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
