from dashboard import app  # load dash

# launch into dash on script execute
import subprocess as sp
from threading import Timer
import os

# Function to open the browser after the Dash server starts
def open_fullscreen_browser():
    # Check OS and use the correct command for Chrome
    if os.name == 'nt':  # Windows
        os.system('start chrome "http://0.0.0.0:8050/" --kiosk')
    elif os.name == 'posix':  # macOS/Linux
        sp.Popen(['firefox', '--kiosk', 'http://0.0.0.0:8050/'], shell=True)


server = app.server

if __name__ == "__main__":
    Timer(2,open_fullscreen_browser).start()  # Note no parentheses here
    app.run(debug=False)
