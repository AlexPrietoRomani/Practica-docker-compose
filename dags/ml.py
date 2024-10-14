# ml.py
import pandas as pd
import numpy as np
from sklearn.model_selection import train_test_split
from sklearn.ensemble import RandomForestClassifier
from sklearn.metrics import accuracy_score
import joblib

class MLSystem:
    def __init__(self, model=None):
        self.model = model if model else RandomForestClassifier()

    def load_data(self, filepath: str):
        """Carga los datos desde un archivo CSV."""
        data = pd.read_csv(filepath)
        return data

    def preprocess_data(self, data: pd.DataFrame, target_column: str):
        """Preprocesa los datos y separa características y la columna objetivo."""
        X = data.drop(columns=[target_column])
        y = data[target_column]
        return train_test_split(X, y, test_size=0.2, random_state=42)

    def train(self, X_train, y_train):
        """Entrena el modelo."""
        self.model.fit(X_train, y_train)

    def evaluate(self, X_test, y_test):
        """Evalúa el modelo."""
        predictions = self.model.predict(X_test)
        return accuracy_score(y_test, predictions)

    def save_model(self, file_name: str):
        """Guarda el modelo entrenado."""
        joblib.dump(self.model, file_name)

    def load_model(self, file_name: str):
        """Carga un modelo desde un archivo."""
        self.model = joblib.load(file_name)