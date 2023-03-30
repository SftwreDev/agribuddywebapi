import os
import requests
import pandas as pd
import datetime as dt
import csv, urllib.request
from datetime import datetime



class Datasets:
    
    def __init__(self, link: str, lat: str, lng:str):
        self.link = link
        self.lat = lat
        self.lng = lng

    def barako_datasets(self):
        url = self.link
        url_response = urllib.request.urlopen(url)
        csv_lines = [l.decode('utf-8') for l in url_response.readlines()]
        # Create a Pandas DataFrame from the CSV data
        csv_data = list(csv.reader(csv_lines))
        weather_data = pd.DataFrame(csv_data)
        weather_data.columns = ['Date', 'Time', 'Temp Out', 'Hi Temp', 'Low Temp', 'Out Hum', 'Dew Pt.',
                  'Wind Speed', 'Wind Dir', 'Wind Run', 'Hi Speed', 'Hi Dir', 'Wind Chill',
                  'Heat Index', 'THW Index', 'Bar', 'Rain', 'Rain Rate', 'Heat D-D', 'Cool D-D',
                  'In Temp', 'In Hum', 'In Dew', 'In Heat', 'In EMC', 'In Air Density', 'Wind Samp',
                  'Wind Tx', 'ISS Receipt', 'Arc Int', '', '', '', '', '', '', '', '', '']
        # The reset_index() method returns a new DataFrame and does not modify the original one
        weather_data['Date'] = pd.to_datetime(weather_data['Date'], format='%m/%d/%y')
        # Slice the columns of interest
        weather_data_num = weather_data.loc[:, ['Date', 'Time', 'Temp Out', 'Out Hum', 'Dew Pt.', 'Wind Speed']]
        # Convert the date string to a datetime object and then to the desired format
        weather_data_num['Date'] = pd.to_datetime(weather_data_num['Date'], format='%m/%d/%y')
        return weather_data_num
    
    def openmeteo_datasets(self):
        date_today = dt.date.today()
        five_days_ago = date_today - dt.timedelta(days=5)
        print(five_days_ago)
        url = f"https://archive-api.open-meteo.com/v1/archive?latitude={self.lat}&longitude={self.lng}&start_date=2022-07-01&end_date={five_days_ago}&hourly=temperature_2m,relativehumidity_2m,dewpoint_2m,windspeed_10m&models=era5&daily=windspeed_10m_max&timezone=Asia%2FSingapore"
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

        weather_data = pd.DataFrame(weather_arr)
        weather_data['Date'] = pd.to_datetime(weather_data['Date'], format='%m/%d/%y')

        return weather_data


    def merge_datasets(self):
        # Read the two datasets into separate dataframes
        df1 = self.barako_datasets()
        df2 = self.openmeteo_datasets()

        # Merge the two dataframes
        merged_df = pd.concat([df1, df2], ignore_index=True)
        merged_df.replace('---', 0, inplace=True)
        # Sort the merged dataframe based on the 'Date' column
        merged_df[['Temp Out', 'Out Hum', 'Dew Pt.', 'Wind Speed']] = merged_df[['Temp Out', 'Out Hum', 'Dew Pt.', 'Wind Speed']].astype(float)
        merged_df = merged_df.sort_values(by='Date', ascending=True)
        merged_df = merged_df.dropna()
        merged_datasets = merged_df.drop_duplicates()
        
        # Write the merged dataframe to a CSV file
        merged_datasets.to_csv('merged_dataset.csv', index=False)
        
        # Return the merged dataframe
        return merged_datasets
    
    
    def farming_activity_datasets(self):
        return pd.read_csv(os.path.join(os.getcwd(), "farming_data.csv"))
    
    def historical_weather_datasets(self):
        merged_dataset = self.merge_datasets()
        return pd.read_csv(os.path.join(os.getcwd(), "merged_dataset.csv"))
        