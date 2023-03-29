import numpy as np
from fastapi import APIRouter
from config.settings import app
from datetime import datetime, timedelta
from machine_learning.predict import Predict
from machine_learning.weather_api import openmeteo_datasets

router = APIRouter(
    prefix="/api/v1",
    tags=["API Endpoints"],
)


@router.get("/recommend-activity/train={train}")
async def recommend_activity(train: bool):
    past_forecast = openmeteo_datasets()
    forecast_5_days_ago = []

    for forecast in past_forecast:
        forecast_5_days_ago.append([forecast['Temp Out'], forecast['Out Hum'], forecast['Dew Pt.'], forecast['Wind Speed']])

    predict = Predict(train=train)
    current_date = datetime.now()
    res = []
    
    for idx, x in enumerate(forecast_5_days_ago[-5:]):
        response = {}
        result = predict.predict_activiy(params=np.array([x]))
        
        # get the date 5 days from the current date
        five_days_from_now = current_date + timedelta(days=idx + 1)

        # extract only the date portion
        five_days_from_now_date = five_days_from_now.date()
        
        # print the result
        response['title'] = result['title']
        response['start'] = five_days_from_now_date
        response['end'] = five_days_from_now_date
        response['allDay'] = True
        response['temperature'] = round(result['temperature'])
        response['humidity'] = round(result['humidity'])
        response['dew_pt'] = round(result['dew_pt'])
        response['wind_speed'] = round(result['wind_speed'])
        res.append(response)
    
    return res