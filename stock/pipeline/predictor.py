import pandas as pd
import numpy as np
from xgboost import XGBClassifier
from sklearn.preprocessing import StandardScaler
import joblib
import os

def train_and_predict(df):
    """
    Trains the XGBoost model on the dataframe and predicts the outcome for the latest data point.
    """
    features = [
        'Open', 'High', 'Low', 'Close', 'Volume', 'RSI', 'SMA20', 'SMA50', 
        'EMA20', 'EMA50', 'MACD', 'MACD_SIGNAL', 'BB_UPPER', 'BB_LOWER', 
        'ATR', 'OBV', 'Daily_Return', 'Price_Range', 'Volume_Change'
    ]
    
    # Create target (1 if tomorrow's close is higher than today's, NaN for the last row)
    tomorrow_close = df['Close'].shift(-1)
    df['Target'] = (tomorrow_close > df['Close']).astype(float)
    df.iloc[-1, df.columns.get_loc('Target')] = np.nan
    
    # Prepare data
    X = df[features]
    
    # Store latest features for prediction before dropping last row
    latest_features = X.iloc[[-1]]
    
    # Drop rows with NaN targets (the last row)
    df_train = df.dropna(subset=['Target'])
    X_train = df_train[features]
    y_train = df_train['Target'].astype(int)
    
    # Model parameters from notebook
    model = XGBClassifier(
        n_estimators=1000,
        learning_rate=0.01,
        max_depth=8,
        min_child_weight=3,
        subsample=0.8,
        colsample_bytree=0.8,
        gamma=0.1,
        objective='binary:logistic',
        eval_metric='logloss',
        random_state=42
    )
    
    # Fit model
    model.fit(X_train, y_train)
    
    # Predict for tomorrow
    prediction = model.predict(latest_features)[0]
    probability = model.predict_proba(latest_features)[0][1]
    
    return int(prediction), float(probability)
