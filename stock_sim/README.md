# Stock Simulation Game

A sophisticated stock broker simulation with dynamic economic modeling and a modern web interface.

## Overview

This simulation game provides a realistic stock market experience where users can:
- **Trade Assets**: Buy and sell stocks, bonds, and options
- **Monitor Portfolio**: Track portfolio value, P&L, and positions in real-time
- **Economic Simulation**: Watch as macroeconomic indicators evolve and influence asset prices
- **Modern UI**: Interact through a professional broker-style web interface

## System Architecture

### Core Components

1. **Economic Engine** (`economic_engine.py`)
   - Simulates macroeconomic indicators using stochastic differential equations
   - Models: Interest rates, unemployment, market sentiment, inflation, GDP growth
   - Uses Ornstein-Uhlenbeck processes for mean-reverting behavior
   - Indicators interact realistically (e.g., high GDP growth reduces unemployment)

2. **Asset Classes** (`assets.py`)
   - **Stocks**: Geometric Brownian motion with economic factor adjustments
     - Influenced by GDP growth, sentiment, interest rates
     - Company-specific trend factors and sector classification
     - Beta coefficient for market sensitivity
   - **Bonds**: Price inversely related to interest rates
     - Uses present value formula for accurate pricing
     - Decreasing time to maturity
   - **Options**: Black-Scholes pricing model
     - Call and put options
     - Greeks-based sensitivity to underlying and time decay

3. **Portfolio Management** (`portfolio.py`)
   - Cash and position tracking
   - Buy/sell transaction execution with commissions
   - Real-time P&L calculation (realized and unrealized)
   - Transaction history

4. **Web Application** (`broker_app.py`)
   - Flask-based REST API
   - Real-time data streaming
   - Background simulation thread
   - Adjustable simulation speed

5. **Frontend Interface**
   - Modern, responsive design
   - Real-time updates (1-second refresh)
   - Interactive trading interface
   - Economic dashboard
   - Portfolio visualization

## Economic Model

### Indicators and Interactions

The simulation models realistic economic relationships:

- **Interest Rate** → Affects stock drift (inverse), bond prices (inverse)
- **Unemployment** → Influenced by GDP growth, affects sentiment
- **Sentiment** → Driven by GDP and unemployment, influences stock prices
- **Inflation** → Correlated with GDP growth, inversely related to interest rates
- **GDP Growth** → Affected by interest rates and sentiment, influences all assets

### Asset Pricing Models

**Stocks**:
```
dS = S * (μ_adjusted * dt + σ_adjusted * dW)
```
where μ is adjusted by economic conditions and company trends

**Bonds**:
```
Price = PV(coupons) + PV(face_value)
```
with yield = current interest rate

**Options**:
Black-Scholes formula with current volatility and risk-free rate

## Installation

### Prerequisites

Install **uv** - a fast, modern Python package manager:

```bash
# macOS/Linux
curl -LsSf https://astral.sh/uv/install.sh | sh

# Or via pip
pip install uv

# Or via Homebrew
brew install uv
```

### Quick Start

1. **Clone and navigate to the project**:
```bash
cd stock_sim
```

2. **Run the application** (uv handles dependencies automatically):
```bash
./run.sh
```

Or manually:
```bash
uv sync                    # Install dependencies
uv run python broker_app.py  # Run the app
```

3. **Open your browser to**:
```
http://localhost:5000
```

### Alternative: Traditional pip Installation

If you prefer pip over uv:
```bash
pip install -e .
python broker_app.py
```

## Usage Guide

### Starting the Simulation

1. Click **"Start Simulation"** to begin the economic and price simulation
2. Adjust simulation speed using the slider (0.1x to 5x)
3. Watch economic indicators evolve in real-time

### Trading Assets

1. Browse available assets in the "Available Assets" panel
2. Filter by type: All, Stocks, Bonds, or Options
3. Click **"Buy"** on any asset to open the trade modal
4. Enter quantity and execute the trade
5. Monitor your positions in the "Your Positions" panel

### Portfolio Management

- **Cash**: Available cash for trading
- **Positions Value**: Current market value of all holdings
- **Total Value**: Cash + Positions
- **Total P&L**: Combined realized and unrealized profit/loss
- **Return**: Percentage return on initial capital

### Understanding the Market

- **Stocks**: Higher risk, higher return potential
  - Positive sentiment and GDP growth boost prices
  - High interest rates suppress prices
  - Each stock has unique trend factors

- **Bonds**: Lower risk, stable returns
  - Prices rise when interest rates fall (inverse relationship)
  - Steady coupon payments (implicit in pricing)
  - Shorter maturity = less interest rate sensitivity

- **Options**: Leverage and speculation
  - Call options: Bet on price increases
  - Put options: Bet on price decreases
  - Time decay: Value decreases as expiration approaches
  - Volatility increases option value

## Configuration

### Initial Settings

You can modify these in the code:

- **Initial Cash**: `Portfolio(initial_cash=100000.0)` in broker_app.py
- **Commission Rate**: `commission_rate = 0.001` in portfolio.py (0.1%)
- **Time Step**: `dt = 0.01` in economic_engine.py (3.65 days per step)
- **Simulation Speed**: Adjustable from UI, default 1.0x

### Adding Custom Assets

To add new stocks, edit `create_sample_stocks()` in assets.py:

```python
Stock("SYMBOL", "Company Name", initial_price, "Sector", beta)
```

## API Endpoints

- `GET /api/economic_state` - Current economic indicators
- `GET /api/assets` - All available assets with current prices
- `GET /api/asset/<symbol>` - Detailed asset info with price history
- `GET /api/portfolio` - Portfolio summary and positions
- `GET /api/transactions` - Transaction history
- `POST /api/trade` - Execute buy/sell orders
- `POST /api/simulation/start` - Start simulation
- `POST /api/simulation/stop` - Stop simulation
- `POST /api/simulation/speed` - Adjust simulation speed

## Technical Details

### Simulation Time Scale

- Each time step represents ~3.65 days (dt = 0.01 years)
- At 1.0x speed, 1 real second = 1 simulation step = 3.65 days
- At 5.0x speed, 1 real second = 5 simulation steps = ~18 days

### Stochastic Processes

The simulation uses:
- **Ornstein-Uhlenbeck Process**: Mean-reverting economic indicators
- **Geometric Brownian Motion**: Stock price evolution
- **Wiener Process**: Random shocks (Gaussian noise)

### Performance

- Lightweight simulation: ~0.01s per step
- Supports real-time updates at 1 Hz refresh rate
- Can handle 100+ assets simultaneously

## Future Enhancements

Potential improvements:
- [ ] Add dividend payments for stocks
- [ ] Implement margin trading and short selling
- [ ] Add technical indicators and charting
- [ ] Historical data export
- [ ] Multi-user support with leaderboard
- [ ] Options exercise functionality
- [ ] Futures contracts
- [ ] Cryptocurrency assets
- [ ] News events affecting sentiment
- [ ] Sector rotation dynamics

## License

MIT License - Feel free to modify and extend!

## Credits

Built with:
- Flask (web framework)
- Chart.js (potential for future charting)
- Vanilla JavaScript (frontend)
- Stochastic calculus for financial modeling
