import time, os
import pandas as pd
from sklearn.ensemble import RandomForestClassifier
from sklearn.metrics import accuracy_score
from sklearn.model_selection import train_test_split
from category_encoders.target_encoder import TargetEncoder

os.makedirs("output", exist_ok=True)
start = time.time()

data = pd.read_csv("input/data.csv")
X = data.iloc[:, :-1]
y = data.iloc[:, -1]

categorical_cols = X.select_dtypes(include=["object", "category"]).columns.tolist()
if categorical_cols:
    encoder = TargetEncoder(cols=categorical_cols)
    X = encoder.fit_transform(X, y)

X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.2, random_state=42)
model = RandomForestClassifier()
model.fit(X_train, y_train)
y_pred = model.predict(X_test)

pd.DataFrame({"prediction": y_pred}).to_csv("output/predictions_script4.csv", index=False)
with open("output/metrics_script4.txt", "w") as f:
    f.write(f"Accuracy: {accuracy_score(y_test, y_pred):.4f}\n")
with open("output/timing_script4.txt", "w") as f:
    f.write(f"{time.time() - start:.2f} seconds\n")
