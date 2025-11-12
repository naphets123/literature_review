"""
Stock Broker Web Application
Flask-based web interface for the stock simulation game.
"""
from flask import Flask, render_template, jsonify, request
import threading
import time
from economic_engine import EconomicEngine, EconomicState
from assets import Stock, Bond, Option, create_sample_stocks, create_sample_bonds, create_sample_options
from portfolio import Portfolio

app = Flask(__name__)

# Global state
economic_engine = EconomicEngine()
portfolio = Portfolio(initial_cash=100000.0)

# Create sample assets
stocks = create_sample_stocks()
bonds = create_sample_bonds()
options = create_sample_options(stocks)

# Combine all assets
all_assets = {asset.symbol: asset for asset in stocks + bonds + options}

# Simulation control
simulation_running = False
simulation_thread = None
simulation_speed = 1.0  # Simulation steps per second


def simulation_loop():
    """Background thread that runs the simulation"""
    global simulation_running
    while simulation_running:
        # Update economic state
        economic_engine.step()
        current_state = economic_engine.get_state()

        # Update all asset prices
        for asset in all_assets.values():
            asset.update_price(current_state)

        # Update portfolio with current prices
        portfolio.update_prices(all_assets)

        # Sleep based on simulation speed
        time.sleep(1.0 / simulation_speed)


@app.route('/')
def index():
    """Main page"""
    return render_template('index.html')


@app.route('/api/economic_state')
def get_economic_state():
    """Get current economic state"""
    state = economic_engine.get_state()
    return jsonify({
        "interest_rate": round(state.interest_rate * 100, 2),
        "unemployment_rate": round(state.unemployment_rate * 100, 2),
        "sentiment": round(state.sentiment, 2),
        "inflation_rate": round(state.inflation_rate * 100, 2),
        "gdp_growth": round(state.gdp_growth * 100, 2),
        "time_step": state.time_step,
        "simulation_running": simulation_running
    })


@app.route('/api/assets')
def get_assets():
    """Get all available assets"""
    assets_data = []

    for symbol, asset in all_assets.items():
        asset_type = "stock" if isinstance(asset, Stock) else \
                     "bond" if isinstance(asset, Bond) else "option"

        asset_info = {
            "symbol": symbol,
            "name": asset.name,
            "price": round(asset.current_price, 2),
            "type": asset_type
        }

        # Add type-specific info
        if isinstance(asset, Stock):
            # Calculate daily change
            history = asset.history.prices
            if len(history) > 1:
                change = ((history[-1] - history[-2]) / history[-2]) * 100
            else:
                change = 0.0
            asset_info.update({
                "sector": asset.sector,
                "beta": round(asset.beta, 2),
                "change_percent": round(change, 2)
            })
        elif isinstance(asset, Bond):
            asset_info.update({
                "face_value": asset.face_value,
                "coupon_rate": round(asset.coupon_rate * 100, 2),
                "maturity_years": round(asset.maturity_years, 2)
            })
        elif isinstance(asset, Option):
            asset_info.update({
                "underlying": asset.underlying.symbol,
                "strike_price": round(asset.strike_price, 2),
                "expiry_years": round(asset.expiry_years, 2),
                "option_type": asset.option_type
            })

        assets_data.append(asset_info)

    return jsonify(assets_data)


@app.route('/api/asset/<symbol>')
def get_asset(symbol):
    """Get detailed info for a specific asset"""
    if symbol not in all_assets:
        return jsonify({"error": "Asset not found"}), 404

    asset = all_assets[symbol]
    history = asset.history.prices[-100:]  # Last 100 data points

    return jsonify({
        "symbol": symbol,
        "name": asset.name,
        "current_price": round(asset.current_price, 2),
        "price_history": [round(p, 2) for p in history]
    })


@app.route('/api/portfolio')
def get_portfolio():
    """Get portfolio summary"""
    summary = portfolio.get_summary()
    positions = portfolio.get_positions_summary()

    return jsonify({
        "summary": {
            "cash": round(summary["cash"], 2),
            "positions_value": round(summary["positions_value"], 2),
            "total_value": round(summary["total_value"], 2),
            "initial_value": round(summary["initial_value"], 2),
            "realized_pnl": round(summary["realized_pnl"], 2),
            "unrealized_pnl": round(summary["unrealized_pnl"], 2),
            "total_pnl": round(summary["total_pnl"], 2),
            "total_return_percent": round(summary["total_return_percent"], 2),
            "num_positions": summary["num_positions"]
        },
        "positions": [
            {
                "symbol": p["symbol"],
                "quantity": round(p["quantity"], 4),
                "average_price": round(p["average_price"], 2),
                "current_price": round(p["current_price"], 2),
                "market_value": round(p["market_value"], 2),
                "cost_basis": round(p["cost_basis"], 2),
                "unrealized_pnl": round(p["unrealized_pnl"], 2),
                "unrealized_pnl_percent": round(p["unrealized_pnl_percent"], 2),
                "asset_type": p["asset_type"]
            }
            for p in positions
        ]
    })


@app.route('/api/transactions')
def get_transactions():
    """Get transaction history"""
    limit = request.args.get('limit', default=50, type=int)
    transactions = portfolio.get_transactions(limit)
    return jsonify(transactions)


@app.route('/api/trade', methods=['POST'])
def trade():
    """Execute a trade (buy or sell)"""
    data = request.json
    action = data.get('action')  # 'buy' or 'sell'
    symbol = data.get('symbol')
    quantity = data.get('quantity', 0)

    if symbol not in all_assets:
        return jsonify({"success": False, "message": "Invalid symbol"}), 400

    if quantity <= 0:
        return jsonify({"success": False, "message": "Invalid quantity"}), 400

    asset = all_assets[symbol]
    current_time = economic_engine.get_state().time_step

    if action == 'buy':
        result = portfolio.buy(asset, quantity, current_time)
    elif action == 'sell':
        result = portfolio.sell(asset, quantity, current_time)
    else:
        return jsonify({"success": False, "message": "Invalid action"}), 400

    return jsonify(result)


@app.route('/api/simulation/start', methods=['POST'])
def start_simulation():
    """Start the simulation"""
    global simulation_running, simulation_thread

    if simulation_running:
        return jsonify({"message": "Simulation already running"})

    simulation_running = True
    simulation_thread = threading.Thread(target=simulation_loop, daemon=True)
    simulation_thread.start()

    return jsonify({"message": "Simulation started"})


@app.route('/api/simulation/stop', methods=['POST'])
def stop_simulation():
    """Stop the simulation"""
    global simulation_running

    if not simulation_running:
        return jsonify({"message": "Simulation not running"})

    simulation_running = False
    return jsonify({"message": "Simulation stopped"})


@app.route('/api/simulation/speed', methods=['POST'])
def set_simulation_speed():
    """Set simulation speed"""
    global simulation_speed

    data = request.json
    speed = data.get('speed', 1.0)
    simulation_speed = max(0.1, min(10.0, speed))  # Clamp between 0.1x and 10x

    return jsonify({"speed": simulation_speed})


def main():
    """Main entry point for the application"""
    print("=" * 50)
    print("  Stock Simulation Game")
    print("=" * 50)
    print("\nStarting server...")
    print("Open your browser to: http://localhost:5000")
    print("\nPress Ctrl+C to stop\n")
    app.run(debug=True, host='0.0.0.0', port=5000, threaded=True)


if __name__ == '__main__':
    main()
