<!-- sell-kit:start -->
# Haggle Agent

[![CI](https://github.com/eliem08/haggle-agent/actions/workflows/ci.yml/badge.svg)](https://github.com/eliem08/haggle-agent/actions/workflows/ci.yml)

> **An agent that negotiates the price for you.**

**Who it's for:** Shoppers, procurement teams and agentic-commerce apps.

**The problem:** Most prices are negotiable, but few people haggle, and the ones who do leave money on the table.

**What you get:** Proven concession strategies, smart acceptance rules, persuasive messages and a simulator to test tactics against different sellers.

## Quickstart

Customers receive a release archive with the wheel and the examples. Python 3.10+ and no other dependencies.

```bash
pip install haggle_agent-0.1.0-py3-none-any.whl
haggle-agent simulate --list 1200 --target 850 --walkaway 1000 --seller-reserve 900
haggle-agent tournament --list 1200 --target 850 --walkaway 1000
```

## Web app and API

Every command is also a JSON API endpoint and a browser form, served by the built-in web app.

```bash
haggle-agent-web --port 8000          # then open http://127.0.0.1:8000
docker build -t haggle-agent . && docker run -p 8000:8000 -v haggle-agent-data:/data haggle-agent
```

Endpoints: `POST /api/simulate`, `POST /api/tournament`, plus `GET /healthz` and `GET /api/spec` (machine-readable field list).
Files are sent as `{"name": ..., "content": ...}`, folders as `{"files": [...]}` or a base64 zip.

## Pricing

Every plan starts with a 14-day free trial. Prices in USD, billed monthly unless noted.

| Plan | Price | Includes |
|---|---|---|
| **Shopper** | $9 per month | Unlimited negotiations; Message drafts; Strategy simulator |
| **Procurement** | $299 per month | Team seats; Custom walk-away rules; Savings reports |
| **API** | Custom (% of savings, contact sales) | Embed negotiation in your app; Pay only on savings |

To start a trial or buy a plan, email **sales@YOUR-DOMAIN.com**.

## Licence

Proprietary. Copyright (c) 2026 eliem08. All rights reserved. Use requires a paid plan or an active trial; see [LICENSE](LICENSE).
<!-- sell-kit:end -->

## What it does

- **Buyer brief**: list price, target, walk-away (hidden max), deadline in rounds,
  leverage facts (competitor quotes, timing, volume, loyalty)
- **Concession strategies** (time-dependent, from the negotiation literature):
  - `boulware` — concede slowly, hold firm until the deadline
  - `linear`, `conceder` — concede early
  - `tit_for_tat` — mirror the seller's last concession
- **Anchoring**: opening offer from target and list price, never above walk-away
- **Acceptance rule**: accept when the seller's ask ≤ what we'd offer next round
  (AC-next), or ≤ target
- **Message generation**: offers wrapped in a justification drawn from leverage facts
- **Seller simulator** with a hidden reserve price and its own strategy, for backtesting:
  `simulate()` reports deal / no-deal, final price, savings vs. list, rounds
- **Tournament**: run every buyer strategy against every seller type and rank them

## Quickstart

```bash
pip install -e .
haggle-agent simulate --list 1200 --target 850 --walkaway 1000 --seller-reserve 900 --strategy boulware
haggle-agent tournament --list 1200 --target 850 --walkaway 1000
```

## Roadmap

- Channels: email (pairs with agent-telco for SMS), marketplace chat, live seller bots
- Learned seller models from past negotiations (reserve estimation)
- Guardrails: never misrepresent facts; every leverage claim must be verifiable

## Development

Zero runtime dependencies; Python 3.10+.

```bash
python -m venv .venv && source .venv/bin/activate   # Windows: .venv\Scripts\activate
pip install -e ".[dev]"
python -m unittest discover -s tests -t .           # unit + CLI smoke tests
ruff check . && ruff format --check .               # lint + format
```

```
haggle_agent/core.py       domain logic (pure, importable, fully tested)
haggle_agent/__main__.py   CLI (`haggle-agent ...` / `python -m haggle_agent ...`)
tests/                unit tests + generated CLI smoke tests
```

CI runs lint and tests on Ubuntu and Windows across Python 3.10, 3.12 and 3.13.
Design, data model, trade-offs and production path: **[ARCHITECTURE.md](ARCHITECTURE.md)**.

Part of the [agent-economy](https://github.com/eliem08/agent-economy) portfolio (idea #37).
