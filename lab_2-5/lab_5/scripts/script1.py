import sys
import time
import pandas as pd
from sklearn.linear_model import LogisticRegression
from sklearn.metrics import accuracy_score
from sklearn.model_selection import train_test_split
from category_encoders import TargetEncoder
import json

def run_model_from_csv(csv_text):
    start = time.time()
    from io import StringIO
    data = pd.read_csv(StringIO(csv_text))

    X = data.iloc[:, :-1]
    y = data.iloc[:, -1]

    categorical_cols = X.select_dtypes(include=["object", "category"]).columns.tolist()
    if categorical_cols:
        encoder = TargetEncoder(cols=categorical_cols)
        X = encoder.fit_transform(X, y)

    X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.2, random_state=42)
    model = LogisticRegression(max_iter=1000)
    model.fit(X_train, y_train)
    y_pred = model.predict(X_test)

    print(json.dumps({
        "model": "LogisticRegression",
        "accuracy": accuracy_score(y_test, y_pred),
        "time": round(time.time() - start, 2)
    }))

if __name__ == "__main__":
    csv_input = sys.stdin.read()
    run_model_from_csv(csv_input)
