# haggle-agent

> **Honey that haggles for you** — your agent negotiates the price.

Honey finds coupons. `haggle-agent` goes further: it negotiates. With a
seller's chat bot, a sales rep over email, a Facebook Marketplace seller, a
SaaS renewal. It's the negotiation brain: strategy, offers, acceptance
rules and the messages, with a simulator to test strategies before they
touch real money.

## What the MVP does

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
