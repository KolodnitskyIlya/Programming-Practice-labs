import pandas as pd
from sklearn.metrics import classification_report

y_true = pd.read_csv("input/raw_data.csv")["target"]
y_pred = pd.read_csv("output/final_predictions.csv")["prediction"]

print(classification_report(y_true.iloc[-len(y_pred):], y_pred))
