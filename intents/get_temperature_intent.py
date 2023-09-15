import requests
import dotenv
import os

if __name__ == "__main__":
    dotenv.load_dotenv()
    api_key = os.environ.get('OPEN_WEATHER_API')

    # Specify the city and country code (e.g., London,GB for London, United Kingdom)
    city = 'Berlin'
    country_code = 'DE'

    # # Make a request to the OpenWeatherMap API
    # url = f'http://api.openweathermap.org/data/2.5/weather?q={city},{country_code}&appid={api_key}'
    # response = requests.get(url)

    # if response.status_code == 200:
    #     data = response.json()
        
    #     # Check if the response contains the 'main' key
    #     if 'main' in data:
    #         temperature_kelvin = data['main']['temp']
    #         print(data)
    #         temperature_celsius = temperature_kelvin - 273.15  # Convert to Celsius

    #         # Print the temperature
    #         print(f"The current temperature in {city}, {country_code} is {temperature_celsius:.2f} °C.")
    #     else:
    #         print("Unexpected response format: 'main' key not found.")
    # else:
    #     print(f"Error: Unable to retrieve data. Status code {response.status_code}")

    # Specify the number of days for the forecast (in this case, 3 days)
    num_days = 3

    # Make a request to the OpenWeatherMap API forecast endpoint
    url = f'http://api.openweathermap.org/data/2.5/forecast?q={city},{country_code}&appid={api_key}'
    response = requests.get(url)

    # Check if the request was successful (status code 200)
    if response.status_code == 200:
        data = response.json()

        # Extract the temperature from the response for 3 days from now
        temperature_list = []

        for entry in data['list']:
            date_time = entry['dt_txt']
            temperature_kelvin = entry['main']['temp']
            temperature_celsius = temperature_kelvin - 273.15  # Convert to Celsius

            # Check if the forecast is for 3 days from now
            if '12:00:00' in date_time:  # Adjust this if you want a different time of day
                temperature_list.append((date_time, temperature_celsius))

        # Print the temperatures
        for date_time, temperature in temperature_list:
            print(f"At {date_time}, the temperature will be {temperature:.2f} °C.")
    else:
        print(f"Error: Unable to retrieve data. Status code {response.status_code}")
