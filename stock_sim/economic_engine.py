"""
Economic Simulation Engine
Simulates macroeconomic indicators and their evolution over time.
"""
import random
import time
from dataclasses import dataclass
from typing import List, Dict
import math


@dataclass
class EconomicState:
    """Represents the current state of the economy"""
    interest_rate: float  # Annual interest rate (0.0 to 1.0, e.g., 0.05 = 5%)
    unemployment_rate: float  # Unemployment rate (0.0 to 1.0, e.g., 0.04 = 4%)
    sentiment: float  # General market sentiment (-1.0 to 1.0, negative to positive)
    inflation_rate: float  # Annual inflation rate
    gdp_growth: float  # Quarterly GDP growth rate
    time_step: int  # Current time step in the simulation


class EconomicEngine:
    """
    Simulates the evolution of economic indicators over time.
    Uses simplified stochastic processes to model economic dynamics.
    """

    def __init__(self, initial_state: EconomicState = None, dt: float = 0.01):
        """
        Initialize the economic engine.

        Args:
            initial_state: Starting economic conditions
            dt: Time increment for each simulation step (in years, e.g., 0.01 = 3.65 days)
        """
        self.dt = dt

        if initial_state is None:
            # Set reasonable default values
            self.state = EconomicState(
                interest_rate=0.05,  # 5% base interest rate
                unemployment_rate=0.04,  # 4% unemployment
                sentiment=0.1,  # Slightly positive sentiment
                inflation_rate=0.02,  # 2% inflation
                gdp_growth=0.02,  # 2% GDP growth
                time_step=0
            )
        else:
            self.state = initial_state

        # Historical data for tracking
        self.history: List[EconomicState] = [self._copy_state()]

    def _copy_state(self) -> EconomicState:
        """Create a copy of the current state"""
        return EconomicState(
            interest_rate=self.state.interest_rate,
            unemployment_rate=self.state.unemployment_rate,
            sentiment=self.state.sentiment,
            inflation_rate=self.state.inflation_rate,
            gdp_growth=self.state.gdp_growth,
            time_step=self.state.time_step
        )

    def step(self):
        """
        Advance the simulation by one time step.
        Updates all economic indicators using stochastic differential equations.
        """
        # Mean reversion parameters
        interest_mean = 0.05
        unemployment_mean = 0.045
        sentiment_mean = 0.0
        inflation_mean = 0.02
        gdp_mean = 0.02

        # Volatility parameters
        interest_vol = 0.02
        unemployment_vol = 0.01
        sentiment_vol = 0.3
        inflation_vol = 0.01
        gdp_vol = 0.02

        # Mean reversion speeds
        interest_speed = 0.5
        unemployment_speed = 0.3
        sentiment_speed = 1.0
        inflation_speed = 0.4
        gdp_speed = 0.6

        # Generate random shocks (Wiener process)
        z_interest = random.gauss(0, 1)
        z_unemployment = random.gauss(0, 1)
        z_sentiment = random.gauss(0, 1)
        z_inflation = random.gauss(0, 1)
        z_gdp = random.gauss(0, 1)

        # Update interest rate (Ornstein-Uhlenbeck process)
        drift_interest = interest_speed * (interest_mean - self.state.interest_rate)
        diffusion_interest = interest_vol * math.sqrt(self.dt) * z_interest
        self.state.interest_rate += drift_interest * self.dt + diffusion_interest
        self.state.interest_rate = max(0.0, min(0.15, self.state.interest_rate))  # Cap at 0-15%

        # Update unemployment (with correlation to GDP growth)
        drift_unemployment = unemployment_speed * (unemployment_mean - self.state.unemployment_rate)
        drift_unemployment -= 0.5 * self.state.gdp_growth  # Strong economy reduces unemployment
        diffusion_unemployment = unemployment_vol * math.sqrt(self.dt) * z_unemployment
        self.state.unemployment_rate += drift_unemployment * self.dt + diffusion_unemployment
        self.state.unemployment_rate = max(0.01, min(0.15, self.state.unemployment_rate))  # Cap at 1-15%

        # Update sentiment (affected by economic conditions)
        # Good GDP growth and low unemployment improve sentiment
        sentiment_adjustment = 0.5 * self.state.gdp_growth - 0.3 * (self.state.unemployment_rate - unemployment_mean)
        drift_sentiment = sentiment_speed * (sentiment_mean + sentiment_adjustment - self.state.sentiment)
        diffusion_sentiment = sentiment_vol * math.sqrt(self.dt) * z_sentiment
        self.state.sentiment += drift_sentiment * self.dt + diffusion_sentiment
        self.state.sentiment = max(-1.0, min(1.0, self.state.sentiment))  # Cap at -1 to 1

        # Update inflation (correlated with interest rates inversely)
        drift_inflation = inflation_speed * (inflation_mean - self.state.inflation_rate)
        drift_inflation += 0.3 * self.state.gdp_growth  # Strong growth can cause inflation
        diffusion_inflation = inflation_vol * math.sqrt(self.dt) * z_inflation
        self.state.inflation_rate += drift_inflation * self.dt + diffusion_inflation
        self.state.inflation_rate = max(0.0, min(0.10, self.state.inflation_rate))  # Cap at 0-10%

        # Update GDP growth (affected by interest rates and sentiment)
        drift_gdp = gdp_speed * (gdp_mean - self.state.gdp_growth)
        drift_gdp -= 0.4 * (self.state.interest_rate - interest_mean)  # High rates slow growth
        drift_gdp += 0.2 * self.state.sentiment  # Positive sentiment boosts growth
        diffusion_gdp = gdp_vol * math.sqrt(self.dt) * z_gdp
        self.state.gdp_growth += drift_gdp * self.dt + diffusion_gdp
        self.state.gdp_growth = max(-0.05, min(0.08, self.state.gdp_growth))  # Cap at -5% to 8%

        # Increment time step
        self.state.time_step += 1

        # Store in history
        self.history.append(self._copy_state())

    def get_state(self) -> EconomicState:
        """Get the current economic state"""
        return self._copy_state()

    def get_history(self, steps: int = None) -> List[EconomicState]:
        """Get historical economic data"""
        if steps is None:
            return self.history.copy()
        return self.history[-steps:]

    def get_risk_free_rate(self) -> float:
        """Get the current risk-free rate for asset pricing"""
        return self.state.interest_rate

    def get_market_volatility(self) -> float:
        """
        Calculate implied market volatility based on economic conditions.
        Higher unemployment and negative sentiment increase volatility.
        """
        base_vol = 0.15  # 15% base volatility
        unemployment_factor = self.state.unemployment_rate * 2.0
        sentiment_factor = -self.state.sentiment * 0.5  # Negative sentiment increases vol

        volatility = base_vol + unemployment_factor + sentiment_factor
        return max(0.05, min(0.50, volatility))  # Cap between 5% and 50%
