import pandas as pd
import numpy as np
from sklearn.linear_model import LinearRegression

def prepare_features(series, lags=3):
    df = pd.DataFrame({"y": series})
    for i in range(1, lags + 1):
        df[f"lag_{i}"] = df["y"].shift(i)
    df = df.dropna()
    return df

def ml_forecast(series, periods=3, lags=3):
    """
    ML-based forecast with fallback for short series.
    series: pandas Series indexed by time (month)
    periods: number of future periods to forecast
    lags: number of lag features
    """
    series = series.copy().reset_index(drop=True)

    # If series too short, fallback to mean
    if len(series) <= lags:
        fallback = pd.Series([series.mean()]*periods)
        return fallback

    model = LinearRegression()
    forecast_values = []

    for _ in range(periods):
        features = prepare_features(series, lags=lags)
        X = features.drop(columns=["y"])
        y = features["y"]

        # Extra safety check
        if len(X) == 0:
            forecast_values.append(series.mean())
            series = pd.concat([series, pd.Series([series.mean()])])
            continue

        model.fit(X, y)

        last_lags = series.iloc[-lags:][::-1].values.reshape(1, -1)
        prediction = model.predict(last_lags)[0]

        forecast_values.append(prediction)
        series = pd.concat([series, pd.Series([prediction])], ignore_index=True)

    return pd.Series(forecast_values)
