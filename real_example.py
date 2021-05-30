import pandas as pd
import numpy as np
from sklearn.linear_model import LinearRegression

# training data contains features and targets
def load_train_data():
    training_data = pd.read_csv("numerai_datasets/numerai_training_data.csv")
    training_data.set_index("id")
    return training_data

def load_tournament_data():
    tournament_data = pd.read_csv("numerai_datasets/numerai_tournament_data.csv")
    tournament_data.set_index("id", inplace=True)
    return tournament_data

def get_evaluation_data(tournament_data):
    return tournament_data[tournament_data['target'].notna()]

def get_prediction_data(tournament_data):
    return tournament_data[tournament_data['target'].isna()]

def get_feature_names(data):
    feature_names = [f for f in training_data.columns if "feature" in f]
    return feature_names

def create_and_train_model(training_data, feature_names):
    model = LinearRegression()
    model.fit(training_data[feature_names], training_data["target"])
    return model

def get_prediction(model, data, feature_names):
    return model.predict(data[feature_names])

def get_score(model, data, feature_names):
    X = data[feature_names]
    Y = data["target"]
    P = model.predict(X)
    score = np.corrcoef(P, Y)[0, 1]
    return score

def add_prediction(prediction_data, numpy_predictions):
    prediction_data = prediction_data[["target"]].copy()
    prediction_data["target"] = numpy_predictions
    return prediction_data

training_data = load_train_data()
feature_names = get_feature_names(training_data)
model = create_and_train_model(training_data, feature_names)
train_score = get_score(model, training_data, feature_names)
prediction = get_prediction(model, training_data, feature_names)

tournament_data = load_tournament_data()
evaluation_data = get_evaluation_data(tournament_data)
prediction_data = get_prediction_data(tournament_data)
predictions = get_prediction(model, tournament_data, feature_names)
prediction_df = add_prediction(tournament_data, predictions)
