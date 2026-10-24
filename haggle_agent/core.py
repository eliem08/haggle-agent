"""Negotiation strategies, acceptance rules, messages and a seller simulator."""
from __future__ import annotations

import itertools
from dataclasses import dataclass, field

__all__ = ["Brief", "Buyer", "Seller", "simulate", "tournament", "STRATEGIES"]

STRATEGIES = {"boulware": 0.25, "linear": 1.0, "conceder": 3.0, "tit_for_tat": None}


@dataclass
class Brief:
    list_price: float
    target: float
    walkaway: float
    rounds: int = 8
    leverage: list = field(default_factory=list)

    def __post_init__(self):
        if not self.target <= self.walkaway <= self.list_price:
            raise ValueError("need target <= walkaway <= list_price")


def _curve(start: float, end: float, t: float, e: float) -> float:
    """Time-dependent concession: f(t) = t^(1/e); e<1 boulware (late), e>1 conceder (early)."""
    return start + (end - start) * (t ** (1 / e))


class Buyer:
    def __init__(self, brief: Brief, strategy: str = "boulware"):
        if strategy not in STRATEGIES:
            raise ValueError(f"unknown strategy {strategy}")
        self.b, self.strategy = brief, strategy
        self.opening = max(brief.target - (brief.list_price - brief.target) * 0.5, brief.target * 0.75)
        self.offers: list[float] = []

    def offer(self, rnd: int, seller_asks: list[float]) -> float:
        b = self.b
        t = rnd / max(b.rounds - 1, 1)
        if self.strategy == "tit_for_tat" and len(seller_asks) >= 2 and self.offers:
            concession = max(0.0, seller_asks[-2] - seller_asks[-1])
            price = self.offers[-1] + concession
        else:
            e = STRATEGIES[self.strategy] or 1.0
            price = _curve(self.opening, b.walkaway, t, e)
        price = round(min(price, b.walkaway), 2)
        if self.offers:
            price = max(price, self.offers[-1])  # never go backwards
        self.offers.append(price)
        return price

    def accepts(self, ask: float, rnd: int, seller_asks: list[float]) -> bool:
        if ask > self.b.walkaway:
            return False
        if ask <= self.b.target:
            return True
        nxt = Buyer(self.b, self.strategy)
        nxt.offers = list(self.offers)
        return ask <= nxt.offer(rnd + 1, seller_asks) if rnd + 1 < self.b.rounds else True

    def message(self, price: float, rnd: int) -> str:
        lev = self.b.leverage
        reason = lev[rnd % len(lev)] if lev else "it's at the top of my budget"
        if rnd == 0:
            return f"Thanks for the quote. I'm ready to move forward today at ${price:,.0f}: {reason}."
        if rnd >= self.b.rounds - 1:
            return f"This is my final offer: ${price:,.0f}. {reason[0].upper() + reason[1:]}. If that works, I'll pay now."
        return f"I hear you. I can come up to ${price:,.0f}; {reason}."


class Seller:
    def __init__(self, list_price: float, reserve: float, rounds: int = 8, e: float = 0.5):
        self.list_price, self.reserve, self.rounds, self.e = list_price, reserve, rounds, e
        self.asks: list[float] = []

    def ask(self, rnd: int) -> float:
        t = rnd / max(self.rounds - 1, 1)
        a = round(self.list_price - (self.list_price - self.reserve) * (t ** (1 / self.e)), 2)
        self.asks.append(a)
        return a

    def accepts(self, offer: float, rnd: int) -> bool:
        return offer >= self.reserve and (offer >= self.ask_preview(rnd + 1) or rnd >= self.rounds - 1)

    def ask_preview(self, rnd: int) -> float:
        t = min(rnd, self.rounds - 1) / max(self.rounds - 1, 1)
        return self.list_price - (self.list_price - self.reserve) * (t ** (1 / self.e))


def simulate(brief: Brief, seller_reserve: float, strategy: str = "boulware", seller_e: float = 0.5, verbose=False) -> dict:
    buyer = Buyer(brief, strategy)
    seller = Seller(brief.list_price, seller_reserve, brief.rounds, seller_e)
    transcript = []
    for rnd in range(brief.rounds):
        ask = seller.ask(rnd)
        transcript.append(("seller", ask))
        if buyer.accepts(ask, rnd, seller.asks):
            return _result(brief, "deal", ask, rnd + 1, transcript, "buyer accepted ask")
        bid = buyer.offer(rnd, seller.asks)
        transcript.append(("buyer", bid, buyer.message(bid, rnd)))
        if seller.accepts(bid, rnd):
            return _result(brief, "deal", bid, rnd + 1, transcript, "seller accepted offer")
    return _result(brief, "no_deal", None, brief.rounds, transcript, "deadline reached")


def _result(brief, outcome, price, rounds, transcript, how):
    return {"outcome": outcome, "price": price, "rounds": rounds, "how": how,
            "savings": round(brief.list_price - price, 2) if price else 0.0,
            "savings_pct": round((brief.list_price - price) / brief.list_price, 4) if price else 0.0,
            "transcript": transcript}


def tournament(brief: Brief, reserves=(0.70, 0.78, 0.85), seller_es=(0.3, 1.0, 2.5)) -> list[dict]:
    rows = []
    for strat in STRATEGIES:
        deals, saved = 0, 0.0
        cases = list(itertools.product(reserves, seller_es))
        for r, e in cases:
            res = simulate(brief, brief.list_price * r, strat, e)
            deals += res["outcome"] == "deal"
            saved += res["savings"]
        rows.append({"strategy": strat, "deal_rate": round(deals / len(cases), 3), "avg_savings": round(saved / len(cases), 2)})
    return sorted(rows, key=lambda r: -r["avg_savings"])
