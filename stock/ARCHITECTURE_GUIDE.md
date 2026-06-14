# Stock Prediction System - Two Architecture Guide

## 🎯 System Overview

This stock prediction system uses **TWO DIFFERENT ARCHITECTURES** to provide users with flexible prediction options:

### **Architecture 1: Main Prediction (Conservative)**
- **Type:** Technical + Sentiment Ensemble
- **Model:** XGBoost + News Sentiment Analysis
- **Logic:** Predicts BUY only if BOTH technical AND sentiment signals agree
- **Output:** "BUY 🟢" or "NOT BUY 🔴"
- **Risk Level:** Lower risk
- **Best For:** Conservative traders who want balanced analysis

### **Architecture 2: Alternative Prediction (Aggressive)**
- **Type:** Trend + Momentum Based
- **Model:** Pure technical analysis (no sentiment)
- **Logic:** Score-based approach using trend and momentum indicators
- **Output:** "RISE 📈" or "FALL 📉"
- **Risk Level:** Higher risk
- **Best For:** Aggressive trend followers

---

## 🔄 User Workflow

### Step 1: User Enters Stock Ticker
User opens web app and enters company name or ticker (e.g., "AAPL", "TESLA")

### Step 2: System Shows Architecture 1 Result
Main dashboard displays:
- **Prediction:** BUY or NOT BUY
- **Confidence Level:** 0-100%
- **Current Price:** Stock price
- **Market Sentiment:** Positive/Negative/Neutral
- **Latest News:** Top 5 headlines
- **Chart:** Historical price with SMA20 and SMA50

### Step 3: If Not Satisfied, Click "Confirmation Engine" Button
User can switch to Architecture 2 view

### Step 4: System Shows Architecture 2 Result
Alternative dashboard displays:
- **Prediction:** RISE or FALL
- **Confidence Level:** 0-100%
- **Trend Score:** 0-3 (based on SMA and price alignment)
- **Momentum Score:** 0-2.5 (based on RSI and price change)
- **Total Score:** Combined score
- **Indicators:** RSI, MACD, SMA20, SMA50
- **Details:** Breakdown of trend and momentum signals

---

## 🛠️ Technical Implementation

### Backend API Endpoints

#### `/predict` - Architecture 1 (Main Prediction)
```
POST /predict
Content-Type: application/json

Request:
{
    "ticker": "AAPL"
}

Response:
{
    "ticker": "AAPL",
    "prediction": 1,  // 1 = BUY, 0 = NOT BUY
    "predictionLabel": "BUY 🟢",
    "confidence": 75.5,
    "technicalPrediction": 1,
    "sentimentPrediction": 1,
    "sentimentScore": 0.65,
    "sentimentLabel": "Positive 📈",
    "chartData": {...},
    "news": [...]
}
```

#### `/predict-alternative` - Architecture 2 (Alternative Prediction)
```
POST /predict-alternative
Content-Type: application/json

Request:
{
    "ticker": "AAPL"
}

Response:
{
    "ticker": "AAPL",
    "prediction": 1,  // 1 = RISE, 0 = FALL
    "predictionLabel": "RISE 📈",
    "confidence": 68.5,
    "trendScore": 2.5,
    "momentumScore": 2.0,
    "totalScore": 4.5,
    "trendDetails": [...],
    "momentumDetails": [...],
    "rsi": 55.2,
    "macd": 0.0125,
    "sma20": 150.25,
    "sma50": 148.75,
    "outlook": "Uptrend"
}
```

### Data Flow Diagram

```
User Input (Ticker)
        ↓
[Fetch OHLCV Data] ← yfinance
        ↓
    ┌───┴───────────────────────────┐
    ↓                               ↓
[Architecture 1]            [Architecture 2]
(Technical+Sentiment)       (Trend+Momentum)
    ↓                               ↓
[XGBoost Model]         [Trend Score Analysis]
[News Sentiment]        [Momentum Analysis]
    ↓                               ↓
"BUY or NOT BUY"        "RISE or FALL"
Confidence: 50-100%     Confidence: 50-100%
```

---

## 📊 Architecture 1: Technical + Sentiment Ensemble (Main)

### Step 1: Data Fetching
```
- OHLCV: Open, High, Low, Close, Volume (2 years of daily data)
- News: Latest 5 headlines from yfinance news API
```

### Step 2: Feature Engineering
Technical indicators calculated:
- **Momentum:** RSI (14)
- **Trend:** SMA20, SMA50, EMA20, EMA50, MACD, MACD Signal
- **Volatility:** Bollinger Bands, ATR
- **Volume:** OBV
- **Custom:** Daily Return, Price Range, Volume Change

### Step 3: XGBoost Model Training
```
Features: 19 technical indicators
Target: 1 if tomorrow's close > today's close, else 0
Model Params:
  - n_estimators: 1000
  - learning_rate: 0.01
  - max_depth: 8
  - subsample: 0.8
  - colsample_bytree: 0.8
```

### Step 4: Sentiment Analysis
- Headlines analyzed using VADER (Valence Aware Dictionary and sEntiment Reasoner)
- Sentiment scores normalized to [0, 1]
- > 0.51 = Positive (UP), < 0.49 = Negative (DOWN)

### Step 5: Ensemble Logic
```
Prediction = BUY (1) if BOTH:
  - Technical prediction == UP (1)
  - Sentiment prediction == UP (1)
Otherwise = NOT BUY (0)
```

---

## 📈 Architecture 2: Trend + Momentum (Alternative)

### Trend Analysis (3 Factors)
1. **Price vs SMA20:** Is price above 20-day simple moving average?
2. **SMA20 vs SMA50:** Golden Cross (SMA20 > SMA50) indicates uptrend
3. **MACD Signal:** Is MACD above signal line (bullish momentum)?

Each factor = +1 if bullish, 0 if bearish

### Momentum Analysis (2.5 Factors)
1. **RSI Analysis:**
   - < 30: Oversold (+0.5)
   - > 70: Overbought (-0.5)
   - 30-70: Balanced (+0.5)

2. **5-Day Price Momentum:**
   - Price changed positively: +1.0
   - Price changed negatively: 0

### Scoring
```
Total Score = Trend Score (0-3) + Momentum Score (0-2.5)

Decision:
  - Score >= 3.5: RISE (1)
  - Score < 3.5: FALL (0)

Confidence = Total Score / 5.5 (normalized)
```

---

## 🔌 File Structure

```
stock/
├── app.py                      # Flask backend with both endpoints
├── Final.ipynb                 # Jupyter notebook documenting both architectures
├── requirements.txt            # Python dependencies
├── pipeline/
│   ├── data_fetcher.py        # Fetch OHLCV and news
│   ├── feature_engineering.py # Technical indicators
│   ├── predictor.py           # XGBoost model
│   └── sentiment_analyzer.py  # Sentiment analysis
├── static/
│   ├── css/
│   │   └── style.css          # Glassmorphic UI styles
│   └── js/
│       └── script.js          # Frontend logic for both architectures
└── templates/
    └── index.html             # HTML with both architecture views
```

---

## 🚀 How to Run

### 1. Install Dependencies
```bash
pip install -r requirements.txt
```

Required packages:
- Flask
- yfinance
- pandas, numpy
- scikit-learn
- XGBoost
- technical-analysis (ta)
- vaderSentiment

### 2. Start Flask Server
```bash
python app.py
```

The app runs on `http://localhost:5000`

### 3. Use Web Interface
1. Enter a ticker (AAPL, TSLA, RELIANCE.NS, etc.)
2. Click "Predict" button
3. See Architecture 1 result
4. Click "Confirmation Engine" to see Architecture 2

---

## 📝 Using the Final.ipynb Notebook

The `Final.ipynb` file documents both architectures step-by-step:

1. **Step 1:** Data Fetching - Fetch OHLCV and news
2. **Step 2:** Technical Indicators - Add 19 indicators
3. **Architecture 1:** Train XGBoost + ensemble with sentiment
4. **Architecture 2:** Score-based trend and momentum analysis
5. **Summary:** Compare both architectures side-by-side

Run the notebook to:
- Understand the algorithms
- Test with different stocks
- See comparison between architectures
- Export results

---

## 🎛️ Customization

### Adjust Architecture 1 Sensitivity
In `app.py`, sentiment threshold:
```python
sentiment_prediction = 1 if sentiment_score > 0.51 else 0
# Change 0.51 to adjust (lower = more bullish)
```

### Adjust Architecture 2 Threshold
In `app.py`, trend threshold:
```python
arch2_prediction = 1 if total_score >= 3.5 else 0
# Change 3.5 to adjust (lower = more bullish)
```

### Change Data Period
In `pipeline/data_fetcher.py`:
```python
df = stock.history(period='2y', interval='1d')
# Change '2y' to '1y', '5y', etc.
```

---

## 📊 Comparison Table

| Aspect | Architecture 1 | Architecture 2 |
|--------|---------------|----------------|
| **Name** | Technical + Sentiment | Trend + Momentum |
| **Model Type** | XGBoost + News | Pure Technical |
| **Prediction Output** | BUY / NOT BUY | RISE / FALL |
| **Confidence Calculation** | Model probability | Score-based |
| **Uses Sentiment** | Yes (News Headlines) | No |
| **Risk Level** | Conservative | Aggressive |
| **Best For** | Balanced trading | Trend following |
| **Data Inputs** | OHLCV + News | OHLCV only |
| **Time to Predict** | ~2-3 seconds | ~1 second |

---

## 💡 Tips for Better Predictions

1. **For Architecture 1:**
   - Best when sentiment and technicals align
   - More reliable during normal market conditions
   - Consider news context for better decisions

2. **For Architecture 2:**
   - Better during trending markets
   - Useful for identifying momentum changes
   - More responsive to short-term price movements

3. **General:**
   - Use both architectures for confirmation
   - Don't rely on single prediction alone
   - Consider market context and risk tolerance
   - Check multiple stocks before trading

---

## 🐛 Troubleshooting

### "Insufficient data" error
- Some stocks may not have enough historical data
- Try using major stocks like AAPL, MSFT, GOOGL

### "No news found"
- Not all stocks have recent news
- Architecture 2 doesn't need news, so use confirmation engine

### Slow predictions
- First request may be slow as data is fetched
- Subsequent requests are faster
- Try during low-traffic hours

---

## 📚 References

- **XGBoost:** https://xgboost.readthedocs.io/
- **Technical Analysis:** https://github.com/bukosabino/ta
- **VADER Sentiment:** https://github.com/cjhutto/vaderSentiment
- **yfinance:** https://github.com/ranaroussi/yfinance

---

## ⚠️ Disclaimer

**This is an educational tool, NOT financial advice.** Stock predictions are based on historical data and technical analysis. Past performance does not guarantee future results. Always:
- Do your own research
- Consult financial advisors
- Manage risk appropriately
- Only invest money you can afford to lose

---

**Last Updated:** 2026-06-13
**Version:** 2.0 (Two Architecture System)
