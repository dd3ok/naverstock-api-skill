# Response Notes

## Common Shapes

- Most Naver Stock endpoints return the payload directly, not under a common `result` wrapper.
- Validation errors often return `detailCode` and `message`; scripts treat these as failed requests when HTTP status is not enough.
- Domestic stock detail fields use legacy lowercase keys such as `itemcode`, `itemname`, `nowPrice`, `prevChangeRate`, and `marketSum`.
- Polling endpoints return `{ "pollingInterval": ..., "datas": [...] }`.
- Research category responses return `{ "content": [...], "totalElements": ... }`.
- Crypto rank responses return `{ "contents": [...] }`, while major coin endpoints return a list.

## Useful Enums

- Domestic `codeType`: `KRX`, `NXT`.
- Domestic market list `tradeType`: `KRX`, `NXT`.
- Domestic market list `marketType`: `ALL`, `KOSPI`, `KOSDAQ`.
- Research category: `INVEST`, `MARKET`, `INDUSTRY`, `COMPANY`, `ECONOMY`, `DEBENTURE`.
- Crypto market: `UPBIT`, `BITHUMB`.
- News focus slugs: `market-outlook`, `company-analysis`, `global-market`, `bond-futures`, `disclosure-memo`, `exchange-rate`.
- News list categories: `mainnews`, `flashnews`, `ranknews`.
- Category page types: `industry`, `theme`, `groups`; API path types: `upjong`, `theme`, `group`.
- Category stock-list chip aliases: `accQuant -> quantTop`, `accAmount -> priceTop`, plus `up`, `down`, `marketSum`, `sales`, `operatingProfit`.
- ETF list aliases: `priceTop -> tradingValueDesc`, `capitalization -> aumDesc`, `upper -> changeRateDescUpAll`, `lower -> changeRateDescDownAll`, `trading -> tradingVolumeDesc`.
- ETN list aliases: `priceTop -> AMOUNT_ETN`, `marketSum -> MARKET_SUM_ETN`, `trading -> QUANT_ETN`, `upper -> UP_ETN`, `lower -> DOWN_ETN`.

## Cautions

- For user-facing answers, disclose when data came from unofficial `stock.naver.com/api` calls and avoid implying official support, guaranteed accuracy, or investment suitability.
- `/api/securityService/marketindex/majors` returned 404 on 2026-04-27; `/api/securityFe/api/index/majors` worked.
- Crypto polling needs `fqnfTicker` like `BTC_KRW_UPBIT`, not `KRW-BTC`.
- News list category `main` failed in verification; use `mainnews` unless live traffic shows a newer value.
- Some chart routes are strict about path enums. Verify a small request before adding a new chart script path.
- Naver Stock may format numeric fields as strings with commas in polling responses and plain numeric strings in detail responses.
- Keep the skill scoped to `stock.naver.com`. Do not use `finance.naver.com` group-detail HTML to infer theme or industry constituents.
- The `/market/stock/kr/{industry|theme|groups}/{rank}` route uses rank in the path. Resolve that rank to the current category `no` via `/api/domestic/market/{upjong|theme|group}/list` before calling `info` or `stocklist`.
- Stock disclosure/IR endpoints use `startIdx`, while stock news uses `page`. Do not assume one pagination style across detail subpages.
- Price-tab endpoints mix pagination styles: `siseDay` uses `pageSize` and optional `bizdate`; `siseTick` and investor `trend` use `startIdx` plus `pageSize`.
- `/api/myasset/resources/invest/*` endpoints observed from stock detail pages returned aggregate investor distributions without authentication in checks, but keep account/holding endpoints under `/api/personal/users/*` excluded.
