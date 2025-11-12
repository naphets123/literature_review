"""
Portfolio Management System
Handles user portfolios, transactions, and P&L tracking.
"""
from dataclasses import dataclass
from typing import Dict, List, Optional
from datetime import datetime
import json


@dataclass
class Position:
    """Represents a position in an asset"""
    symbol: str
    quantity: float
    average_price: float
    current_price: float
    asset_type: str  # "stock", "bond", "option"

    @property
    def market_value(self) -> float:
        """Current market value of the position"""
        return self.quantity * self.current_price

    @property
    def cost_basis(self) -> float:
        """Total cost basis of the position"""
        return self.quantity * self.average_price

    @property
    def unrealized_pnl(self) -> float:
        """Unrealized profit/loss"""
        return self.market_value - self.cost_basis

    @property
    def unrealized_pnl_percent(self) -> float:
        """Unrealized P&L as percentage"""
        if self.cost_basis == 0:
            return 0.0
        return (self.unrealized_pnl / self.cost_basis) * 100


@dataclass
class Transaction:
    """Represents a buy/sell transaction"""
    timestamp: int
    symbol: str
    action: str  # "buy" or "sell"
    quantity: float
    price: float
    total_value: float
    commission: float = 0.0

    def to_dict(self):
        return {
            "timestamp": self.timestamp,
            "symbol": self.symbol,
            "action": self.action,
            "quantity": self.quantity,
            "price": self.price,
            "total_value": self.total_value,
            "commission": self.commission
        }


class Portfolio:
    """
    User portfolio managing cash, positions, and transaction history.
    """

    def __init__(self, initial_cash: float = 100000.0):
        self.cash = initial_cash
        self.initial_cash = initial_cash
        self.positions: Dict[str, Position] = {}
        self.transaction_history: List[Transaction] = []
        self.realized_pnl = 0.0
        self.commission_rate = 0.001  # 0.1% commission per trade

    def get_position(self, symbol: str) -> Optional[Position]:
        """Get position for a symbol"""
        return self.positions.get(symbol)

    def has_position(self, symbol: str) -> bool:
        """Check if portfolio has a position in symbol"""
        return symbol in self.positions

    def buy(self, asset, quantity: float, timestamp: int) -> Dict:
        """
        Buy an asset.

        Returns:
            Dict with status and message
        """
        if quantity <= 0:
            return {"success": False, "message": "Quantity must be positive"}

        price = asset.get_price()
        total_cost = quantity * price
        commission = total_cost * self.commission_rate
        total_with_commission = total_cost + commission

        # Check if enough cash
        if self.cash < total_with_commission:
            return {
                "success": False,
                "message": f"Insufficient funds. Need ${total_with_commission:.2f}, have ${self.cash:.2f}"
            }

        # Deduct cash
        self.cash -= total_with_commission

        # Update or create position
        symbol = asset.symbol
        if symbol in self.positions:
            pos = self.positions[symbol]
            # Update average price
            new_quantity = pos.quantity + quantity
            new_avg_price = ((pos.quantity * pos.average_price) + (quantity * price)) / new_quantity
            pos.quantity = new_quantity
            pos.average_price = new_avg_price
            pos.current_price = price
        else:
            # Create new position
            asset_type = "stock" if hasattr(asset, 'beta') else \
                         "bond" if hasattr(asset, 'face_value') else "option"
            self.positions[symbol] = Position(
                symbol=symbol,
                quantity=quantity,
                average_price=price,
                current_price=price,
                asset_type=asset_type
            )

        # Record transaction
        transaction = Transaction(
            timestamp=timestamp,
            symbol=symbol,
            action="buy",
            quantity=quantity,
            price=price,
            total_value=total_cost,
            commission=commission
        )
        self.transaction_history.append(transaction)

        return {
            "success": True,
            "message": f"Bought {quantity} shares of {symbol} at ${price:.2f}",
            "total_cost": total_with_commission
        }

    def sell(self, asset, quantity: float, timestamp: int) -> Dict:
        """
        Sell an asset.

        Returns:
            Dict with status and message
        """
        if quantity <= 0:
            return {"success": False, "message": "Quantity must be positive"}

        symbol = asset.symbol
        if symbol not in self.positions:
            return {"success": False, "message": f"No position in {symbol}"}

        pos = self.positions[symbol]
        if pos.quantity < quantity:
            return {
                "success": False,
                "message": f"Insufficient shares. Have {pos.quantity}, trying to sell {quantity}"
            }

        price = asset.get_price()
        total_proceeds = quantity * price
        commission = total_proceeds * self.commission_rate
        net_proceeds = total_proceeds - commission

        # Calculate realized P&L
        cost_basis = quantity * pos.average_price
        realized_pnl = total_proceeds - cost_basis
        self.realized_pnl += realized_pnl

        # Add cash
        self.cash += net_proceeds

        # Update position
        pos.quantity -= quantity
        pos.current_price = price

        # Remove position if quantity is zero
        if pos.quantity == 0:
            del self.positions[symbol]

        # Record transaction
        transaction = Transaction(
            timestamp=timestamp,
            symbol=symbol,
            action="sell",
            quantity=quantity,
            price=price,
            total_value=total_proceeds,
            commission=commission
        )
        self.transaction_history.append(transaction)

        return {
            "success": True,
            "message": f"Sold {quantity} shares of {symbol} at ${price:.2f}",
            "total_proceeds": net_proceeds,
            "realized_pnl": realized_pnl
        }

    def update_prices(self, assets: Dict):
        """Update current prices for all positions"""
        for symbol, pos in self.positions.items():
            if symbol in assets:
                pos.current_price = assets[symbol].get_price()

    def get_total_value(self) -> float:
        """Get total portfolio value (cash + positions)"""
        positions_value = sum(pos.market_value for pos in self.positions.values())
        return self.cash + positions_value

    def get_unrealized_pnl(self) -> float:
        """Get total unrealized P&L"""
        return sum(pos.unrealized_pnl for pos in self.positions.values())

    def get_total_pnl(self) -> float:
        """Get total P&L (realized + unrealized)"""
        return self.realized_pnl + self.get_unrealized_pnl()

    def get_total_return_percent(self) -> float:
        """Get total return as percentage of initial investment"""
        current_value = self.get_total_value()
        return ((current_value - self.initial_cash) / self.initial_cash) * 100

    def get_positions_summary(self) -> List[Dict]:
        """Get summary of all positions"""
        return [
            {
                "symbol": pos.symbol,
                "quantity": pos.quantity,
                "average_price": pos.average_price,
                "current_price": pos.current_price,
                "market_value": pos.market_value,
                "cost_basis": pos.cost_basis,
                "unrealized_pnl": pos.unrealized_pnl,
                "unrealized_pnl_percent": pos.unrealized_pnl_percent,
                "asset_type": pos.asset_type
            }
            for pos in self.positions.values()
        ]

    def get_summary(self) -> Dict:
        """Get complete portfolio summary"""
        return {
            "cash": self.cash,
            "positions_value": sum(pos.market_value for pos in self.positions.values()),
            "total_value": self.get_total_value(),
            "initial_value": self.initial_cash,
            "realized_pnl": self.realized_pnl,
            "unrealized_pnl": self.get_unrealized_pnl(),
            "total_pnl": self.get_total_pnl(),
            "total_return_percent": self.get_total_return_percent(),
            "num_positions": len(self.positions)
        }

    def get_transactions(self, limit: int = None) -> List[Dict]:
        """Get transaction history"""
        transactions = [t.to_dict() for t in self.transaction_history]
        if limit:
            return transactions[-limit:]
        return transactions
