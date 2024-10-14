# test.py
import pytest
import pandas as pd
from ml import MLSystem

def test_load_data():
    ml_system = MLSystem()
    data = ml_system.load_data('/opt/airflow/dags/data/train.csv')
    assert isinstance(data, pd.DataFrame)

def test_preprocess_data():
    ml_system = MLSystem()
    data = pd.DataFrame({
        'feature1': [1, 2, 3, 4],
        'target': [0, 1, 0, 1]
    })
    X_train, X_test, y_train, y_test = ml_system.preprocess_data(data, 'target')
    assert len(X_train) == 3
    assert len(y_train) == 3

def test_train_and_evaluate():
    ml_system = MLSystem()
    data = pd.DataFrame({
        'feature1': [1, 2, 3, 4],
        'target': [0, 1, 0, 1]
    })
    X_train, X_test, y_train, y_test = ml_system.preprocess_data(data, 'target')
    ml_system.train(X_train, y_train)
    accuracy = ml_system.evaluate(X_test, y_test)
    assert accuracy >= 0