import random
import matplotlib.colors as mcolors

import dash
import dash_bootstrap_components as dbc
from dash import html, dcc, callback, Input, Output

# generate values and define visuals
def randint(min=0, max=125):
    a = random.randint(min, max)
    return a

# random, realistic values for weather variables
ambient_temp = randint(min=0, max=40)
real_feel = ambient_temp + randint(min=-10, max=10)
rain_quant = randint(min=0, max=10)
rain_prob = randint(min=0, max=40)

# use weather variables to choose appropriate icons
def map_temp_to_icon(value):
    if 0 <= value < 5:
        return html.I(className="fa-solid fa-temperature-empty fa-10x", style={"justifyContent": "center"})
    elif 5 <= value < 10:
        return html.I(className="fa-solid fa-temperature-quarter fa-10x", style={"justifyContent": "center"})
    elif 10 <= value < 20:
        return html.I(className="fa-solid fa-temperature-half fa-10x", style={"justifyContent": "center"})
    elif 20 <= value < 25:
        return html.I(className="fa-solid fa-temperature-three-quarters fa-10x", style={"justifyContent": "center"})
    elif 25 <= value < 30:
        return html.I(className="fa-solid fa-temperature-full fa-10", style={"justifyContent": "center"})
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
        [
        colour1[i] * (1 - normalized_value) + colour2[i] * normalized_value for i in range(4)
        ]
    )
    return interpolated_colour

# Create a Dash application instance
app = dash.Dash(__name__, external_stylesheets=[dbc.themes.BOOTSTRAP, dbc.icons.FONT_AWESOME])

# Define the layout of the app
app.layout = dbc.Container(
    [
        dcc.Location(id='url', refresh=False),
        dbc.NavbarSimple(
            children=[
                dbc.NavItem(dbc.NavLink("Page 1", href="/page-1")),
                dbc.NavItem(dbc.NavLink("Page 2", href="/page-2")),
            ],
            brand="Kynan's Dashboard",
            color="dark",
            dark=True,
        ),
        html.Div(id='page-content'),
    ],
    fluid=True
)

temp_card = html.Div(
    [
        dbc.Card(
            dbc.CardBody(
                [
                    html.H1("Temperature", className="text-center"),
                    html.P(
                        [
                            html.Br(), # Line break
                            f"Ambient temperature: {ambient_temp}°C",
                            html.Br(), # Line break
                            html.Br(), # Line break
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
                    "marginTop": "40px"     # Add some space above the icon
                    }
                ),
            ]
        ),
            color=interpolate_colour(ambient_temp, 0, 40, "lightblue", "red"),
            className="w-100 mb-1", # fills the available width. has a margin on the bottom
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
                            html.Br(), #line break
                            f"Rainfall: {rain_quant}mm",
                            html.Br(), #line break
                            html.Br(), #line break
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
                    "marginTop": "40px"     # Add some space above the icon
                    }
                ),
                ]
            ),
            color = interpolate_colour(rain_quant,0,10,
                                       "skyblue", "dimgrey"),
            className="w-100 mb-1",
        )
    ],
style={"height": "95vh"},  # Set the height of the container to 100% of the viewport height
className="d-flex align-items-stretch"
)

# Define the content for Page 1
page_1_layout = dbc.Row(
    [
        dbc.Col(temp_card),
        dbc.Col(rain_card)
    ]
)

# Define the content for Page 2
page_2_layout = html.Div(
    [
        dbc.Row(
            [
                dbc.Col(
                    dbc.Card(
                        [
                            dbc.CardHeader("Single Card"),
                            dbc.CardBody("This is the content of the single card."),
                        ]
                    ),
                    width=12
                )
            ]
        )
    ]
)

# Update the page content based on the URL
@app.callback(
    Output('page-content', 'children'),
    Input('url', 'pathname')
)

def update_page(pathname):
    if pathname == '/page-1':
        return page_1_layout
    elif pathname == '/page-2':
        return page_2_layout
    else:
        return '404 Page Not Found'

# Run the app
if __name__ == '__main__':
    app.run_server(debug = True)
