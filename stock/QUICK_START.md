# 🚀 Quick Start Guide - Stock Prediction System

## What Was Built

You now have a **complete stock prediction system with TWO independent architectures** that work together:

### Architecture 1: Main Prediction (Conservative)
```
User enters "AAPL" → System shows "BUY 🟢" with 75% confidence
- Uses both technical indicators AND news sentiment
- More conservative, requires agreement from both signals
- Best for balanced trading
```

### Architecture 2: Alternative Prediction (Aggressive)  
```
User clicks "Confirmation Engine" → System shows "RISE 📈" with 68% confidence
- Pure trend and momentum analysis (no news)
- More aggressive trend-following approach
- Best for momentum traders
```

---

## 📁 What Was Created/Modified

### New/Updated Files:
1. ✅ **Final.ipynb** - Complete notebook with both architectures documented
2. ✅ **app.py** - Added `/predict-alternative` endpoint
3. ✅ **static/css/style.css** - Added styles for both architectures
4. ✅ **static/js/script.js** - Rewrote to support architecture switching
5. ✅ **templates/index.html** - UI for both architectures with toggle buttons
6. ✅ **ARCHITECTURE_GUIDE.md** - Comprehensive technical documentation

---

## 🎯 How to Use

### 1. Start the Server
```bash
python app.py
```

### 2. Open in Browser
```
http://localhost:5000
```

### 3. Get Prediction (User Steps)
1. **Type company name/ticker** (e.g., "AAPL", "TESLA", "MSFT")
2. **Click "Predict" button**
3. **See Main Analysis** → Architecture 1 results (BUY/NOT BUY)
   - Shows confidence, sentiment score, latest news, price chart
4. **If not satisfied**, click **"Confirmation Engine"** button
5. **See Alternative Results** → Architecture 2 results (RISE/FALL)
   - Shows trend score, momentum score, RSI, MACD, outlook

---

## 🔄 System Architecture Comparison

| Feature | Architecture 1 (Main) | Architecture 2 (Alternative) |
|---------|----------------------|------------------------------|
| **Prediction** | BUY or NOT BUY 🟢🔴 | RISE or FALL 📈📉 |
| **Model** | XGBoost + News Sentiment | Pure Technical Analysis |
| **Uses News** | ✅ Yes | ❌ No |
| **Risk Level** | Lower (Conservative) | Higher (Aggressive) |
| **Confidence** | Probability-based | Score-based |
| **API** | POST /predict | POST /predict-alternative |
| **Data** | OHLCV + News | OHLCV only |

---

## 📊 What Each Architecture Shows

### Main Prediction (Architecture 1)
```
┌─────────────────────────────────────────┐
│  Prediction: BUY 🟢                     │
│  Confidence: 75%                        │
│  Architecture: Technical + Sentiment    │
├─────────────────────────────────────────┤
│  Market Sentiment: Positive 📈          │
│  Sentiment Score: 0.65                  │
│  Latest News: (top 5 headlines)         │
├─────────────────────────────────────────┤
│  Chart: Price with SMA20 & SMA50        │
└─────────────────────────────────────────┘
```

### Alternative Prediction (Architecture 2)
```
┌─────────────────────────────────────────┐
│  Prediction: RISE 📈                    │
│  Confidence: 68%                        │
│  Architecture: Trend + Momentum         │
├─────────────────────────────────────────┤
│  Trend Score: 2.5/3                     │
│  Momentum Score: 2.0/2.5                │
│  Total Score: 4.5/5.5                   │
├─────────────────────────────────────────┤
│  RSI: 55.2 | MACD: 0.0125               │
│  SMA20: $150.25 | SMA50: $148.75        │
│  Trend Details & Momentum Details       │
└─────────────────────────────────────────┘
```

---

## 🧠 How Predictions Work

### Architecture 1: Technical + Sentiment
```
Step 1: Fetch OHLCV data (2 years) + News
Step 2: Calculate 19 technical indicators
        RSI, SMA20, SMA50, MACD, Bollinger Bands, ATR, OBV, etc.
Step 3: Train XGBoost on indicators
        Target: tomorrow's close > today's close
Step 4: Analyze news sentiment (VADER)
        Positive = UP, Negative = DOWN, Neutral = ?
Step 5: Ensemble logic
        BUY = 1 only if Technical==1 AND Sentiment==1
        Otherwise = NOT BUY = 0
```

### Architecture 2: Trend + Momentum
```
Step 1: Fetch OHLCV data (2 years)
Step 2: Calculate indicators
        RSI, MACD, SMA20, SMA50, price momentum
Step 3: Trend Analysis (score 0-3)
        ✓ Price > SMA20? +1
        ✓ SMA20 > SMA50? +1  (Golden Cross)
        ✓ MACD > Signal? +1
Step 4: Momentum Analysis (score 0-2.5)
        RSI analysis: -0.5 to +0.5
        5-day momentum: +1.0 if up, 0 if down
Step 5: Decision
        Total score >= 3.5 → RISE
        Total score < 3.5 → FALL
```

---

## 🛠️ API Endpoints

### Get Main Prediction (Architecture 1)
```bash
curl -X POST http://localhost:5000/predict \
  -H "Content-Type: application/json" \
  -d '{"ticker": "AAPL"}'
```

Response:
```json
{
  "prediction": 1,
  "predictionLabel": "BUY 🟢",
  "confidence": 75.5,
  "sentimentLabel": "Positive 📈",
  "sentimentScore": 0.65,
  "news": ["Apple earnings beat expectations", ...]
}
```

### Get Alternative Prediction (Architecture 2)
```bash
curl -X POST http://localhost:5000/predict-alternative \
  -H "Content-Type: application/json" \
  -d '{"ticker": "AAPL"}'
```

Response:
```json
{
  "prediction": 1,
  "predictionLabel": "RISE 📈",
  "confidence": 68.5,
  "trendScore": 2.5,
  "momentumScore": 2.0,
  "totalScore": 4.5,
  "rsi": 55.2,
  "outlook": "Uptrend"
}
```

---

## 📝 Testing Different Stocks

Try these tickers:
- **Tech:** AAPL, MSFT, GOOGL, NVDA, META
- **E-commerce:** AMZN, TSLA
- **Finance:** JPM, GS, BAC
- **India:** RELIANCE.NS, TCS.NS, INFY.NS

---

## 🔧 Configuration

### Adjust Sensitivity

**Architecture 1** - Make more bullish:
```python
# In app.py, change sentiment threshold
sentiment_prediction = 1 if sentiment_score > 0.50 else 0  # was 0.51
```

**Architecture 2** - Make more bullish:
```python
# In app.py, change score threshold  
arch2_prediction = 1 if total_score >= 3.0 else 0  # was 3.5
```

### Change Historical Data Period
```python
# In pipeline/data_fetcher.py
df = stock.history(period='5y', interval='1d')  # was '2y'
```

---

## 📚 Files Reference

```
Stock Prediction System
├── app.py (BACKEND - Flask)
│   ├── /predict → Architecture 1
│   └── /predict-alternative → Architecture 2
│
├── pipeline/ (DATA & MODELS)
│   ├── data_fetcher.py → Fetch OHLCV & news
│   ├── feature_engineering.py → Add technical indicators
│   ├── predictor.py → XGBoost model
│   └── sentiment_analyzer.py → VADER sentiment
│
├── templates/index.html (FRONTEND - HTML)
│   ├── Header with search bar
│   ├── Architecture toggle buttons
│   ├── Main Analysis view (Arch 1)
│   └── Confirmation Engine view (Arch 2)
│
├── static/ (FRONTEND - CSS & JS)
│   ├── css/style.css → Glassmorphic design
│   └── js/script.js → Handles both architectures
│
├── Final.ipynb (DOCUMENTATION)
│   └── Step-by-step walkthrough of both architectures
│
└── ARCHITECTURE_GUIDE.md (COMPLETE DOCUMENTATION)
```

---

## ⚡ Performance

- **First Prediction:** ~2-3 seconds (fetching data + processing)
- **Alternative Prediction:** ~1-2 seconds (using same data)
- **Subsequent Requests:** ~2-3 seconds (fresh data fetch)

---

## 🚨 Error Handling

**"Insufficient data"** → Stock doesn't have enough history
- Solution: Try major stocks (AAPL, MSFT, GOOGL)

**"No news found"** → Stock has no recent news
- Solution: Architecture 2 still works (doesn't need news)

**"Ticker not found"** → Invalid ticker symbol
- Solution: Check ticker format or try another stock

---

## 💡 Best Practices

1. **Use Architecture 1 when:**
   - You want balanced, conservative predictions
   - News sentiment aligns with technical signals
   - Trading medium to long-term positions

2. **Use Architecture 2 when:**
   - You want aggressive trend-following signals
   - Trading short-term momentum moves
   - You prefer pure technical analysis

3. **General Tips:**
   - Always check BOTH architectures for confirmation
   - Consider market conditions and news context
   - Don't rely on single prediction alone
   - Manage risk appropriately

---

## 📖 For Complete Details

See **ARCHITECTURE_GUIDE.md** for:
- Full technical implementation
- Mathematical formulas
- Data flow diagrams
- Customization options
- Troubleshooting guide

---

## 🎉 Summary

✅ **Architecture 1:** Main prediction (Technical + Sentiment) → BUY/NOT BUY
✅ **Architecture 2:** Alternative prediction (Trend + Momentum) → RISE/FALL  
✅ **Web Interface:** Toggle between both with buttons
✅ **Documentation:** Complete in Final.ipynb and ARCHITECTURE_GUIDE.md
✅ **Ready to Use:** Just run `python app.py` and visit localhost:5000

**Happy trading! 📈**
