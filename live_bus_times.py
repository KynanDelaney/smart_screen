import requests
import pandas as pd
import json
import re

# URL of the webpage containing the JSON data
url = "https://lothianapi.co.uk/departureBoards/website?stops=6200206810"

# Fetch the page content
response = requests.get(url)
html_content = response.text

# Print a snippet of the HTML content to confirm it's fetched correctly
#print(html_content[:2000])  # Print the first 2000 characters

json_match = re.search(r'{.*}', html_content, re.DOTALL)
json_data = json_match.group(0)

#print(json_data)

# Parse and print the JSON data if found
if json_data:
    try:
        data = json.loads(json_data)
        print(json.dumps(data, indent=4))
    except json.JSONDecodeError as e:
        print("Failed to parse JSON data:", e)
else:
    print("No JSON data found.")

# Extracting the first two departure times for each service
bus_services = []
for service in data['services']:
    service_name = service['service_name']
    departures = service['departures'][:2]  # Get the first two departures
    for departure in departures:
        bus_services.append({
            'Service Name': service_name,
            'Minutes Until Departure': departure['minutes'],
            'Departure Time': departure['departure_time']
        })

# Creating a DataFrame for easy display
df = pd.DataFrame(bus_services)

# Display the DataFrame as a table
print(df)
