from flask import Flask, request, jsonify, render_template
import pandas as pd
import numpy as np
from pipeline.data_fetcher import fetch_stock_data, fetch_news_sentiment
from pipeline.feature_engineering import add_technical_indicators
from pipeline.sentiment_analyzer import get_sentiment_score
from pipeline.predictor import train_and_predict
import json

app = Flask(__name__)

@app.route('/')
def index():
    return render_template('index.html')

# Search mapping for common inputs
TICKER_MAPPING = {
    'TESLA': 'TSLA',
    'APPLE': 'AAPL',
    'RELIANCE': 'RELIANCE.NS',
    'MICROSOFT': 'MSFT',
    'AMAZON': 'AMZN',
    'TCS': 'TCS.NS',
    'GOOGLE': 'GOOGL',
    'ALPHABET': 'GOOGL',
    'META': 'META',
    'FACEBOOK': 'META',
    'NVIDIA': 'NVDA',
    'NETFLIX': 'NFLX',
}

COMPANY_NAMES = {
    'TSLA': 'Tesla, Inc.',
    'AAPL': 'Apple Inc.',
    'RELIANCE.NS': 'Reliance Industries Limited',
    'MSFT': 'Microsoft Corporation',
    'AMZN': 'Amazon.com, Inc.',
    'TCS.NS': 'Tata Consultancy Services Limited',
    'GOOGL': 'Alphabet Inc.',
    'GOOG': 'Alphabet Inc.',
    'NVDA': 'NVIDIA Corporation',
    'META': 'Meta Platforms, Inc.',
    'NFLX': 'Netflix, Inc.',
}

@app.route('/predict', methods=['POST'])
def predict():
    try:
        data = request.get_json()
        input_ticker = data.get('ticker', '').strip().upper()
        if not input_ticker:
            return jsonify({'error': 'Ticker or company name is required'}), 400

        # Map input name to ticker if exists, otherwise use as ticker
        ticker = TICKER_MAPPING.get(input_ticker, input_ticker)

        # Step 1: Fetch stock data
        df = fetch_stock_data(ticker)
        if df.empty:
            return jsonify({'error': f'No data found for symbol "{ticker}"'}), 404
        
        current_price = df['Close'].iloc[-1]
        
        # Calculate price change percent compared to previous day's close
        price_change_percent = 0.0
        if len(df) > 1:
            prev_price = df['Close'].iloc[-2]
            price_change_percent = ((current_price - prev_price) / prev_price) * 100

        # Resolve company name
        company_name = COMPANY_NAMES.get(ticker)
        if not company_name:
            try:
                import yfinance as yf
                stock = yf.Ticker(ticker)
                company_name = stock.info.get('longName', ticker)
            except Exception:
                company_name = f"{ticker} Equity"
        
        # Step 2: Fetch and Analyze News Sentiment
        news_headlines = fetch_news_sentiment(ticker)
        sentiment_score, sentiment_label = get_sentiment_score(news_headlines)
        
        # Step 3: Feature Engineering
        df_with_features = add_technical_indicators(df.copy())
        if len(df_with_features) < 10:
            return jsonify({'error': f'Insufficient historical data for symbol "{ticker}" to perform predictions.'}), 400
        
        # Step 4: Model Prediction
        technical_prediction, probability = train_and_predict(df_with_features)
        
        # Step 5: Ensemble Prediction (Technical 60% + Sentiment 40%)
        # Sentiment is treated as an independent signal — it can override technical prediction
        sentiment_prediction = 1 if sentiment_score > 0.51 else 0

        if not news_headlines:
            # No news available — rely purely on technical prediction
            ensemble_prediction = technical_prediction
            ensemble_explanation = f"Technical indicators predict {'upward' if technical_prediction == 1 else 'downward'} movement. No news data available for sentiment analysis."
        else:
            # Weighted score: Technical 60%, Sentiment 40%
            technical_weight = 0.6
            sentiment_weight = 0.4
            weighted_score = (technical_prediction * technical_weight) + (sentiment_prediction * sentiment_weight)

            # RISE only if weighted score >= 0.6 (i.e., at least technical must agree)
            ensemble_prediction = 1 if weighted_score >= 0.6 else 0

            # Build a clear explanation reflecting any conflict
            tech_direction = 'upward' if technical_prediction == 1 else 'downward'
            sent_direction = sentiment_label.lower()

            if technical_prediction == sentiment_prediction:
                ensemble_explanation = (
                    f"Both technical indicators and market sentiment agree on "
                    f"{'positive' if technical_prediction == 1 else 'negative'} outlook. "
                    f"Technical signals predict {tech_direction} movement; sentiment is {sent_direction}."
                )
            else:
                # Conflict — explain which signal won
                winner = "Technical analysis" if technical_prediction == ensemble_prediction else "Market sentiment"
                ensemble_explanation = (
                    f"⚠️ Mixed signals detected. Technical indicators predict {tech_direction} movement, "
                    f"but market sentiment is {sent_direction} based on recent news. "
                    f"{winner} has the higher weight in the final prediction."
                )

        # Step 6: Prepare data for charts
        history_data = df.tail(100) # Last 100 days for chart
        chart_data = {
            'dates': history_data.index.strftime('%Y-%m-%d').tolist(),
            'prices': history_data['Close'].tolist(),
            'sma20': history_data['Close'].rolling(window=20).mean().fillna(0).tolist(),
            'sma50': history_data['Close'].rolling(window=50).mean().fillna(0).tolist()
        }
        
        result = {
            'ticker': ticker,
            'companyName': company_name,
            'currentPrice': round(current_price, 2),
            'priceChangePercent': round(price_change_percent, 2),
            'prediction': ensemble_prediction,
            'predictionLabel': 'Rise 📈' if ensemble_prediction == 1 else 'Fall 📉',
            'confidence': round(probability if technical_prediction == 1 else (1 - probability), 4) * 100,
            'technicalPrediction': technical_prediction,
            'sentimentPrediction': sentiment_prediction,
            'sentimentScore': round(sentiment_score, 2),
            'sentimentLabel': sentiment_label,
            'explanation': ensemble_explanation,
            'chartData': chart_data,
            'news': news_headlines
        }
        
        return jsonify(result)
    except Exception as e:
        print(f"Error during prediction: {e}")
        return jsonify({'error': str(e)}), 500


@app.route('/predict-alternative', methods=['POST'])
def predict_alternative():
    """
    ARCHITECTURE 2: Confirmation Engine
    Logic: OR operation between 1-day and 3-day sentiment, then AND with technical signal
    Results: BUY, NEUTRAL, or NOT BUY
    """
    try:
        data = request.get_json()
        input_ticker = data.get('ticker', '').strip().upper()
        if not input_ticker:
            return jsonify({'error': 'Ticker or company name is required'}), 400

        ticker = TICKER_MAPPING.get(input_ticker, input_ticker)

        # Step 1: Fetch stock data
        df = fetch_stock_data(ticker)
        if df.empty:
            return jsonify({'error': f'No data found for symbol "{ticker}"'}), 404

        # Step 2: Feature Engineering
        df_with_features = add_technical_indicators(df.copy())
        if len(df_with_features) < 10:
            return jsonify({'error': f'Insufficient historical data for symbol "{ticker}".'}), 400

        # Step 3: Fetch News Sentiment
        news_headlines = fetch_news_sentiment(ticker)
        sentiment_score, sentiment_label = get_sentiment_score(news_headlines)

        # Step 4: Extract latest indicator values for technical signal
        latest_idx = len(df_with_features) - 1
        latest_close    = float(df_with_features['Close'].iloc[latest_idx])
        latest_sma20    = float(df_with_features['SMA20'].iloc[latest_idx])
        latest_sma50    = float(df_with_features['SMA50'].iloc[latest_idx])
        latest_macd     = float(df_with_features['MACD'].iloc[latest_idx])
        latest_macd_sig = float(df_with_features['MACD_SIGNAL'].iloc[latest_idx])
        latest_rsi      = float(df_with_features['RSI'].iloc[latest_idx])

        # Debug: Print indicator values
        print(f"DEBUG - {ticker} indicators:")
        print(f"  Close: {latest_close}, SMA20: {latest_sma20}, SMA50: {latest_sma50}")
        print(f"  MACD: {latest_macd}, MACD_Signal: {latest_macd_sig}, RSI: {latest_rsi}")

        # ── TECHNICAL SIGNAL CALCULATION ─────────────────────────────────────
        # Technical signal is 1 if at least 1 of 2 trend indicators are bullish
        trend_signals = 0
        trend_details = []

        # 1. SMA20 vs SMA50 (Golden Cross)
        if latest_sma20 > latest_sma50:
            trend_signals += 1
            trend_details.append("SMA20 > SMA50 (Golden Cross) ✓")
        else:
            trend_details.append("SMA20 < SMA50 (Death Cross) ✗")

        # 2. MACD Analysis
        if latest_macd > latest_macd_sig:
            trend_signals += 1
            trend_details.append("MACD > Signal ✓")
        else:
            trend_details.append("MACD < Signal ✗")

        # Technical signal = 1 if both trend indicators are bullish
        technical_signal = 1 if trend_signals >= 2 else 0

        # ── SENTIMENT SIGNAL CALCULATION ────────────────────────────────────
        # 1-day sentiment (current)
        sentiment_1day = 1 if sentiment_score > 0.5 else 0

        # 3-day sentiment (simulated - using same sentiment with slightly lower threshold)
        # In production, you would fetch 3-day historical sentiment
        sentiment_3day = 1 if sentiment_score > 0.45 else 0

        # ── OR OPERATION: 1-day OR 3-day sentiment ────────────────────────────
        sentiment_confirmation = sentiment_1day | sentiment_3day  # Bitwise OR

        # ── AND OPERATION: Technical AND Sentiment_Confirmation ───────────────
        final_output = technical_signal & sentiment_confirmation  # Bitwise AND

        # ── FINAL RESULT LOGIC ─────────────────────────────────────────────────
        if final_output == 1:
            final_result = "BUY SIGNAL"
            final_signal = "BUY SIGNAL 🚀"
            signal_description = "Technical and sentiment confirmation aligned."
        else:
            final_result = "NO BUY SIGNAL"
            final_signal = "NO BUY SIGNAL ⚠️"
            signal_description = "Confirmation conditions not met."

        result = {
            'ticker': ticker,
            'technicalSignal': technical_signal,
            'sentiment1Day': sentiment_1day,
            'sentiment3Day': sentiment_3day,
            'sentimentConfirmation': sentiment_confirmation,
            'finalOutput': final_output,
            'finalResult': final_result,
            'finalSignal': final_signal,
            'signalDescription': signal_description,
            'trendDetails': trend_details,
            'sentimentScore': round(sentiment_score, 2),
            'sentimentLabel': sentiment_label,
            'rsi': round(latest_rsi, 2),
            'macd': round(latest_macd, 4),
            'sma20': round(latest_sma20, 2),
            'sma50': round(latest_sma50, 2),
        }

        return jsonify(result)
    except Exception as e:
        print(f"Error during confirmation engine prediction: {e}")
        return jsonify({'error': str(e)}), 500

if __name__ == '__main__':
    app.run(debug=True, port=5000)
