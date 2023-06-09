import joblib
import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
from sklearn.metrics import r2_score
from sklearn.model_selection import train_test_split
from sklearn.preprocessing import PolynomialFeatures
from sklearn.linear_model import LinearRegression, LogisticRegression
from sklearn.metrics import accuracy_score, precision_score, recall_score, f1_score

from machine_learning.datasets import Datasets

class RegressionModel:

    def __init__(self, link: str, lat: str, lng: str):
        self.link = link
        self.lat = lat
        self.lng = lng
    
    def get_dataset(self):
        return Datasets(self.link, self.lat, self.lng)
    
    def rmse_formula(self, predictions, targets):
        return np.sqrt(((predictions - targets) ** 2).mean())
    
    def weather_forecast_linear_regression(self):
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
            rmse = self.rmse_formula(prediction, y_test)
            print(f"RMSE : {rmse} | Regression Coefficient : {clf.coef_[1:]}")
            
            print(y_test)
            print(prediction)
            model_name = target.lower().replace(" ", "_").replace(".", "")
            self.save_trained_model(name=model_name, model=clf)
            models[target] = clf
        return models
    

    def weather_forecast_polynomial_regression(self):
        df = pd.DataFrame(self.get_dataset().historical_weather_datasets())

        features = ['Temp Out', 'Out Hum', 'Dew Pt.', 'Wind Speed']
        models = {}

        for target in features:
            X = df[['Temp Out', 'Out Hum', 'Dew Pt.', 'Wind Speed']]
            Y = df[target]

            x_train, x_test, y_train, y_test = train_test_split(X, Y, test_size=0.2, random_state=42)

            # Apply polynomial features to input variables
            poly_features = PolynomialFeatures(degree=1, include_bias=False)
            x_train_poly = poly_features.fit_transform(x_train)
            x_test_poly = poly_features.transform(x_test)

            # Fit a linear regression model to the polynomial features
            clf = LinearRegression(fit_intercept=True,copy_X=True, n_jobs=-1)
            clf.fit(x_train_poly, y_train)

            # Evaluate the model
            prediction = clf.predict(x_test_poly)
            rmse = self.rmse_formula(prediction, y_test)
            print(f"RMSE : {rmse} | Regression Coefficient : {clf.coef_[1:]}")

            # Save the trained model
            model_name = target.lower().replace(" ", "_").replace(".", "")
            self.save_trained_model(name=f"{model_name}_polynomial", model=clf)
            models[target] = clf

        return models
    
    def weather_forecast_logistic_regression(self):
        """
            Function for Weather Forecast using LogisticRegression.
            
            Output: ValueError: Unknown label type: 'continuous'
            Reason: The LogisticRegression class from scikit-learn is meant for 
                    binary classification problems not for regression problems. Since 
                    the target variables in this case are continuous, it's better 
                    to use a regression algorithm such as LinearRegression.
        """
        df = pd.DataFrame(self.get_dataset().historical_weather_datasets())
        
        features = ['Temp Out', 'Out Hum', 'Dew Pt.', 'Wind Speed']
        for target in features:
            X = df[['Temp Out', 'Out Hum', 'Dew Pt.', 'Wind Speed']]
            y = df[target]
            
            model = LogisticRegression(penalty='l1', dual=False, C=0.1, fit_intercept=True, solver='saga', 
                                intercept_scaling=10.0, tol=1e-4, class_weight='balanced', max_iter=100, 
                                multi_class='multinomial', warm_start=True, n_jobs=-1)
            
            model.fit(X, y)
            model_name = target.lower().replace(" ", "_").replace(".", "")
            self.save_trained_model(name=f"{model_name}_logistics", model=model)
            return model
    
    def farming_activity_regression(self):
        dataset = self.get_dataset().farming_activity_datasets()
        X = dataset[["Temperature", "Humidity", "Wind Speed", "Dew Point"]]
        y = dataset["Farming Activity"]
        # Fit the logistic regression model to the data
        model = LogisticRegression(penalty='l1', dual=False, C=0.1, fit_intercept=True, solver='saga', 
                                intercept_scaling=10.0, tol=1e-4, class_weight='balanced', max_iter=100, 
                                multi_class='multinomial', warm_start=True, n_jobs=-1)
        
        X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.2, random_state=42)

        model.fit(X_train, y_train)
        y_pred = model.predict(X_test)

        accuracy = accuracy_score(y_test, y_pred)
        precision = precision_score(y_test, y_pred, average='weighted')
        recall = recall_score(y_test, y_pred, average='weighted')
        f1 = f1_score(y_test, y_pred, average='weighted')

        print("Accuracy score:", accuracy)
        print("Precision score: ", precision)
        print("Recall score: {:.2f}".format(recall))
        print("F1 score:", f1)
        return model
        
    def save_trained_model(self, name, model):
        joblib.dump(model, f'{name}.joblib')
            
            
    def load_trained_model(self, name):
        return joblib.load(f'{name}.joblib')
        

