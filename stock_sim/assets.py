"""
Asset Classes for Stock Simulation
Includes Stocks, Bonds, and Options with dynamic pricing.
"""
import random
import math
from dataclasses import dataclass
from typing import List, Optional
from economic_engine import EconomicState


@dataclass
class PriceHistory:
    """Stores price history for an asset"""
    prices: List[float]
    timestamps: List[int]

    def add(self, price: float, timestamp: int):
        self.prices.append(price)
        self.timestamps.append(timestamp)

    def get_returns(self, periods: int = 1) -> List[float]:
        """Calculate returns over specified periods"""
        if len(self.prices) < periods + 1:
            return []
        returns = []
        for i in range(periods, len(self.prices)):
            ret = (self.prices[i] - self.prices[i - periods]) / self.prices[i - periods]
            returns.append(ret)
        return returns


class Asset:
    """Base class for all tradeable assets"""

    def __init__(self, symbol: str, name: str, initial_price: float):
        self.symbol = symbol
        self.name = name
        self.current_price = initial_price
        self.history = PriceHistory([initial_price], [0])

    def update_price(self, economic_state: EconomicState):
        """Update asset price based on economic conditions"""
        raise NotImplementedError("Subclasses must implement update_price")

    def get_price(self) -> float:
        """Get current price"""
        return self.current_price


class Stock(Asset):
    """
    Stock asset with price dynamics influenced by:
    - Economic conditions (GDP, sentiment, interest rates)
    - Company-specific trend factors
    - Random walk component
    """

    def __init__(self, symbol: str, name: str, initial_price: float,
                 sector: str = "Technology", beta: float = 1.0):
        super().__init__(symbol, name, initial_price)
        self.sector = sector
        self.beta = beta  # Sensitivity to market movements
        self.drift = 0.08  # Expected annual return
        self.volatility = 0.25  # Annual volatility
        self.trend_factor = random.uniform(-0.05, 0.10)  # Company-specific trend
        self.dt = 0.01  # Time step (matches economic engine)

    def update_price(self, economic_state: EconomicState):
        """
        Update stock price using geometric Brownian motion with economic factors.
        Price follows: dS = S * (μ * dt + σ * dW)
        where μ is adjusted by economic conditions
        """
        # Base drift adjusted by economic conditions
        adjusted_drift = self.drift

        # GDP growth positively affects stock prices
        adjusted_drift += self.beta * economic_state.gdp_growth * 2.0

        # Positive sentiment boosts prices
        adjusted_drift += self.beta * economic_state.sentiment * 0.3

        # High interest rates negatively affect stocks (opportunity cost)
        adjusted_drift -= self.beta * (economic_state.interest_rate - 0.05) * 0.5

        # Add company-specific trend
        adjusted_drift += self.trend_factor

        # Adjust volatility based on market conditions
        market_volatility = 0.15 + abs(economic_state.sentiment) * 0.2
        adjusted_volatility = self.volatility * (1.0 + market_volatility)

        # Random shock (Wiener process)
        z = random.gauss(0, 1)

        # Geometric Brownian motion
        drift_component = adjusted_drift * self.dt
        diffusion_component = adjusted_volatility * math.sqrt(self.dt) * z

        # Update price
        price_change_ratio = drift_component + diffusion_component
        self.current_price *= (1.0 + price_change_ratio)

        # Ensure price doesn't go negative or too extreme
        # Cap at 10x the initial price
        initial_price = self.history.prices[0]
        self.current_price = max(0.01, min(self.current_price, initial_price * 10))

        # Record in history
        self.history.add(self.current_price, economic_state.time_step)

        # Occasionally update trend factor (company news, earnings, etc.)
        if random.random() < 0.05:  # 5% chance per step
            self.trend_factor += random.gauss(0, 0.02)
            self.trend_factor = max(-0.10, min(0.15, self.trend_factor))


class Bond(Asset):
    """
    Bond asset with price influenced by interest rates.
    Bond prices move inversely to interest rates.
    """

    def __init__(self, symbol: str, name: str, face_value: float,
                 coupon_rate: float, maturity_years: float):
        # Calculate initial price based on current rates (assume 5% yield)
        initial_price = self._calculate_price(face_value, coupon_rate, 0.05, maturity_years)
        super().__init__(symbol, name, initial_price)

        self.face_value = face_value
        self.coupon_rate = coupon_rate
        self.maturity_years = maturity_years
        self.duration = maturity_years * 0.8  # Simplified duration

    def _calculate_price(self, face_value: float, coupon_rate: float,
                         yield_rate: float, time_to_maturity: float) -> float:
        """Calculate bond price using present value formula"""
        if yield_rate <= 0:
            yield_rate = 0.001

        # Annual coupon payment
        coupon = face_value * coupon_rate

        # Present value of coupon payments
        if yield_rate == coupon_rate:
            pv_coupons = coupon * time_to_maturity / (1 + yield_rate)
        else:
            pv_coupons = coupon * (1 - (1 + yield_rate) ** (-time_to_maturity)) / yield_rate

        # Present value of face value
        pv_face = face_value / ((1 + yield_rate) ** time_to_maturity)

        return pv_coupons + pv_face

    def update_price(self, economic_state: EconomicState):
        """
        Update bond price based on interest rate changes.
        Bond prices move inversely to interest rates (duration effect).
        """
        # Use interest rate as the yield
        market_yield = economic_state.interest_rate

        # Decrease time to maturity slightly each step
        self.maturity_years -= 0.01  # Assuming dt = 0.01 years
        self.maturity_years = max(0.1, self.maturity_years)

        # Recalculate price
        self.current_price = self._calculate_price(
            self.face_value,
            self.coupon_rate,
            market_yield,
            self.maturity_years
        )

        # Record in history
        self.history.add(self.current_price, economic_state.time_step)


class Option(Asset):
    """
    Option asset (call option) with price based on Black-Scholes model.
    Simplified implementation.
    """

    def __init__(self, symbol: str, name: str, underlying: Stock,
                 strike_price: float, expiry_years: float, option_type: str = "call"):
        # Calculate initial price using Black-Scholes
        initial_price = self._black_scholes_price(
            underlying.current_price, strike_price, 0.05, expiry_years,
            underlying.volatility, option_type
        )
        super().__init__(symbol, name, initial_price)

        self.underlying = underlying
        self.strike_price = strike_price
        self.expiry_years = expiry_years
        self.option_type = option_type.lower()  # "call" or "put"

    def _black_scholes_price(self, S: float, K: float, r: float, T: float,
                             sigma: float, option_type: str) -> float:
        """
        Calculate option price using Black-Scholes formula.

        S: Current stock price
        K: Strike price
        r: Risk-free rate
        T: Time to expiration (years)
        sigma: Volatility
        """
        if T <= 0:
            # Option expired, calculate intrinsic value
            if option_type == "call":
                return max(0, S - K)
            else:
                return max(0, K - S)

        # Prevent division by zero
        if sigma <= 0:
            sigma = 0.01

        # Black-Scholes formula
        d1 = (math.log(S / K) + (r + 0.5 * sigma ** 2) * T) / (sigma * math.sqrt(T))
        d2 = d1 - sigma * math.sqrt(T)

        # Cumulative normal distribution (approximation)
        def norm_cdf(x):
            return 0.5 * (1.0 + math.erf(x / math.sqrt(2.0)))

        if option_type == "call":
            price = S * norm_cdf(d1) - K * math.exp(-r * T) * norm_cdf(d2)
        else:  # put
            price = K * math.exp(-r * T) * norm_cdf(-d2) - S * norm_cdf(-d1)

        return max(0.01, price)

    def update_price(self, economic_state: EconomicState):
        """Update option price based on underlying and economic conditions"""
        # Decrease time to expiry
        self.expiry_years -= 0.01
        self.expiry_years = max(0, self.expiry_years)

        # Get current underlying price
        S = self.underlying.current_price

        # Calculate option price
        self.current_price = self._black_scholes_price(
            S,
            self.strike_price,
            economic_state.interest_rate,
            self.expiry_years,
            self.underlying.volatility,
            self.option_type
        )

        # Record in history
        self.history.add(self.current_price, economic_state.time_step)


# Asset factory functions
def create_sample_stocks() -> List[Stock]:
    """Create a diversified portfolio of sample stocks"""
    stocks = [
        Stock("TECH", "TechCorp", 150.0, "Technology", beta=1.3),
        Stock("FIN", "FinBank", 80.0, "Finance", beta=1.1),
        Stock("ENRG", "EnergyCo", 60.0, "Energy", beta=0.9),
        Stock("HLTH", "HealthMed", 120.0, "Healthcare", beta=0.7),
        Stock("CONS", "ConsumerGoods", 45.0, "Consumer", beta=0.85),
    ]
    return stocks


def create_sample_bonds() -> List[Bond]:
    """Create sample bonds with different maturities"""
    bonds = [
        Bond("BOND2Y", "2-Year Treasury", 1000.0, 0.03, 2.0),
        Bond("BOND5Y", "5-Year Treasury", 1000.0, 0.04, 5.0),
        Bond("BOND10Y", "10-Year Treasury", 1000.0, 0.045, 10.0),
        Bond("CORPBND", "Corporate Bond", 1000.0, 0.06, 5.0),
    ]
    return bonds


def create_sample_options(stocks: List[Stock]) -> List[Option]:
    """Create sample options on stocks"""
    options = []
    for stock in stocks[:3]:  # Create options for first 3 stocks
        # Call option at-the-money
        call = Option(
            f"{stock.symbol}-C",
            f"{stock.name} Call",
            stock,
            stock.current_price,
            1.0,  # 1 year expiry
            "call"
        )
        # Put option at-the-money
        put = Option(
            f"{stock.symbol}-P",
            f"{stock.name} Put",
            stock,
            stock.current_price,
            1.0,
            "put"
        )
        options.extend([call, put])
    return options
