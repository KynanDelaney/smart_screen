# Home smart-screen

This repository contains the main script and requirements for running a dashboard of current weather, tomorrow's forecast, and live bus times.

This project used a Raspberry Pi 2b, a cheap [3.5" touchscreen display](http://www.lcdwiki.com/3.5inch_RPi_Display), and a 3D-printed stand case.


## Getting started
To get started, a user needs the latitude and longitude of their address in Decimal Degrees. 
This format of lat/lon is available on Google maps from a dropped pin (e.g. Edinburgh Castle: 55.94861699800257, -3.199928483633489).
Weather data for this location is obtained from [openmeteo](https://open-meteo.com/en/docs).

The user also needs the ID of their local bus stop, as defined by their local bus system API.
For Lothian buses, this is available from [here](https://www.lothianbuses.com/live-travel-info/live-bus-times/).
For Lothian buses, the live times for a given bus stop are accessed from the following style of link: https://lothianapi.co.uk/departureBoards/website?stops=6200206350. 


### Adding personal details
These values, and preferred bus routes, can be saved in a .env file and loaded by the dashboard.
Below is an example .env for weather data for Edinburgh Castle, and Bus Stop data for two buses that pass along Princes Street.

```
# Coordinates for a specific location
HOME_LATITUDE=55.94861699800257
HOME_LONGITUDE=-3.199928483633489

# URL for accessing bus departure data
HOME_BUS=https://lothianapi.co.uk/departureBoards/website?stops=6200206350
BUS_1=15
BUS_2=26
```

<br>

The dashboard is launched by calling the following in the terminal:

```commandline
gunicorn wsgi:server --bind 0.0.0.0:8050 --workers 4
```
