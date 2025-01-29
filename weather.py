# pylint: disable=missing-module-docstring

import sys
import urllib.parse
import requests

# Base URL for the Le Wagon OpenWeather proxy API
BASE_URI = "https://weather.lewagon.com"

 #-------------------------------City Search---------------------------------------------#

def search_city(query):
    """
    Look for a given city using the Le Wagon OpenWeather proxy.
    If multiple options are returned, ask the user to pick one by index.
    Return one city (dictionary) or None if none found.
    """

    # Short-circuit if user didn't type anything
    if not query.strip():
        print("No city name provided, please try again.")
        return None

    # Build URL, limit=5 to allow multiple results
    url = f"{BASE_URI}/geo/1.0/direct?q={urllib.parse.quote(query)}&limit=5"
    response = requests.get(url).json()

    # If no result, return None (so main can handle "City not found")
    if not response:
        print("No city found for that query, please try again.")
        return None

    # If exactly one city is returned, just return it
    if len(response) == 1:
        return response[0]

    # If multiple options are returned, list them for the user
    print("Multiple matches found:")

    for idx, city_info in enumerate(response, start=1):

        # Some city entries may not have a 'country' or 'state' key; handle gracefully
        country = city_info.get("country", "")
        state = city_info.get("state", "")
        name = city_info.get("name", "")

        # Handle case where 'state' could duplicate the city name
        if state and state != name:
            print(f"{idx}. {name}, {state}, {country}")
        else:
            print(f"{idx}. {name}, {country}")

    while True:
        user_choice = input("Which city did you mean? Enter index:\n> ")

        # Validate user choice
        if user_choice.isdigit():
            choice_index = int(user_choice)
            if 1 <= choice_index <= len(response):
                return response[choice_index - 1]
        print("Invalid choice, please enter a valid number from the list above.")

 #-------------------------------Weather Forecast---------------------------------------------#

def weather_forecast(lat, lon):
    """
    Return a 5-day weather forecast for the city, given its latitude and longitude.
    Each day includes:
      - date (YYYY-MM-DD)
      - weather description
      - max temperature in Celsius
    """
    # Construct URL for fetching weather forecast data
    url = f"{BASE_URI}/data/2.5/forecast?lat={lat}&lon={lon}&units=metric"
    response = requests.get(url).json()

    # response['list'] contains forecasts every 3 hours (8 per day)
    forecasts = response.get("list", [])
    daily_forecast = []
    # only need 5 results, each representing a separate day
    # Slicing by 8 gives approx. 1 forecast reading per day (the next ~5 days)
    for i in range(0, min(len(forecasts), 40), 8):
        entry = forecasts[i]
        date_str = entry["dt_txt"][:10]  # e.g. '2025-01-29'
        description = entry["weather"][0]["description"].title()
        temp = entry["main"]["temp_max"]  # max temp in °C
        daily_forecast.append({
            "date": date_str,
            "description": description,
            "temp": temp
        })

    return daily_forecast

def main():
    """
    Ask user for a city and display weather forecast
    """
    # Prompt user for city input
    query = input("City?\n> ")
    # Search for city and get city data
    city = search_city(query)

    # If city is None = no match or user canceled
    if not city:
        return  # Will go back to the top of the loop in __main__

    # Extract coordinates for selected city
    lat = city["lat"]
    lon = city["lon"]
    name = city["name"]

    # Fetch forecast
    forecast_data = weather_forecast(lat, lon)

    # Display forecast if we have results
    if forecast_data:
        print(f"Here's the weather in {name}")
        # Iterate through forecast data and print day's weather
        for day in forecast_data:
            print(f"{day['date']}: {day['description']} {day['temp']:.1f}°C")
    else:
        print(f"No forecast data found for {name}.")

if __name__ == '__main__':
    try:
        while True:
            main()
    except KeyboardInterrupt:
        # exit upon receiving keyboard interrupt
        print("\nGoodbye!")
        sys.exit(0)
