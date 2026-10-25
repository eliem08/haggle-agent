import argparse
import csv
import math
import os
import sys

from .core import STRATEGIES, Brief, simulate, tournament


def _finite_float(s: str) -> float:
    """argparse type: a float that is not nan/inf, so limits and prices cannot be bypassed."""
    v = float(s)
    if not math.isfinite(v):
        raise argparse.ArgumentTypeError(f"must be a finite number, got {s!r}")
    return v


LEVERAGE = ["a competitor quoted me lower last week", "I can pay in full upfront", "I'm buying two more next quarter"]


def build_parser():
    ap = argparse.ArgumentParser(prog="haggle-agent")
    sub = ap.add_subparsers(dest="cmd", required=True)
    for name in ("simulate", "tournament"):
        p = sub.add_parser(name)
        p.add_argument("--list", type=_finite_float, required=True, dest="list_price")
        p.add_argument("--target", type=_finite_float, required=True)
        p.add_argument("--walkaway", type=_finite_float, required=True)
        p.add_argument("--rounds", type=int, default=8)
        if name == "simulate":
            p.add_argument("--seller-reserve", type=_finite_float, required=True)
            p.add_argument("--seller-e", type=_finite_float, default=0.5)
            p.add_argument("--strategy", choices=sorted(STRATEGIES), default="boulware")
    return ap


def _run(argv=None):
    ap = build_parser()
    a = ap.parse_args(argv)
    brief = Brief(a.list_price, a.target, a.walkaway, a.rounds, LEVERAGE)
    if a.cmd == "tournament":
        for r in tournament(brief):
            print(f"{r['strategy']:<12} deal rate {r['deal_rate']:.0%}  avg savings ${r['avg_savings']:,.2f}")
        return 0
    res = simulate(brief, a.seller_reserve, a.strategy, a.seller_e)
    for turn in res["transcript"]:
        if turn[0] == "seller":
            print(f"  seller asks  ${turn[1]:,.2f}")
        else:
            print(f'  we offer     ${turn[1]:,.2f}   "{turn[2]}"')
    if res["outcome"] == "deal":
        print(
            f"DEAL at ${res['price']:,.2f} in {res['rounds']} rounds ({res['how']}); saved ${res['savings']:,.2f} ({res['savings_pct']:.1%})"
        )
    else:
        print("NO DEAL - walked away at the deadline")
    return 0


def main(argv=None):
    """Run the CLI; a bad input file or argument exits 2 with a one-line error instead of a traceback.

    Set AGENT_ECONOMY_DEBUG=1 to see the full traceback.
    """
    if hasattr(sys.stdout, "reconfigure"):
        sys.stdout.reconfigure(errors="replace")
    try:
        return _run(argv)
    except (OSError, ValueError, KeyError, csv.Error) as e:
        if os.environ.get("AGENT_ECONOMY_DEBUG"):
            raise
        msg = e.args[0] if isinstance(e, KeyError) and e.args else e
        print(f"error: {msg}", file=sys.stderr)
        return 2


if __name__ == "__main__":
    sys.exit(main())
