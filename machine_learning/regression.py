import joblib
import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
from sklearn.model_selection import train_test_split
from sklearn.metrics import r2_score, mean_squared_error
from sklearn.linear_model import LinearRegression, LogisticRegression


from machine_learning.datasets import Datasets

class RegressionModel:
    
    def get_dataset(self):
        return Datasets()
    
    def rmse(self, y_true, y_pred):
        return np.sqrt(np.mean((y_true - y_pred)**2))
    
    def weather_forecast_regression(self):
        df = pd.DataFrame(self.get_dataset().historical_weather_datasets())

        features = ['Temp Out', 'Out Hum', 'Dew Pt.', 'Wind Speed']
        models = {}

        for target in features:
            X = df[['Temp Out', 'Out Hum', 'Dew Pt.', 'Wind Speed']]
            Y = df[target]

            x_train, x_test, y_train, y_test = train_test_split(X, Y, test_size=0.2, random_state=42)
            clf = LinearRegression()
            clf.fit(x_train, y_train)
            prediction = clf.predict(x_test)
            r2 = r2_score(y_test, prediction)
            mse = mean_squared_error(y_test, prediction)
            model_name = target.lower().replace(" ", "_").replace(".", "")
            self.save_trained_model(name=model_name, model=clf)
            models[target] = clf
        return models
    
    def farming_activity_regression(self):
        dataset = self.get_dataset().farming_activity_datasets()
        X = dataset[["Temperature", "Humidity", "Wind Speed", "Dew Point"]]
        y = dataset["Farming Activity"]
        # Fit the logistic regression model to the data
        model = LogisticRegression(penalty='l1', dual=False, C=0.1, fit_intercept=True, solver='saga', 
                                intercept_scaling=10.0, tol=1e-4, class_weight='balanced', max_iter=100, 
                                multi_class='multinomial', warm_start=True, n_jobs=-1)
        model.fit(X, y)
        self.save_trained_model(name="farming_datasets", model=model)
        return model
        
    def save_trained_model(self, name, model):
        joblib.dump(model, f'{name}.joblib')
            
            
    def load_trained_model(self, name):
        return joblib.load(f'{name}.joblib')
        

