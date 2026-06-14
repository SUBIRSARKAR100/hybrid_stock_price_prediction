import ta
import pandas as pd
import numpy as np

def add_technical_indicators(df):
    """
    Adds technical indicators to the dataframe as per the notebook pipeline.
    """
    # Momentum
    df['RSI'] = ta.momentum.rsi(close=df['Close'], window=14)
    
    # Trend
    df['SMA20'] = ta.trend.sma_indicator(close=df['Close'], window=20)
    df['SMA50'] = ta.trend.sma_indicator(close=df['Close'], window=50)
    df['EMA20'] = ta.trend.ema_indicator(close=df['Close'], window=20)
    df['EMA50'] = ta.trend.ema_indicator(close=df['Close'], window=50)
    
    macd = ta.trend.MACD(close=df['Close'])
    df['MACD'] = macd.macd()
    df['MACD_SIGNAL'] = macd.macd_signal()
    
    # Volatility
    bb = ta.volatility.BollingerBands(close=df['Close'])
    df['BB_UPPER'] = bb.bollinger_hband()
    df['BB_LOWER'] = bb.bollinger_lband()
    df['ATR'] = ta.volatility.AverageTrueRange(high=df['High'], low=df['Low'], close=df['Close']).average_true_range()
    
    # Volume
    df['OBV'] = ta.volume.OnBalanceVolumeIndicator(close=df['Close'], volume=df['Volume']).on_balance_volume()
    
    # Extra features
    df['Daily_Return'] = df['Close'].pct_change()
    df['Price_Range'] = df['High'] - df['Low']
    df['Volume_Change'] = df['Volume'].pct_change()
    
    # Drop rows with NaN values created by indicators
    df.dropna(inplace=True)
    return df
