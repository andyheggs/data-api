# weather.py
# pylint: disable=missing-module-docstring

import sys
import urllib.parse
import requests

BASE_URI = "https://weather.lewagon.com"

def search_city(query):
    """
    Look for a given city using the Le Wagon OpenWeather proxy.
    Return:
      - None if nothing was found
      - A list of city dictionaries if one or more matches were found
    """
    url = f"{BASE_URI}/geo/1.0/direct?q={urllib.parse.quote(query)}&limit=5"
    response = requests.get(url).json()

    if not response:
        return None  # No match

    # Otherwise, return the entire list of city matches
    return response

def weather_forecast(lat, lon):
    """
    Return a 5-day weather forecast for the city, given its latitude and longitude.
    Each day includes:
      - date (YYYY-MM-DD)
      - weather description
      - max temperature in Celsius
    """
    url = f"{BASE_URI}/data/2.5/forecast?lat={lat}&lon={lon}&units=metric"
    response = requests.get(url).json()
    # 'list' has 3h-interval forecasts
    forecasts = response.get("list", [])
    daily_forecast = []

    # We only want 5 daily entries, stepping by 8 (since 24h / 3h = 8 intervals per day).
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
    CLI flow:
    1. Ask the user for a city name
    2. Attempt to find matches
    3. If multiple matches, ask user to choose which one
    4. Fetch the forecast and display
    """
    query = input("City?\n> ")
    results = search_city(query)

    if not results:
        print("No city found for that query, please try again.")
        return  # Will return to the while True loop in __main__

    if len(results) == 1:
        # Only one match
        chosen_city = results[0]
    else:
        # Multiple matches, let user pick
        print("Multiple matches found:")
        for idx, city_info in enumerate(results, start=1):
            country = city_info.get("country", "")
            state = city_info.get("state", "")
            name = city_info.get("name", "")
            if state and state != name:  # Avoid repeating name if state == name
                print(f"{idx}. {name}, {state}, {country}")
            else:
                print(f"{idx}. {name}, {country}")

        while True:
            choice = input("Which city did you mean? Enter index:\n> ")
            if choice.isdigit():
                index = int(choice)
                if 1 <= index <= len(results):
                    chosen_city = results[index - 1]
                    break
            print("Invalid choice, please try again.")

    lat = chosen_city["lat"]
    lon = chosen_city["lon"]
    name = chosen_city["name"]

    # Fetch forecast
    forecast_data = weather_forecast(lat, lon)

    if forecast_data:
        print(f"Here's the weather in {name}:")
        for day in forecast_data:
            print(f"{day['date']}: {day['description']} {day['temp']:.1f}°C")
    else:
        print(f"No forecast data found for {name}.")

if __name__ == '__main__':
    try:
        while True:
            main()
    except KeyboardInterrupt:
        print("\nGoodbye!")
        sys.exit(0)
