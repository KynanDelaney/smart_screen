import dash
from dash import html, dcc, callback, Input, Output
import random
import matplotlib.colors as mcolors

# Initialize the Dash app
app = dash.Dash(__name__)

def randint(min=0, max=30):
    a = random.randint(min, max)
    return a

# Example numbers to display
numbers = [randint(), randint()]

# Function to interpolate between blue and red based on a value from 0 to 100
def interpolate_colour(value, min_value=0, max_value=30):
    # Normalize the value to be between 0 and 1
    normalized_value = (value - min_value) / (max_value - min_value)
    # Create color gradients from blue to red
    colour1 = mcolors.to_rgba('lightblue')
    colour2 = mcolors.to_rgba('red')
    # Interpolate color
    interpolated_colour = mcolors.to_hex([
        colour1[i] * (1 - normalized_value) + colour2[i] * normalized_value for i in range(4)])
    return interpolated_colour

# Example text to display on the second page
random_text = "Lorem ipsum dolor sit amet, consectetur adipiscing elit. Vivamus lacinia odio vitae vestibulum vestibulum. Cras venenatis euismod malesuada."



# Define the layout of the dashboard
app.layout = html.Div([
    dcc.Location(id='url', refresh=False),  # Track the URL

    # Container for the main content
    html.Div(id='page-content',
             style={'height': '100vh', 'display': 'flex', 'alignItems': 'center', 'justifyContent': 'center'}),

    # Left arrow for navigation
    html.Div(
        id='left-arrow',
        style={'position': 'fixed', 'left': '20px', 'top': '50%', 'fontSize': '50px', 'cursor': 'pointer'}
    ),

    # Right arrow for navigation
    html.Div(
        id='right-arrow',
        style={'position': 'fixed', 'right': '20px', 'top': '50%', 'fontSize': '50px', 'cursor': 'pointer'}
    ),
])


# Define callback to update the page content and arrows based on the URL
@callback(
    [Output('page-content', 'children'),
     Output('left-arrow', 'children'),
     Output('right-arrow', 'children')],
    Input('url', 'pathname')
)
def display_page(pathname):
    if pathname == '/page-2':
        # Page 2 content with random text
        content = html.Div(
            random_text,
            style={
                'backgroundColor': 'green',
                'color': 'white',
                'width': '100%',
                'height': '100%',
                'textAlign': 'center',
                'fontSize': '40px',
                'display': 'flex',
                'alignItems': 'center',
                'justifyContent': 'center',
                'padding': '20px',
            }
        )
        left_arrow = dcc.Link('←', href='/page-1', style={'textDecoration': 'none', 'color': 'black'})
        right_arrow = dcc.Link('→', href='/page-1', style={'textDecoration': 'none', 'color': 'black'})

    else:  # Default to page 1
        # Page 1 content with two numbers
        content = html.Div(
            [
                html.Div(
                    str(numbers[0]),
                    style={
                        'backgroundColor': interpolate_colour(numbers[0]),
                        'color': 'black',
                        'width': '50%',
                        'height': '95%',
                        'textAlign': 'center',
                        'fontSize': '100px',
                        'display': 'inline-block',
                        'lineHeight': '100vh',
                    }
                ),
                html.Div(
                    str(numbers[1]),
                    style={
                        'backgroundColor': interpolate_colour(numbers[1]),
                        'color': 'black',
                        'width': '50%',
                        'height': '95%',
                        'textAlign': 'center',
                        'fontSize': '100px',
                        'display': 'inline-block',
                        'lineHeight': '100vh',
                    }
                )
            ],
            style={'display': 'flex', 'width': '100%', 'height': '100%'}
        )
        left_arrow = dcc.Link('←', href='/page-2', style={'textDecoration': 'none', 'color': 'black'})
        right_arrow = dcc.Link('→', href='/page-2', style={'textDecoration': 'none', 'color': 'black'})

    return content, left_arrow, right_arrow


# Run the app
if __name__ == '__main__':
    app.run_server(debug=True)
