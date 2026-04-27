# NaverStock Web API Catalog

Base observation date: 2026-04-27
Observed from: public `https://stock.naver.com/` pages and Next.js chunks in a non-authenticated session.
Primary host: `https://stock.naver.com`

Naver Stock internal APIs are undocumented and can change without notice. Re-verify endpoints before depending on current production behavior.

This catalog intentionally excludes legacy `finance.naver.com` HTML pages. Add only endpoints visible from `stock.naver.com` pages or relative `stock.naver.com/api/...` calls.

## Status Labels

| Status | Meaning |
| --- | --- |
| `script-backed` | A bundled script calls this endpoint family. |
| `observed` | Observed in public page traffic or static chunks, but not wrapped by a script. |
| `needs-recheck` | Route, enum, auth sensitivity, or pagination shape needs fresh verification. |
| `excluded` | Outside read-only stock/market information scope. Do not call. |

## Identifier Conventions

| Identifier | Example | Meaning |
| --- | --- | --- |
| `itemCode` | `005930` | Six-digit Korean stock code. |
| `codeType` | `KRX`, `NXT` | Domestic detail trade route. |
| `itemCodes` | `005930,000660` | Comma-separated domestic stock/index code list. |
| `reutersCode` | `KOSPI`, `GCcv1` | Index, futures, or indicator code used by market indicator APIs. |
| `fqnfTicker` | `BTC_KRW_UPBIT` | Crypto ticker used by polling endpoints. |
| `market` | `UPBIT`, `BITHUMB` | Crypto exchange enum; uppercase is required. |

## Domestic Stock APIs

| Purpose | Status | Method | Path / params |
| --- | --- | ---: | --- |
| Stock detail | `script-backed` | GET | `/api/domestic/detail/{itemCode}/detail?codeType=KRX` or `NXT` |
| Stock price tab | `script-backed` | GET | `/api/domestic/detail/{itemCode}/price` |
| Stock hoga / order book | `script-backed` | GET | `/api/domestic/detail/{itemCode}/hoga` |
| Stock daily prices | `script-backed` | GET | `/api/domestic/detail/{itemCode}/siseDay?pageSize=20&bizdate={yyyyMMdd}` |
| Stock ticks | `script-backed` | GET | `/api/domestic/detail/{itemCode}/siseTick?startIdx=0&pageSize=20` |
| Stock investor trend rows | `script-backed` | GET | `/api/domestic/detail/{itemCode}/trend?tradeType=KRX&startIdx=0&pageSize=20` |
| Stock broker trader info | `script-backed` | GET | `/api/domestic/detail/{itemCode}/traderInfo` |
| Stock chart payload | `script-backed` | GET | `/api/securityFe/api/fchart/domestic/stock/{itemCode}?periodType=day&range={range}` |
| Market classification | `script-backed` | GET | `/api/domestic/detail/{itemCode}/sosok` |
| Consensus | `script-backed` | GET | `/api/domestic/detail/{itemCode}/consensus` |
| Industry peers | `script-backed` | GET | `/api/domestic/detail/{itemCode}/stock/industry?page=1&pageSize=10&marketType=ALL` |
| Stock news | `script-backed` | GET | `/api/domestic/detail/news?itemCode={itemCode}&page=1&pageSize=20` |
| Stock disclosures / 공시 | `script-backed` | GET | `/api/domestic/detail/notice?itemCode={itemCode}&startIdx=0&pageSize=20&causeCode={code}` |
| Stock IR list | `script-backed` | GET | `/api/domestic/detail/ir?itemCode={itemCode}&startIdx=0&pageSize=20` |
| Stock IR detail | `script-backed` | GET | `/api/domestic/detail/ir/{itemCode}/{articleId}` |
| Aggregate investor poll statistics | `script-backed` | GET | `/api/stockDomestic/invest-info/poll/statistics/{itemCode}` |
| Aggregate investor distribution resources | `script-backed` | GET | `/api/myasset/resources/invest/{stock-trade\|stock-investor-rank\|stock-invest-rate\|stock-investor-age\|stock-floor}?item_code={itemCode}` |
| Stock info tabs | `needs-recheck` | GET | `/domestic/stock/{itemCode}/info/{company\|overview\|financial\|investment\|consensus\|industry\|sector\|share\|esg}` route chunks reference stock info APIs, but simple direct guesses under `/api/securityFe/api/stock/*` and `/api/securityService/stock/*` returned 404/409 in spot checks |
| Realtime polling quote | `script-backed` | GET | `/api/polling/domestic/stock?itemCodes={codes}` |
| NXT polling quote | `observed` | GET | `/api/polling/domestic/NXT/stock?itemCodes={codes}` |
| Market stock default list | `script-backed` | GET | `/api/domestic/market/stock/default?tradeType=KRX&marketType=ALL&orderType=marketSum&startIdx=0&pageSize=20` |
| Dividend list | `script-backed` | GET | `/api/domestic/market/stock/dividend?page=1&pageSize=20` |
| Search popularity | `script-backed` | GET | `/api/domestic/market/searchTop?page=1&pageSize=20` |
| IPO progress | `script-backed` | GET | `/api/domestic/market/ipo/progress?page=1&pageSize=20` |
| Sector/theme ranking | `script-backed` | GET | `/api/domestic/home/upjongTheme/ranking?rankingType=upjong&page=1&pageSize=20` |
| Industry/theme/group ranking list | `script-backed` | GET | `/api/domestic/market/{upjong\|theme\|group}/list?startIdx=0&pageSize=100&sortType=changeRate` |
| Industry/theme/group detail info | `script-backed` | GET | `/api/domestic/market/{upjong\|theme\|group}/{no}/info?marketType=ALL` |
| Industry/theme/group constituent stocks | `script-backed` | GET | `/api/domestic/market/{upjong\|theme\|group}/{no}/stocklist?marketType=ALL&orderType=quantTop&startIdx=0&pageSize=20` |
| Market aggregate investor trend | `needs-recheck` | POST | `/api/domestic/home/marketaggregate/aggregateInvestor` with JSON body containing `sections`, `tradeType`, `marketType`, `periodType`, and dates |
| Market aggregate investor ranking | `needs-recheck` | POST | `/api/domestic/home/marketaggregate/aggregateInvestorRanking` with ranking section fields, `startIdx`, and `pageSize` |
| Investor deposit list | `observed` | GET | `/api/domestic/market/trendDeposit?startIdx=0&pageSize=20` |
| Investor deposit chart | `observed` | GET | `/api/domestic/market/trendDeposit/chart?startDate={yyyyMMdd}&endDate={yyyyMMdd}` |
| Sector total market cap | `observed` | GET | `/api/domestic/market/home/upjong/totalMarketSum?type=upjong` |
| ETF themes | `observed` | GET | `/api/domestic/market/etf/themes` |
| Domestic ETF list | `script-backed` | GET | `/api/stockSecurity/etfs/v1/domestic?listingType=tradingValueDesc&size=20&index=0` |
| Domestic ETF category metadata | `script-backed` | GET | `/api/stockSecurity/etfs/v1/domestic/themes` |
| Domestic ETF leverage metadata | `script-backed` | GET | `/api/stockSecurity/etfs/v1/domestic/leverage-types` |
| ETF base info | `script-backed` | GET | `/api/domestic/detail/{itemCode}/ETFBase` |
| ETF dividend summary | `script-backed` | GET | `/api/domestic/detail/{itemCode}/ETFDividend` |
| ETF dividend history | `script-backed` | GET | `/api/domestic/detail/{itemCode}/ETFDividendHist?startIdx=0&pageSize=20` |
| ETF components | `script-backed` | GET | `/api/domestic/detail/{itemCode}/ETFComponent?startIdx=0&pageSize=20` |
| ETF theme tags | `script-backed` | GET | `/api/domestic/detail/{itemCode}/ETFTheme` |
| ETF fund-flow day/week | `script-backed` | GET | `/api/domestic/detail/{itemCode}/ETFSumFlowDayList?count=20`, `/ETFSumFlowWeekList?count=20` |
| Domestic ETN list | `script-backed` | GET | `/api/domestic/market/etn?orderType=AMOUNT_ETN&startIdx=0&pageSize=20` |
| Notable ETF | `observed` | GET | `/api/domestic/market/home/notableETF?orderType=up_etf&startIdx=0&pageSize=10` |

Observed stock-list `orderType` values include `marketSum`, `accAmount`, `searchTop`, `up`, `steady`, `down`, `quantTop`, and alert-related order types such as `investmentCaution`, `investmentWarning`, and `investmentRisk`.

The `stock.naver.com/market/stock/kr/{industry|theme|groups}/{rank}` pages resolve the path rank to a current category `no` from the list API, then call `info` and `stocklist`. The API path uses `upjong` for `industry`, `theme` for `theme`, and `group` for `groups`. Directly calling `/industry/1` as a category id is incorrect because `1` is the page rank, not necessarily the category `no`.

Observed category stock-list `orderType` values include `quantTop`, `priceTop`, `up`, `down`, `marketSum`, `sales`, and `operatingProfit`. UI chip aliases map as `accQuant -> quantTop` and `accAmount -> priceTop`.

Observed domestic stock-menu routes opened successfully on 2026-04-27: `/market/stock/kr/stocklist/*`, `/market/stock/kr/etf/*`, `/market/stock/kr/etn`, `/market/stock/kr/ipo*`, `/market/stock/kr/deposit`, `/market/stock/kr/trend/{foreigner|organization|program|trader}`, and stock detail subpages `/domestic/stock/{itemCode}/{price|news|notice|ir|discussion|research}`. Routes such as `/domestic/stock/{itemCode}/financial`, `/total`, `/chart`, `/analysis`, and `/investment` returned 404 in direct checks.

Domestic ETF `listingType` aliases observed from UI chunks include `tradingValueDesc`, `aumDesc`, `changeRateDescUpAll`, `changeRateDescDownAll`, `tradingVolumeDesc`, `tradingVolumeIncreaseRateDesc`, `tradingVolumeIncreaseRateAsc`, `returnRate1mDesc`, `returnRate3mDesc`, `returnRate6mDesc`, `marketCapDesc`, and `listedAtDesc`.

Domestic ETN `orderType` values observed from UI chunks include `MARKET_SUM_ETN`, `AMOUNT_ETN`, `UP_ETN`, `DOWN_ETN`, `QUANT_ETN`, `QUANT_HIGH_ETN`, `QUANT_LOW_ETN`, and `NEW_STOCK_ETN`.

Foreign stock routes such as `/market/stock/global`, `/market/stock/usa/stocklist`, and country subpages under `/market/stock/global/{chn|hkg|jpn|vnm}` are reachable and expose `/api/foreign/*`, `/api/securityService/stock/*`, `/api/securityService/etf/*`, and worldstock polling families. They are stock-related but are kept separate from the domestic scripts to avoid mixing code systems.

## Market Index And Indicators

| Purpose | Status | Method | Path / params |
| --- | --- | ---: | --- |
| Major indices | `script-backed` | GET | `/api/securityFe/api/index/majors` |
| Market-index major blocks | `observed` | GET | `/api/securityService/marketindex/majors/{type}` where observed `type` values include `exchange`, `exchangeWorld`, `domesticInterest`, and `rpc` |
| Index basic | `observed` | GET | `/api/securityFe/api/index/{reutersCode}/basic` |
| Index integration | `observed` | GET | `/api/securityFe/api/index/{reutersCode}/integration` |
| Index price history | `observed` | GET | `/api/securityFe/api/index/{reutersCode}/price?page=1&pageSize=20` |
| Domestic index polling | `script-backed` | GET | `/api/polling/domestic/index?itemCodes=KOSPI,KOSDAQ,KPI200` |
| Index chart | `script-backed` | GET | `/api/securityService/chart/domestic/index/{code}?periodType=day` |
| Commodity indicators | `script-backed` | GET | `/api/securityService/marketindex/energy`, `/metals`, `/agricultural` |
| Domestic interest rates | `script-backed` | GET | `/api/securityService/marketindex/domesticInterest` |
| Other indicator categories | `observed` | GET | `/api/securityService/marketindex/exchange`, `/bond`, `/standardInterest`, and detail paths under those categories |
| Indicator detail | `script-backed` | GET | `/api/securityService/marketindex/{energy\|metals\|agricultural\|exchange}/{reutersCode}` |
| Indicator price history | `script-backed` | GET | `/api/securityService/marketindex/{energy\|metals\|agricultural\|exchange}/{reutersCode}/prices?page=1&pageSize=20` |
| Bond by nation | `script-backed` | GET | `/api/securityService/marketindex/bond/nation/{nationType}?sortType={sortType}` |
| Standard interest detail | `script-backed` | GET | `/api/securityService/marketindex/standardInterest/{nationType}` |
| Economic upcoming indicators | `script-backed` | GET | `/api/securityService/economic/indicator/nations/upcoming?limit=10&nationTypeList=USA` |
| Economic release-date indicators | `script-backed` | GET | `/api/securityService/economic/indicator/nations/releaseDate?page=1&pageSize=20&releaseDate={yyyyMMdd}` |
| Exchange-rate helper | `script-backed` | GET | `/api/stockDomestic/exchangeRates/list?currencies=USD,JPY` |
| Market-index polling | `observed` | GET | `/api/polling/marketindex/{category}/{codes}` |
| Integration indicators | `observed` | GET | `/api/securityService/integration/indicators?stockType=domestic&indicatorCodes=KOSPI&indicatorCodes=KOSDAQ` |
| Integration prices | `observed` | GET | `/api/securityService/integration/price?domesticKrxCodes=005930&foreignCodes=.IXIC&cryptoCodes=BTC_KRW_UPBIT` |

Some older-looking routes such as `/api/securityService/marketindex/majors` returned 404 on 2026-04-27; use `/api/securityFe/api/index/majors`.

## Crypto APIs

| Purpose | Status | Method | Path / params |
| --- | --- | ---: | --- |
| Ranking list | `script-backed` | GET | `/api/coin/rank/{market}?sortType=marketValue&page=1&pageSize=60` |
| Major coins | `script-backed` | GET | `/api/coin/rank/{market}/majors` |
| Coin price by market | `script-backed` | GET | `/api/coin/price/{market}/{ticker}` |
| Coin price across exchanges | `script-backed` | GET | `/api/coin/price/{ticker}?excludeExchange={market}` |
| Polling prices | `script-backed` | GET | `/api/polling/coin/price?fqnfTickers=BTC_KRW_UPBIT` |
| Minute candles | `script-backed` | GET | `/api/coin/candle/{market}/KRW/{ticker}/minutes/{unit}/marketInfo?from={iso}&to={iso}` |

Use uppercase `UPBIT` or `BITHUMB`. The polling endpoint accepts `fqnfTicker` values such as `BTC_KRW_UPBIT`; plain `KRW-BTC` returned an empty list in direct checks.

## News APIs

| Purpose | Status | Method | Path / params |
| --- | --- | ---: | --- |
| News list | `script-backed` | GET | `/api/domestic/news/list?category=mainnews&page=1&pageSize=20` |
| Focus news | `script-backed` | GET | `/api/domestic/news/focus?sid=401&page=1&pageSize=20` |
| News search | `script-backed` | GET | `/api/domestic/news/search?query=반도체&page=1&pageSize=20` |
| Market disclosure/notice news | `script-backed` | GET | `/api/domestic/news/noticeList?page=1&pageSize=20&keyword={keyword}&typeIdx={idx}` |
| World/foreign market news | `script-backed` | GET | `/api/foreign/news/worldNews?page=1&pageSize=20&date={yyyyMMdd}` |
| News aggregate home | `script-backed` | GET | `/api/domestic/news/aggregate/home?flashNewsSize=5&mainNewsSize=5&rankingNewsSize=5&overseasNewsSize=5&focusSize=5&moneyStorySize=5&noticeSize=5` |

Observed list categories include `mainnews`, `flashnews`, and `ranknews`; ad hoc values such as `stock`, `market`, and `all` can fail. Observed focus section map: `market-outlook=401`, `company-analysis=402`, `global-market=403`, `bond-futures=404`, `disclosure-memo=406`, `exchange-rate=429`.

## Research APIs

| Purpose | Status | Method | Path / params |
| --- | --- | ---: | --- |
| Research category list | `script-backed` | GET | `/api/domestic/research/category?category=COMPANY&page=1&pageSize=15` |
| Category detail | `script-backed` | GET | `/api/domestic/research/category/{researchId}?category=COMPANY` |
| Stock report list | `observed` | GET | `/api/domestic/research/{itemCode}/research?page=0&size=30` |
| Stock report detail | `observed` | GET | `/api/domestic/research/{itemCode}/research/{researchId}` |
| Recent popular | `script-backed` | GET | `/api/domestic/research/recent-popular` |
| Research home aggregate | `script-backed` | POST | `/api/domestic/home/researchaggregate/static` with boolean `sections` such as `researchCategory`, `researchRanking`, `recentPopular` |
| Category latest | `observed` | GET | `/api/domestic/research/category-lastest` |
| Industry research | `observed` | GET | `/api/domestic/research/industry-research` |
| Ranking | `observed` | GET | `/api/domestic/research/ranking?rankingType={type}&selectedRank={rank}` |
| Broker list | `script-backed` | GET | `/api/domestic/research/broker-list` |

Category enum values observed from validation errors and chunks: `INVEST`, `MARKET`, `INDUSTRY`, `COMPANY`, `ECONOMY`, `DEBENTURE`.

## Discussion APIs

| Purpose | Status | Method | Path / params |
| --- | --- | ---: | --- |
| Hot feed | `observed` | GET | `/api/community/discussion/posts/hot?pageSize=20&page=1&discussionType={type}&itemCode={itemCode}` |
| Hot home feed | `observed` | GET | `/api/community/discussion/posts/hot/home?pageSize=20&page=1` |
| Post detail | `script-backed` | GET | `/api/community/discussion/posts/{postId}` |
| Adjacent post navigation | `script-backed` | GET | `/api/community/discussion/posts/{postId}/adjacent?pageSize=20&itemCode={itemCode}` |
| Related hot posts | `script-backed` | GET | `/api/community/discussion/posts/related/hot?itemCode={itemCode}&pageSize=20&discussionType=domesticStock` |
| Popular hot posts | `script-backed` | GET | `/api/community/discussion/posts/popular/hot` |
| Market feed | `observed` | GET | `/api/community/discussion/posts/market?offset={offset}&pageSize=20` |
| Item posts | `observed` | GET | `/api/community/discussion/posts?itemCode={itemCode}&pageSize=20` |
| Posts by item | `observed` | GET | `/api/community/discussion/posts/by-item?itemCode={itemCode}&pageSize=20` |
| Posts by item codes | `observed` | GET | `/api/community/discussion/posts/by-item-codes?filterType=itemCodes&pageSize=20&offset={offset}&domesticCodes={codes}` |
| Latest item posts | `observed` | GET | `/api/community/discussion/items/posts/latest?domesticCodes={codes}&limit=10` |
| Comment counts | `observed` | GET | `/api/community/discussion/posts/comment-counts?postIds={ids}` |
| Reactions | `observed` | GET | `/api/community/discussion/posts/reactions?postIds={ids}` |
| Rankings | `observed` | GET | `/api/community/discussion/rankings?nationType=KOR&page=1&size=20&postType=HOT` |
| Item stats | `observed` | GET | `/api/community/discussion/stats/by-items?itemCodes={codes}` |

Avoid write, profile-editing, image-upload, nickname validation/recommendation, reaction mutation, and authenticated community profile workflows.

## Excluded Families

| Family | Status | Reason |
| --- | --- | --- |
| `/api/auth/*` | `excluded` | Login/authentication. |
| `/api/personal/users/holding/*` | `excluded` | Account holdings and refresh workflows. |
| `/api/personal/users/favorite/*` | `excluded` | User-specific favorites and groups. |
| `/api/personal/users/notification*` | `excluded` | User notification settings/messages. |
| `/api/community/profile/users/*` mutation-like routes | `excluded` | User profile and image workflows. |
| `https://finance.naver.com/*` | `excluded` | Legacy HTML pages outside the `stock.naver.com` scope requested for this skill. |
| Telemetry, ads, static chunks, fonts, images | `excluded` | Not stock-information APIs. |
