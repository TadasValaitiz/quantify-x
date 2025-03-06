# Technical Trading Indicators for Python

Technical trading indicators are essential for algorithmic strategies. These indicators are categorized into **trend**, **momentum**, **volatility**, **volume**, and **other relevant indicators**. They can be implemented in Python using libraries like `TA-Lib` and `pandas-ta`.

---

## 📈 Trend Indicators  
*Used to identify the direction of the market (uptrend, downtrend, range-bound).*

- **Simple Moving Average (SMA)** – Averages the price over a given period.
- **Exponential Moving Average (EMA)** – Similar to SMA but gives more weight to recent prices.
- **Average Directional Index (ADX)** – Measures trend strength (above 25 = strong trend).
- **Ichimoku Cloud** – Multi-component indicator for trend, support, and resistance.
- **Parabolic SAR** – Places dots above/below price to signal trend reversals.
- **Aroon Indicator** – Identifies trend strength and direction using recent highs/lows.

---

## ⚡ Momentum Indicators  
*Measures the speed of price movement to identify overbought/oversold conditions and trend reversals.*

- **Relative Strength Index (RSI)** – Oscillates between 0-100; above 70 = overbought, below 30 = oversold.
- **Moving Average Convergence Divergence (MACD)** – Uses EMAs to track momentum changes and crossovers.
- **Stochastic Oscillator** – Compares closing price to past highs/lows; values over 80 = overbought, below 20 = oversold.
- **Commodity Channel Index (CCI)** – Measures price deviation from an average to identify overbought/oversold.
- **Williams %R** – Similar to Stochastic; values closer to -100 indicate oversold, closer to 0 indicate overbought.

---

## 🎢 Volatility Indicators  
*Tracks price fluctuations and breakout potential.*

- **Bollinger Bands** – Upper and lower bands set at 2 standard deviations from an SMA.
- **Average True Range (ATR)** – Measures market volatility using recent price ranges.
- **Keltner Channels** – Similar to Bollinger Bands but uses ATR instead of standard deviation.
- **Donchian Channels** – Plots highest high and lowest low over a specified period.

---

## 📊 Volume Indicators  
*Analyzes trading volume to confirm trends and price moves.*

- **On-Balance Volume (OBV)** – Cumulative volume measure; rising OBV confirms uptrends.
- **Accumulation/Distribution (A/D) Line** – Weights volume by price position to track buying/selling pressure.
- **Chaikin Money Flow (CMF)** – Uses volume flow to assess buying vs. selling pressure.
- **Money Flow Index (MFI)** – Volume-weighted RSI; above 80 = overbought, below 20 = oversold.
- **Volume-Weighted Average Price (VWAP)** – Average price weighted by volume; used as a trading benchmark.

---

## 🔍 Other Relevant Indicators  
*Additional tools for technical analysis and market sentiment.*

- **Fibonacci Retracement Levels** – Key levels (23.6%, 38.2%, 50%, 61.8%) for potential support/resistance.
- **Pivot Points** – Calculates support/resistance levels using previous high, low, and close.
- **Advance–Decline Line (A/D Line)** – Tracks the number of advancing vs. declining stocks for market breadth.
- **Arms Index (TRIN)** – Compares advancing/declining stocks with advancing/declining volume.

---