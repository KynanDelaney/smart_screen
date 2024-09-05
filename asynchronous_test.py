import random
import asyncio

import openmeteo_requests
import requests_cache
from retry_requests import retry

# Setup the Open-Meteo API client with cache and retry on error
cache_session = requests_cache.CachedSession('.cache', expire_after=3600)
retry_session = retry(cache_session, retries=5, backoff_factor=0.2)
openmeteo = openmeteo_requests.Client(session=retry_session)
url = "https://api.open-meteo.com/v1/forecast"


async def weather_check():
    while True:

        # Make sure all required weather variables are listed here
        # The order of variables in hourly or daily is important to assign them correctly below
        params = {
            "latitude": 55.967049727775326,
            "longitude": -3.1928189339319695,
            "current": ["temperature_2m", "apparent_temperature"]
        }
        responses = openmeteo.weather_api(url, params=params)
        response = responses[0]

        # Current values. The order of variables needs to be the same as requested.
        current = response.Current()
        current_temperature_2m = current.Variables(0).Value()
        current_apparent_temperature = current.Variables(1).Value()

        print("The current temperature: ", current_temperature_2m)
        print("Real-feel: ", current_apparent_temperature)

        await asyncio.sleep(20)  # Use asyncio.sleep for non-blocking delay


def randint(min=0, max=100):
    a = random.randint(min, max)
    return a

async def fast_check():
    while True:
        print("fast: ", randint())
        await asyncio.sleep(1)  # Use asyncio.sleep for non-blocking delay

# Main function to run all tasks concurrently
async def main():
    # Schedule all tasks to run concurrently
    await asyncio.gather(
        weather_check(),
        fast_check()
    )

# Run the main function using asyncio
if __name__ == "__main__":
    asyncio.run(main())
