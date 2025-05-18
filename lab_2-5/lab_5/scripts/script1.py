import pandas as pd
from sklearn.linear_model import LogisticRegression
from sklearn.preprocessing import StandardScaler
from preprocessing import smart_encode
import os

def process_data(input_path, output_path):
    df = pd.read_csv(input_path).dropna()
    X, y = smart_encode(df)

    X = StandardScaler().fit_transform(X)
    model = LogisticRegression(max_iter=200)
    model.fit(X, y)

    preds = model.predict(X)
    pd.DataFrame({'prediction': preds}).to_csv(
        f"{output_path}/predictions_script1.csv", index=False)
