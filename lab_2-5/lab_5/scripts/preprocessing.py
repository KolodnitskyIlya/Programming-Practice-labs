import pandas as pd
from sklearn.preprocessing import OneHotEncoder, StandardScaler
from sklearn.model_selection import KFold
from sklearn.compose import ColumnTransformer
from sklearn.pipeline import Pipeline
import numpy as np

def smart_encode(df, target_col='target'):
    X = df.drop(columns=[target_col])
    y = df[target_col]

    cat_cols = X.select_dtypes(include='object').columns.tolist()
    num_cols = X.select_dtypes(include=['int64', 'float64']).columns.tolist()

    low_card_cat = [col for col in cat_cols if df[col].nunique() <= 10]
    high_card_cat = [col for col in cat_cols if df[col].nunique() > 10]

    ohe = ColumnTransformer(
        transformers=[
            ('cat', OneHotEncoder(handle_unknown='ignore'), low_card_cat)
        ],
        remainder='passthrough'
    )

    X_low_encoded = ohe.fit_transform(X)

    for col in high_card_cat:
        global_mean = y.mean()
        kf = KFold(n_splits=5, shuffle=True, random_state=42)
        target_encoded = np.zeros(len(df))
        for train_idx, val_idx in kf.split(df):
            means = df.iloc[train_idx].groupby(col)[target_col].mean()
            target_encoded[val_idx] = df.iloc[val_idx][col].map(means).fillna(global_mean)
        X_low_encoded = np.hstack((X_low_encoded, target_encoded.reshape(-1, 1)))

    return X_low_encoded, y
