# Redemption Access & Arbitrage Gating by Issuer

This determines which computed spreads are labeled "closeable" vs
"wrapper basis" in the product — see PROJECT.md normalization
requirement.

| Issuer | Primary access | Min size | Fees | Who can redeem | US persons |
|---|---|---|---|---|---|
| Dinari | Broker-dealer (Alpaca) mint/burn | Low | Trading fees (flat + variable) | KYC'd users, same-day USDC, US market hours | Yes (accredited / Reg A+) |
| Backed / xStocks | Authorized Participant / issuer | $5,000 redemption (~$100k cited for primary mint) | Spread on issuance; exchange trading fees (e.g. 0.25–0.40%) | Qualified Professional Investors only | No |
| Ondo | Issuer atomic mint/redeem | $1 | Zero mint/redeem fee | Non-US qualified purchasers | No |
| Robinhood (not in v1 scope) | In-app only | €1 | 0.1% FX | No retail redemption to shares | No (EU only) |

## Legal structure notes

- **Dinari dShares**: SEC-registered transfer agent + FINRA
  broker-dealer model. Token = the ledger entry; underlying share sits
  with a regulated custodian. Cleanest US-accessible peg mechanism.
- **Backed / xStocks**: tracker certificate issued by a Jersey SPV
  under a Liechtenstein FMA prospectus. Holder is a *creditor of the
  SPV*, not a direct shareholder. Collateral "may not always consist
  of the underlying shares" per issuer documentation — flag this in
  any user-facing risk copy.
- **Ondo**: structured note vs. a bankruptcy-remote BVI SPV. Same
  creditor-not-shareholder structure as xStocks, different jurisdiction.

## Practical implication for the product

A US-based retail user literally cannot redemption-arb a Dinari/xStocks
gap — one side requires US accreditation, the other explicitly
excludes US persons. This is jurisdictional segmentation, not a market
inefficiency. The dashboard should say this plainly rather than imply
all displayed spreads are tradeable by anyone viewing them.
