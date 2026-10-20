"""
Paper Trading Engine
Copies detected wallet BUY/SELL signals in PAPER mode only.
No real orders are placed.
"""

from dataclasses import dataclass, asdict
from datetime import datetime, timezone
from typing import Dict, Optional


@dataclass
class Position:
    token: str
    quantity: float
    entry_price: float
    entry_time: str
    invested: float


class PaperTrader:
    def __init__(self, starting_balance: float = 1000.0):
        self.starting_balance = float(starting_balance)
        self.balance = float(starting_balance)

        self.positions: Dict[str, Position] = {}
        self.trade_history = []

    def buy(
        self,
        token: str,
        price: float,
        amount_usd: float,
        timestamp: Optional[str] = None,
    ):
        if price <= 0:
            raise ValueError("BUY price must be greater than 0")

        if amount_usd <= 0:
            raise ValueError("BUY amount must be greater than 0")

        if amount_usd > self.balance:
            print(
                f"[PAPER] BUY skipped: insufficient balance "
                f"(${self.balance:.2f})"
            )
            return None

        timestamp = timestamp or self._now()
        quantity = amount_usd / price

        # If already holding the token, add to the position.
        if token in self.positions:
            position = self.positions[token]

            total_invested = position.invested + amount_usd
            total_quantity = position.quantity + quantity

            position.quantity = total_quantity
            position.entry_price = total_invested / total_quantity
            position.invested = total_invested

        else:
            self.positions[token] = Position(
                token=token,
                quantity=quantity,
                entry_price=price,
                entry_time=timestamp,
                invested=amount_usd,
            )

        self.balance -= amount_usd

        trade = {
            "side": "BUY",
            "token": token,
            "price": price,
            "quantity": quantity,
            "amount_usd": amount_usd,
            "timestamp": timestamp,
        }

        self.trade_history.append(trade)

        print(
            f"[PAPER BUY] {token} | "
            f"Price=${price:.10f} | "
            f"Amount=${amount_usd:.2f} | "
            f"Qty={quantity:.8f}"
        )

        return trade

    def sell(
        self,
        token: str,
        price: float,
        quantity: Optional[float] = None,
        timestamp: Optional[str] = None,
    ):
        if price <= 0:
            raise ValueError("SELL price must be greater than 0")

        if token not in self.positions:
            print(f"[PAPER] SELL skipped: no open position for {token}")
            return None

        timestamp = timestamp or self._now()
        position = self.positions[token]

        sell_quantity = (
            position.quantity if quantity is None
            else min(float(quantity), position.quantity)
        )

        if sell_quantity <= 0:
            return None

        proceeds = sell_quantity * price
        cost = sell_quantity * position.entry_price
        pnl = proceeds - cost
        pnl_percent = (pnl / cost * 100) if cost else 0

        self.balance += proceeds
        position.quantity -= sell_quantity
        position.invested -= cost

        if position.quantity <= 1e-12:
            del self.positions[token]

        trade = {
            "side": "SELL",
            "token": token,
            "price": price,
            "quantity": sell_quantity,
            "amount_usd": proceeds,
            "cost_basis": cost,
            "pnl_usd": pnl,
            "pnl_percent": pnl_percent,
            "timestamp": timestamp,
        }

        self.trade_history.append(trade)

        print(
            f"[PAPER SELL] {token} | "
            f"Price=${price:.10f} | "
            f"Value=${proceeds:.2f} | "
            f"P&L=${pnl:.2f} ({pnl_percent:.2f}%)"
        )

        return trade

    def get_position(self, token: str):
        position = self.positions.get(token)

        if position is None:
            return None

        return asdict(position)

    def get_status(self):
        return {
            "starting_balance": round(self.starting_balance, 2),
            "cash_balance": round(self.balance, 2),
            "open_positions": {
                token: asdict(position)
                for token, position in self.positions.items()
            },
            "total_trades": len(self.trade_history),
        }

    def get_trade_history(self):
        return self.trade_history

    @staticmethod
    def _now():
        return datetime.now(timezone.utc).isoformat()


if __name__ == "__main__":
    # Simple local test
    trader = PaperTrader(starting_balance=1000)

    trader.buy(
        token="TEST",
        price=1.00,
        amount_usd=100,
    )

    trader.sell(
        token="TEST",
        price=1.20,
    )

    print("\nFINAL PAPER ACCOUNT")
    print(trader.get_status())
