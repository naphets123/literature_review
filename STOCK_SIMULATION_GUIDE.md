# Stock Simulation Game - Quick Start Guide

## Overview

A complete stock market simulation with realistic economic modeling and a modern broker interface. The system simulates macroeconomic indicators (interest rates, unemployment, GDP, etc.) and their effects on stocks, bonds, and options.

## Project Structure

```
stock_sim/
├── economic_engine.py      # Economic simulation engine
├── assets.py               # Stock, Bond, and Option classes
├── portfolio.py            # Portfolio management system
├── broker_app.py           # Flask web application
├── static/
│   ├── style.css          # Modern UI styling
│   └── app.js             # Frontend JavaScript
├── templates/
│   └── index.html         # Main web interface
├── requirements.txt       # Python dependencies
├── README.md             # Detailed documentation
└── run.sh                # Startup script
```

## Quick Start

### 1. Install Dependencies

```bash
cd stock_sim
pip install -r requirements.txt
```

### 2. Run the Application

**Option A: Using the script**
```bash
./run.sh
```

**Option B: Direct Python**
```bash
python3 broker_app.py
```

### 3. Open in Browser

Navigate to: **http://localhost:5000**

## How to Use

### Starting the Simulation

1. **Click "Start Simulation"** - Begins the economic simulation
2. **Adjust Speed** - Use the slider to control simulation speed (0.1x to 5x)
3. **Watch the Economy** - Economic indicators update in real-time

### Trading

1. **Browse Assets** - View available stocks, bonds, and options
2. **Filter by Type** - Click filter buttons (All/Stocks/Bonds/Options)
3. **Buy Assets** - Click "Buy" button, enter quantity, execute trade
4. **Sell Assets** - View your positions, click "Sell" to liquidate

### Monitoring Your Portfolio

The portfolio summary shows:
- **Total Value**: Current portfolio worth
- **Cash**: Available for trading
- **Positions Value**: Current market value of holdings
- **Total P&L**: Profit/Loss (realized + unrealized)
- **Return %**: Performance vs initial capital

## Key Features

### Economic Simulation

**Six Interacting Indicators:**
- Interest Rate (affects bonds and stocks)
- Unemployment Rate (correlates with GDP)
- Market Sentiment (drives stock prices)
- Inflation Rate (relates to GDP growth)
- GDP Growth (fundamental economic driver)

**Realistic Interactions:**
- High GDP growth → Lower unemployment
- Positive sentiment → Higher stock prices
- High interest rates → Lower bond prices
- Economic shocks propagate through the system

### Asset Classes

**Stocks (5 available)**
- Geometric Brownian motion pricing
- Sector classification (Tech, Finance, Energy, Healthcare, Consumer)
- Beta coefficients for market sensitivity
- Company-specific trend factors
- Responsive to economic conditions

**Bonds (4 available)**
- 2-Year, 5-Year, 10-Year Treasury bonds
- Corporate bond option
- Prices inversely related to interest rates
- Accurate present value calculations

**Options (6 available)**
- Call and Put options on select stocks
- Black-Scholes pricing model
- Time decay (theta)
- Volatility sensitivity (vega)
- 1-year expiration period

### Portfolio Management

- Real-time position tracking
- Transaction history
- Realized and unrealized P&L
- Commission fees (0.1% per trade)
- Initial capital: $100,000

## Understanding the Markets

### Stock Strategy

**When to Buy:**
- Positive economic sentiment
- Strong GDP growth
- Falling interest rates
- Low unemployment

**When to Sell:**
- Negative sentiment turning
- Interest rates rising sharply
- Economic indicators deteriorating

### Bond Strategy

**When to Buy:**
- Rising interest rates (bonds are cheap)
- Economic uncertainty (safe haven)
- Stock market volatility high

**When to Sell:**
- Falling interest rates (bond prices peaked)
- Strong economic growth (stocks more attractive)

### Options Strategy

**Call Options (Bullish):**
- Buy when you expect stock price to rise
- Leverage: Control stock exposure with less capital
- Risk: Time decay and volatility changes

**Put Options (Bearish):**
- Buy when you expect stock price to fall
- Hedge: Protect existing stock positions
- Risk: Premium paid if wrong direction

## Example Scenarios

### Scenario 1: Bull Market
1. Start simulation
2. Wait for positive sentiment (> 0.2)
3. Buy tech stocks (high beta)
4. Monitor for sentiment reversal
5. Take profits when sentiment peaks

### Scenario 2: Interest Rate Play
1. Observe interest rate trend
2. If rates falling: Buy long-term bonds (BOND10Y)
3. If rates rising: Buy short-term bonds or stocks
4. Bond prices move inverse to rates

### Scenario 3: Options Leverage
1. Identify stock with strong positive trend
2. Buy call option instead of stock
3. Control more exposure with less capital
4. Exit before time decay erodes value

## Technical Details

### Simulation Parameters

- **Time Step**: 0.01 years (~3.65 days)
- **Base Volatility**: 15-25% depending on asset
- **Mean Reversion**: Economic indicators trend toward historical means
- **Refresh Rate**: 1 second (adjustable via speed slider)

### Economic Model

Uses stochastic differential equations:
- **Ornstein-Uhlenbeck Process**: Mean-reverting indicators
- **Geometric Brownian Motion**: Stock prices
- **Wiener Process**: Random shocks

### API Endpoints

Available for custom integrations:

```
GET  /api/economic_state     - Current economy
GET  /api/assets             - All assets
GET  /api/portfolio          - Your portfolio
POST /api/trade              - Execute trade
POST /api/simulation/start   - Start simulation
POST /api/simulation/stop    - Stop simulation
```

## Tips for Success

1. **Start Slow**: Begin with 1x speed to understand the dynamics
2. **Diversify**: Don't put all capital in one asset
3. **Watch Indicators**: Economic trends predict asset movements
4. **Use Stop Losses**: Sell positions that move against you
5. **Options Timing**: Be mindful of time decay
6. **Bond Inverse**: Remember bonds move opposite to rates
7. **Sentiment Matters**: Market sentiment drives short-term moves
8. **Trends**: GDP and unemployment affect long-term performance

## Troubleshooting

**Port already in use:**
```bash
# Change port in broker_app.py, line: app.run(port=5001)
```

**Simulation too fast/slow:**
- Use the speed slider in the UI
- Default: 1.0x (1 step per second)

**Asset prices not updating:**
- Make sure simulation is started (green button)
- Check browser console for errors

## Next Steps

After mastering the basics:
1. Try different market conditions (bull vs bear)
2. Test complex strategies (hedging with options)
3. Monitor how economic shocks propagate
4. Analyze which assets perform best in different scenarios
5. Experiment with portfolio allocations

## Files to Modify

**Add more stocks:**
- Edit `create_sample_stocks()` in `assets.py`

**Change initial cash:**
- Modify `Portfolio(initial_cash=...)` in `broker_app.py`

**Adjust commission rate:**
- Change `commission_rate` in `portfolio.py`

**Modify economic parameters:**
- Edit mean/volatility values in `economic_engine.py`

## Support

For detailed technical documentation, see: `stock_sim/README.md`

---

**Have fun trading!** 📈📊💰
