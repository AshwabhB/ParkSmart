import pandas as pd
import numpy as np
from sklearn.neural_network import MLPRegressor
from sklearn.preprocessing import StandardScaler
from sklearn.model_selection import train_test_split
import joblib
from datetime import datetime
import os

SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))
ROOT_DIR = os.path.dirname(SCRIPT_DIR)
DEFAULT_MODEL_DIR = os.path.join(SCRIPT_DIR, 'models')


class ParkingPredictor:
    def __init__(self):
        self.models = {}
        self.scalers = {}
        self.garages = ['North Garage', 'South Garage', 'West Garage', 'South Campus Garage']

    def load_and_preprocess_data(self):
        all_data = []
        for garage in self.garages:
            file_name = f"{garage.replace(' ', '_').lower()}.csv"
            file_path = os.path.join(ROOT_DIR, file_name)
            try:
                df = pd.read_csv(file_path)
                df['Garage Name'] = garage
                all_data.append(df)
            except FileNotFoundError:
                print(f"Warning: {file_path} not found, skipping...")
                continue

        if not all_data:
            raise ValueError("No data files found!")

        df = pd.concat(all_data)
        df['Timestamp'] = pd.to_datetime(df['Timestamp'])
        df['Day'] = df['Timestamp'].dt.day_name()
        df['Hour'] = df['Timestamp'].dt.hour
        df['DayOfWeek'] = df['Timestamp'].dt.dayofweek

        day_dummies = pd.get_dummies(df['Day'], prefix='Day')
        df = pd.concat([df, day_dummies], axis=1)

        garage_dummies = pd.get_dummies(df['Garage Name'], prefix='Garage')
        df = pd.concat([df, garage_dummies], axis=1)

        return df

    def prepare_features(self, df):
        feature_columns = ['Hour', 'DayOfWeek'] + \
                          [col for col in df.columns if col.startswith('Day_')] + \
                          [col for col in df.columns if col.startswith('Garage_')]
        X = df[feature_columns]
        y = df['Occupancy']
        return X, y

    def train_models(self):
        df = self.load_and_preprocess_data()
        X, y = self.prepare_features(df)

        for garage in self.garages:
            print(f"\nTraining model for {garage}")
            print("-" * 50)

            garage_mask = df['Garage Name'] == garage
            X_garage = X[garage_mask]
            y_garage = y[garage_mask]

            X_train_garage, X_test_garage, y_train_garage, y_test_garage = train_test_split(
                X_garage, y_garage, test_size=0.2, random_state=42
            )

            scaler = StandardScaler()
            X_train_garage_scaled = scaler.fit_transform(X_train_garage)
            X_test_garage_scaled = scaler.transform(X_test_garage)

            model = MLPRegressor(
                hidden_layer_sizes=(100, 50),
                activation='relu',
                solver='adam',
                max_iter=1000,
                random_state=42,
                verbose=True
            )

            model.fit(X_train_garage_scaled, y_train_garage)

            train_score = model.score(X_train_garage_scaled, y_train_garage)
            test_score = model.score(X_test_garage_scaled, y_test_garage)

            train_pred = model.predict(X_train_garage_scaled)
            test_pred = model.predict(X_test_garage_scaled)
            train_mse = np.mean((y_train_garage - train_pred) ** 2)
            test_mse = np.mean((y_test_garage - test_pred) ** 2)

            print(f"Training R² Score: {train_score:.4f}")
            print(f"Testing R² Score: {test_score:.4f}")
            print(f"Training MSE: {train_mse:.2f}")
            print(f"Testing MSE: {test_mse:.2f}")

            self.models[garage] = model
            self.scalers[garage] = scaler

    def predict_occupancy(self, garage, date, hour):
        if garage not in self.models:
            raise ValueError(f"No model found for {garage}")

        day_name = date.strftime("%A")
        day_of_week = date.weekday()

        pred_data = pd.DataFrame()
        pred_data['Hour'] = [hour]
        pred_data['DayOfWeek'] = [day_of_week]

        for day in sorted(['Monday', 'Tuesday', 'Wednesday', 'Thursday', 'Friday', 'Saturday', 'Sunday']):
            pred_data[f'Day_{day}'] = 1 if day == day_name else 0

        for g in sorted(self.garages):
            pred_data[f'Garage_{g}'] = 1 if g == garage else 0

        X_pred_scaled = self.scalers[garage].transform(pred_data)
        prediction = self.models[garage].predict(X_pred_scaled)[0]
        prediction = max(0, min(100, prediction))
        return prediction

    def get_best_garage(self, date, hour):
        predictions = {}
        for garage in self.garages:
            predictions[garage] = self.predict_occupancy(garage, date, hour)

        best_garage = min(predictions.items(), key=lambda x: x[1])

        alternatives = [
            (garage, occ) for garage, occ in predictions.items() if occ < 90
        ]
        alternatives.sort(key=lambda x: x[1])

        return predictions, best_garage, alternatives

    def save_models(self, directory=None):
        if directory is None:
            directory = DEFAULT_MODEL_DIR
        os.makedirs(directory, exist_ok=True)
        for garage in self.garages:
            key = garage.lower().replace(' ', '_')
            joblib.dump(self.models[garage], os.path.join(directory, f'{key}_model.joblib'))
            joblib.dump(self.scalers[garage], os.path.join(directory, f'{key}_scaler.joblib'))

    def load_models(self, directory=None):
        if directory is None:
            directory = DEFAULT_MODEL_DIR
        for garage in self.garages:
            key = garage.lower().replace(' ', '_')
            model_path = os.path.join(directory, f'{key}_model.joblib')
            scaler_path = os.path.join(directory, f'{key}_scaler.joblib')
            if os.path.exists(model_path) and os.path.exists(scaler_path):
                self.models[garage] = joblib.load(model_path)
                self.scalers[garage] = joblib.load(scaler_path)
            else:
                print(f"Warning: Model files not found for {garage}")


if __name__ == "__main__":
    predictor = ParkingPredictor()
    predictor.train_models()
    predictor.save_models()
