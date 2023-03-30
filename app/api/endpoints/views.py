import numpy as np
from fastapi import APIRouter
from config.settings import app
from datetime import datetime, timedelta
from machine_learning.predict import Predict
from machine_learning.weather_api import openmeteo_datasets
from typing import List

import databases
import sqlalchemy
from sqlalchemy import and_



router = APIRouter(
    prefix="/api/v1",
    tags=["API Endpoints"],
)

# SQLAlchemy specific code, as with any other app
DATABASE_URL = "postgresql://postgres:iWjHNRgEbf3vybYX0dB9@containers-us-west-26.railway.app:7837/railway"
# DATABASE_URL = "postgresql://user:password@postgresserver/db"

database = databases.Database(DATABASE_URL)

metadata = sqlalchemy.MetaData()

predictions = sqlalchemy.Table(
    "predictions",
    metadata,
    sqlalchemy.Column("id", sqlalchemy.Integer, primary_key=True),
    sqlalchemy.Column("title", sqlalchemy.String),
    sqlalchemy.Column("start", sqlalchemy.Date),
    sqlalchemy.Column("end", sqlalchemy.Date),
    sqlalchemy.Column("temperature", sqlalchemy.String),
    sqlalchemy.Column("out_hum", sqlalchemy.String),
    sqlalchemy.Column("dew_pt", sqlalchemy.String),
    sqlalchemy.Column("wind_speed", sqlalchemy.String),
)


engine = sqlalchemy.create_engine(
    DATABASE_URL, connect_args={}
)
metadata.create_all(engine)

@router.on_event("startup")
async def startup():
    await database.connect()


@router.on_event("shutdown")
async def shutdown():
    await database.disconnect()

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
        
        result = predict.predict_activiy(params=np.array([x]))
        
        # get the date 5 days from the current date
        five_days_from_now = current_date + timedelta(days=idx + 1)

        # extract only the date portion
        five_days_from_now_date = five_days_from_now.date()
        
        filterQuery = predictions.select().where(
            and_(
                predictions.c.title == result['title'],
                predictions.c.start == five_days_from_now_date,
                predictions.c.end == five_days_from_now_date
            )
        )
        if not await database.fetch_all(filterQuery):
            # print the result
            query = predictions.insert().values(
                title=result['title'], start=five_days_from_now_date, end=five_days_from_now_date,
                temperature=str(round(result['temperature'])), out_hum=str(round(result['humidity'])), dew_pt=str(round(result['dew_pt'])), wind_speed=str(round(result['wind_speed']))
                )
            await database.execute(query)
    

    selectQuery = predictions.select()
    fetchAll  = await database.fetch_all(selectQuery)

    for item in fetchAll:
        response = {}
        response['title'] = item.title
        response['start'] = item.start
        response['end'] = item.end
        response['allDay'] = True
        response['temperature'] = item.temperature
        response['humidity'] = item.out_hum
        response['dew_pt'] = item.dew_pt
        response['wind_speed'] = item.wind_speed
        res.append(response)
    
    return res