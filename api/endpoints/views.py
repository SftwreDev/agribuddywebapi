import numpy as np
from fastapi import APIRouter
from config.settings import app
from datetime import datetime, timedelta
from machine_learning.predict import Predict

router = APIRouter(
    prefix="/api/v1",
    tags=["API Endpoints"],
)


@router.get("/recommend-activity/train={train}")
async def recommend_activity(train: bool):
    predict = Predict(train=train)
    print(predict.predict_activiy(params=np.array([[30, 95, 24.4, 80]])))
    current_date = datetime.now()
    res = []
    for i in range(5):
        response = {}
        result = predict.predict_activiy(params=np.array([[30, 95, 24.4, 80]]))
        
        # get the date 5 days from now
        five_days_from_now = current_date + timedelta(days=i)

        # extract only the date portion
        five_days_from_now_date = five_days_from_now.date()
        
        # print the result
        print(five_days_from_now_date)
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