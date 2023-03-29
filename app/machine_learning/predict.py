import numpy as np

from machine_learning.regression import RegressionModel

class Predict:
    
    def __init__(self, train: bool):
        self.train = train
        
    def init_model(self):
        return RegressionModel()
    
    def predict_forecast(self, params):
        regression_model = self.init_model()
        features = ['Temp Out', 'Out Hum', 'Dew Pt.', 'Wind Speed']
        result = []
        for target in features:     
            model_name = target.lower().replace(" ", "_").replace(".", "")
            if not self.train:
                print("<=================== Loading weather forecast trained model ===================>")
                model = regression_model.load_trained_model(name=model_name)
                predict = model.predict(params)
                result.append(predict[0])
            else:
                print("<=================== Start weather forecast training ===================>")
                weather_forecast_regression = regression_model.weather_forecast_regression()
                model = regression_model.load_trained_model(name=model_name)
                predict = model.predict(params)
                result.append(predict[0])
        return result
    
    def predict_activiy(self, params):
        activity = {1: 'Acquisition of quality planting materials', 2: 'Land Preparation', 3: 'Field Lay outing', 
         4: 'Holing/ Hole preparation', 5: 'Transplanting of Seedlings', 6: 'Mulching', 7: 'Fertilization', 
         8: 'Water management', 9: 'Pruning', 10: 'Harvesting the cherries', 11: 'Processing the cherries', 
         12: 'Drying the Beans', 13: 'Milling the Beans', 14: 'Exporting the Beans'}
            
        regression_model = self.init_model()
        if not self.train:
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
            return activity[predict_activity[0]]