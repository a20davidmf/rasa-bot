import requests

def search_weather(location):

    api_key = "6a36faf4f8d939b909d9b60b5a7ef038"

    base_url = "http://api.openweathermap.org/data/2.5/weather?"

    complete_url = base_url + "appid=" + api_key + "&q=" + location

    response = requests.get(complete_url)
    x = response.json()

    if x["cod"] != "404":
        y = x["main"]

        current_temperature = y["temp"]
        z = x["weather"]

        weather_description = z[0]["description"]

        temperature_celsius = round(current_temperature - 273.15, 2)

        return f"The temperature in {location} in is {str(temperature_celsius)} °C and the description says: {str(weather_description)}"

    else:
        return None