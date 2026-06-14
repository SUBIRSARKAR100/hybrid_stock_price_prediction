import yfinance as yf
import pandas as pd
from datetime import datetime, timedelta

def fetch_stock_data(ticker, period="2y", interval="1d"):
    """
    Fetches historical stock data using yfinance.
    """
    stock = yf.Ticker(ticker)
    df = stock.history(period=period, interval=interval)
    return df

def fetch_news_sentiment(ticker):
    """
    Fetches news for the given ticker and returns news headlines.
    Uses yf.Search first for higher reliability.
    """
    try:
        search = yf.Search(ticker)
        news = search.news
        if not news:
            stock = yf.Ticker(ticker)
            news = stock.news
            
        if not news:
            return []
        headlines = [item['title'] for item in news[:5] if 'title' in item]
        return headlines
    except Exception as e:
        print(f"Error fetching news for {ticker}: {e}")
        return []
