import os
import googlemaps
import numpy as np
from fastapi import APIRouter
from config.settings import app
from pydantic import BaseModel
from datetime import datetime, timedelta, date
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
DATABASE_URL = "postgresql://postgres:ZbjA9YQJW7oHxwUj0ptk@containers-us-west-92.railway.app:7471/railway"
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

locations = sqlalchemy.Table(
    "locations",
    metadata,
    sqlalchemy.Column("id", sqlalchemy.Integer, primary_key=True),
    sqlalchemy.Column("locations", sqlalchemy.String),
    sqlalchemy.Column("link", sqlalchemy.String),
    sqlalchemy.Column("lat", sqlalchemy.String),
    sqlalchemy.Column("lng", sqlalchemy.String),
    sqlalchemy.Column("is_trained", sqlalchemy.Boolean),
)

engine = sqlalchemy.create_engine(
    DATABASE_URL, connect_args={}
)
metadata.create_all(engine)

class Locations(BaseModel):
    locations: str
    link: str 

class LocationsResponse(BaseModel):
    id: int
    locations: str
    link: str 

class PredictInput(BaseModel):
    link: str

class CustomDateprediction(BaseModel):
    date: date

@router.on_event("startup")
async def startup():
    await database.connect()


@router.on_event("shutdown")
async def shutdown():
    await database.disconnect()

async def check_predictions(title):
    predict = predictions.select().where(and_(predictions.c.title==title))
    if not await database.fetch_all(predict):
        return False
    else:
        return True

async def recommend_activity_checker(is_custom: bool, custom_date):
    today = datetime.today().date()
    if is_custom:
        custom_date = custom_date
    else:
        custom_date = custom_date.date()
    if await check_predictions("Land Preparation"):
        if custom_date > today - timedelta(days=60):
            return "Land Preparation"
        else:
            if await check_predictions("Weeding"):
                if custom_date > today - timedelta(days=3):
                    return "Weeding"
                else:
                    if await check_predictions("Field Lay outing & Holing"):
                        if custom_date > today - timedelta(days=3):
                            return "Field Lay outing & Holing"
                        else:
                            if await check_predictions("Application of fertilizer"):
                                if custom_date > today - timedelta(days=1):
                                    return "Application of fertilizer"
                                else:
                                    if await check_predictions("Transplanting of Seedlings"):
                                        if custom_date > today - timedelta(days=3):
                                            return "Transplanting of Seedlings"
                                        
                                        else:
                                            if custom_date > today - timedelta(days=730):
                                                return "Recommend Activity"
                                            else:
                                                return "Harvesting"
                                    else:
                                        return "Transplanting of Seedlings"
                            else:
                                return "Application of fertilizer"
                    else:
                        return "Field Lay outing & Holing"
            else:
                return "Weeding"
    else:
        return "Land Preparation"

@router.post("/locations/new")
async def create_location(loc: Locations):
        
    API_KEY = os.environ.get('GOOGLEMAPS_API_KEY')

    # Create a client object with your API key
    client = googlemaps.Client(key=API_KEY)

    # Geocode an address
    geocode_result = client.geocode(loc.locations)

    # Get the latitude and longitude from the geocode result
    lat = geocode_result[0]["geometry"]["location"]["lat"]
    lng = geocode_result[0]["geometry"]["location"]["lng"]

    filterQuery = locations.select().where(
            and_(
                locations.c.locations == loc.locations
            )   
        )
    if not await database.fetch_all(filterQuery):
        
        query = locations.insert().values(
                    locations=loc.locations, link=loc.link, lat=str(lat), lng=str(lng), is_trained=False
                    )
        await database.execute(query)

        return {"status" : 201, "message" : "New Locations Created"}
    else:
        return {"status" : 400, "message" : "Locations already exists"}

@router.get("/locations", response_model=List[LocationsResponse])
async def get_locations():
    query = locations.select()
    return await database.fetch_all(query)

@router.get("/recommend-activity/train={train}/id={id}")
async def recommend_activity(train: bool,id: int):
    query = locations.select().where(locations.c.id==id)
    link = await database.fetch_one(query)
    predict = Predict(train=link.is_trained, link=link.link, lat=link.lat, lng=link.lng)
    current_date = datetime.now()
    res = []
    past_forecast = openmeteo_datasets(lat=link.lat, lng=link.lng)
    forecast_5_days_ago = []
    days = []
    for forecast in past_forecast:
        forecast_5_days_ago.append([forecast['Temp Out'], forecast['Out Hum'], forecast['Dew Pt.'], forecast['Wind Speed']])

    for idx, x in enumerate(forecast_5_days_ago[-5:]):
        
        result = predict.predict_activiy(params=np.array([x]))
        
        if current_date.date()  not in days:
            days.append(current_date.date())
        
        # get the date 5 days from the current date
        five_days_from_now = current_date + timedelta(days=idx + 1)

        # extract only the date portion
        five_days_from_now_date = five_days_from_now.date()

        if len(days) != 5:
            days.append(five_days_from_now_date)
    
    for five_days_from_now_date in days:
        filterQuery = predictions.select().where(
            and_(
                predictions.c.start == five_days_from_now_date,
                predictions.c.end == five_days_from_now_date
            )
        )
        activity = await recommend_activity_checker(False, five_days_from_now)
        if not await database.fetch_all(filterQuery):
            # print the result
            if activity != "Recommend Activity":
                query = predictions.insert().values(
                    title=activity, start=five_days_from_now_date, end=five_days_from_now_date,
                    temperature=str(round(result['temperature'])), out_hum=str(round(result['humidity'])), dew_pt=str(round(result['dew_pt'])), wind_speed=str(round(result['wind_speed']))
                    )
                await database.execute(query)
            elif activity == "Recommend Activity":
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



@router.post("/recommend-activity/custom/train={train}/id={id}")
async def custom_recommend_activity(train: bool,id: int, payload: CustomDateprediction):
    with engine.connect() as conn:
            conn.execute(predictions.delete())
    query = locations.select().where(locations.c.id==id)
    link = await database.fetch_one(query)
    predict = Predict(train=link.is_trained, link=link.link, lat=link.lat, lng=link.lng)
    current_date = payload.date
    res = []
    past_forecast = openmeteo_datasets(lat=link.lat, lng=link.lng)
    forecast_5_days_ago = []
    days = []

    for forecast in past_forecast:
        forecast_5_days_ago.append([forecast['Temp Out'], forecast['Out Hum'], forecast['Dew Pt.'], forecast['Wind Speed']])
    for idx, x in enumerate(forecast_5_days_ago[-5:]):
        
        result = predict.predict_activiy(params=np.array([x]))

        if current_date not in days:
            days.append(current_date)

        # get the date 5 days from the current date
        five_days_from_now = current_date + timedelta(days=idx + 1)

        # extract only the date portion
        five_days_from_now_date = five_days_from_now

        if len(days) != 5:
            days.append(five_days_from_now_date)
    
    for five_days_from_now_date in days:
        filterQuery = predictions.select().where(
            and_(
                predictions.c.start == five_days_from_now_date,
                predictions.c.end == five_days_from_now_date
            )
        )
        activity = await recommend_activity_checker(True, five_days_from_now)

        if not await database.fetch_all(filterQuery):
            # print the result
            if activity != "Recommend Activity":
                query = predictions.insert().values(
                    title=activity, start=five_days_from_now_date, end=five_days_from_now_date,
                    temperature=str(round(result['temperature'])), out_hum=str(round(result['humidity'])), dew_pt=str(round(result['dew_pt'])), wind_speed=str(round(result['wind_speed']))
                    )
                await database.execute(query)
            elif activity == "Recommend Activity":
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


@router.delete("/predictions/reset")
async def delete_all_predictions():
    try:
        with engine.connect() as conn:
            conn.execute(predictions.delete())
        return {"success": True}
    except Exception as e:
        return {"error": str(e)}