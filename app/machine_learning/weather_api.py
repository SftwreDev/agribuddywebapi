import requests
import datetime as dt
from datetime import datetime

def openmeteo_datasets(lat, lng):
    date_today = dt.date.today()
    five_days_ago = date_today - dt.timedelta(days=5)
    print(five_days_ago)
    url = f"https://api.open-meteo.com/v1/forecast?latitude={lat}&longitude={lng}&hourly=temperature_2m,relativehumidity_2m,dewpoint_2m,windspeed_10m&current_weather=true&past_days=5&forecast_days=1&timezone=Asia%2FSingapore"
    print(url)
    response = requests.get(url)
    json_data = response.json()

    hourly_data = json_data['hourly']
    weather_arr = []

    for i in range(len(hourly_data['time'])):
        date_string, time_string = hourly_data['time'][i].split("T")
        date_obj = datetime.strptime(date_string, '%Y-%m-%d')
        weather_arr.append({
            "Date" : date_obj.strftime("%m/%d/%y"),
            "Time" : time_string,
            "Temp Out" : hourly_data['temperature_2m'][i],
            "Out Hum" : hourly_data['relativehumidity_2m'][i],
            "Dew Pt." : hourly_data['dewpoint_2m'][i],
            "Wind Speed" : hourly_data['windspeed_10m'][i]
        })

    return weather_arr