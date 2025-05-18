import pandas as pd
from sklearn.tree import DecisionTreeClassifier
from preprocessing import smart_encode
import os

def process_data(input_path, output_path):
    df = pd.read_csv(input_path).dropna()
    X, y = smart_encode(df)

    model = DecisionTreeClassifier()
    model.fit(X, y)

    preds = model.predict(X)
    pd.DataFrame({'prediction': preds}).to_csv(
        f"{output_path}/predictions_script6.csv", index=False)
