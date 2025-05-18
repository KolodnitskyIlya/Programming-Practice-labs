import pandas as pd
from sklearn.ensemble import GradientBoostingClassifier
from preprocessing import smart_encode
import os

def process_data(input_path, output_path):
    df = pd.read_csv(input_path).dropna()
    X, y = smart_encode(df)

    model = GradientBoostingClassifier()
    model.fit(X, y)

    preds = model.predict(X)
    pd.DataFrame({'prediction': preds}).to_csv(
        f"{output_path}/predictions_script5.csv", index=False)
