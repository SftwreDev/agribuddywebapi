import numpy as np
from machine_learning.regression import RegressionModel

class Predict:
    
    def __init__(self, train: bool, link: str, lat: str, lng: str):
        self.train = train
        self.link = link
        self.lat = lat
        self.lng = lng
        
    def init_model(self):
        return RegressionModel(self.link, self.lat, self.lng)
    
    def predict_forecast(self, params):
        # self.train = False
        regression_model = self.init_model()
        features = ['Temp Out', 'Out Hum', 'Dew Pt.', 'Wind Speed']
        result = []
        for target in features:     
            model_name = target.lower().replace(" ", "_").replace(".", "")
            if self.train:
                print("<=================== Loading weather forecast trained model ===================>")
                model = regression_model.load_trained_model(name=f"{model_name}_polynomial")
                print(params)
                predict = model.predict(params)
                result.append(predict[0])
            else:
                print("<=================== Start weather forecast training ===================>")
                regression_model.weather_forecast_polynomial_regression()
                model = regression_model.load_trained_model(name=f"{model_name}_polynomial")
                predict = model.predict(params)
                result.append(predict[0])
        return result
    
    def predict_activiy(self, params):
        # self.train = False
        activity = {1: 'Weed Removal', 2: 'Fertilizer application', 3: 'Pest Control', 
         4: 'Water management'}
            
        regression_model = self.init_model()
        if self.train:
            print("<=================== Loading farming activity trained model ===================>")
            model = regression_model.load_trained_model(name="farming_datasets")
            weather_data = self.predict_forecast(params)
            predict_activity = model.predict([weather_data])
            return  {"title" : activity[predict_activity[0]], "temperature" : weather_data[0], "humidity" : weather_data[1], "dew_pt" : weather_data[2], "wind_speed" : weather_data[3]}
        else:
            print("<=================== Start farming activity training ===================>")
            model = regression_model.farming_activity_regression()
            model = regression_model.load_trained_model(name="farming_datasets")
            weather_data = self.predict_forecast(params)
            predict_activity = model.predict([weather_data])
            return {"title" : activity[predict_activity[0]], "temperature" : weather_data[0], "humidity" : weather_data[1], "dew_pt" : weather_data[2], "wind_speed" : weather_data[3]}