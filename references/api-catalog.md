# NaverStock Web API 카탈로그

기준 관찰일: 2026-04-27  
관찰 출처: 로그인하지 않은 공개 `https://stock.naver.com/` 페이지와 Next.js chunk  
기본 호스트: `https://stock.naver.com`

네이버증권 내부 API는 문서화되어 있지 않으며 예고 없이 바뀔 수 있습니다. 현재 운영 동작에 의존하기 전에는 엔드포인트를 다시 검증합니다.

이 카탈로그는 레거시 `finance.naver.com` HTML 페이지를 의도적으로 제외합니다. 구버전 네이버 증권 페이지가 필요하면 [dd3ok/naverfinance-api-skills](https://github.com/dd3ok/naverfinance-api-skills)를 참고해 주세요. 이 카탈로그에는 `stock.naver.com` 페이지 또는 상대 `stock.naver.com/api/...` 호출에서 확인되는 엔드포인트만 추가합니다.

## 목차

- [상태 라벨](#상태-라벨)
- [페이지 점검 메모](#페이지-점검-메모)
- [식별자 규칙](#식별자-규칙)
- [국내 주식 API](#국내-주식-api)
- [시장 지수와 지표](#시장-지수와-지표)
- [가상자산 API](#가상자산-api)
- [뉴스 API](#뉴스-api)
- [리서치 API](#리서치-api)
- [종목토론 API](#종목토론-api)
- [제외 계열](#제외-계열)

## 상태 라벨

| 상태 | 의미 |
| --- | --- |
| `script-backed` | 번들 스크립트가 이 엔드포인트 계열을 호출합니다. |
| `observed` | 공개 페이지 트래픽 또는 정적 chunk에서 관찰했지만 스크립트로 감싸지 않았습니다. |
| `needs-recheck` | route, enum, 인증 민감도, 페이징 형태를 새로 검증해야 합니다. |
| `excluded` | 읽기 전용 주식/시장 정보 범위 밖입니다. 호출하지 않습니다. |

## 페이지 점검 메모

2026-04-27 재점검에서는 `https://stock.naver.com/` 루트 HTML과 루트가 로드하는 Next.js chunk 58개에서 route/API 문자열을 추출하고, 후보 route를 작은 직접 요청으로 확인했습니다. `robots.txt`는 `Disallow: /`이고 sitemap은 404라서, 대량 크롤링 대신 루트와 정적 앱 chunk 기반으로만 점검했습니다.

확인된 주요 페이지 route:

| Route | 결과 | 메모 |
| --- | --- | --- |
| `/market` | 307 | `/market/stock/kr/`로 이동 |
| `/market/stock/kr` | 200 | 국내 주식 메인 |
| `/market/stock/kr/stocklist/{top\|priceTop\|trading}` | 200 | 국내 종목 목록 탭 |
| `/market/stock/kr/{industry\|theme\|groups}` | 307 | 각각 `/1`로 이동 |
| `/market/stock/kr/{industry\|theme\|groups}/1` | 200 | path 숫자는 현재 랭킹 순번이며 API category `no`와 다를 수 있음 |
| `/market/stock/kr/etf` | 307 | `/market/stock/kr/etf/priceTop?etfListEntry=1`로 이동 |
| `/market/stock/kr/etf/{priceTop\|trading}` | 200 | 국내 ETF 목록 탭 |
| `/market/stock/kr/etn` | 307 | `/market/stock/kr/etn/priceTop?etnListEntry=1`로 이동 |
| `/market/stock/kr/etn/{priceTop\|trading}` | 200 | 국내 ETN 목록 탭 |
| `/market/stock/kr/ipo` | 200 | IPO 페이지. `/market/stock/kr/ipo/progress`는 404 |
| `/market/stock/kr/deposit` | 200 | 예탁금 페이지 |
| `/market/stock/kr/trend/{foreigner\|organization\|program\|trader}` | 200 | 투자자 동향 페이지 |
| `/market/crypto` | 200 | 가상자산 페이지. `/crypto`는 404 |
| `/market/marketindex` | 307 | `/market/marketindex/major/`로 이동 |
| `/market/marketindex/{major\|energy\|metals\|agricultural\|transport}` | 200 | 주요 시장지표 탭 |
| `/market/marketindex/exchangeRate/exchange` | 200 | 환율 탭. `/exchangeRate`는 이 경로로 이동 |
| `/market/marketindex/bondAndInterest/{bond\|domesticInterest\|standardInterest}` | 200 | 채권/금리 탭 |
| `/market/stock/global`, `/market/stock/usa` | 200 | 해외 주식 메인 |
| `/market/stock/global/{chn\|hkg\|jpn\|vnm}/top` | 200 | 해외 국가별 상위 목록 |
| `/market/stock/global/industry/{chn\|hkg\|jpn\|vnm}` | 307 | 현재 첫 industry code로 이동 |
| `/domestic/stock/{itemCode}` | 307 | `/price`로 이동 |
| `/domestic/stock/{itemCode}/{price\|news\|notice\|ir\|discussion\|research}` | 200 | 종목 상세 하위 페이지 |
| `/domestic/stock/{itemCode}/info/{company\|overview\|financial\|investment\|consensus\|industry\|sector\|share\|esg}` | 200 | 종목 정보 탭 page route |
| `/news`, `/news/mainnews`, `/notice` | 200 | 뉴스/공지 페이지 |
| `/research`, `/research/{daily\|company\|industry\|invest\|economy}` | 200 | 리서치 페이지. `/research/firm`은 404 |
| `/discussion`, `/discussion/feed/{all\|domesticStock\|market\|my}` | 200 | 토론 페이지. `/discussion/feed`는 `/discussion/feed/all`로 이동 |

확인했지만 스킬 범위에서 제외하거나 404였던 route:

- `/market/domestic`, `/market/domestic/stock`, `/market/domestic/etf`, `/market/domestic/etn`, `/market/domestic/ipo`는 404였습니다.
- `/marketindex`는 404였고 `/market/marketindex`를 사용합니다.
- `/my/favorite`는 200이지만 개인/관심종목 페이지라 제외합니다.
- `/market/my/order`, `/my/timeline`, `/my/subscriptions`는 404였습니다.

## 식별자 규칙

| 식별자 | 예시 | 의미 |
| --- | --- | --- |
| `itemCode` | `005930` | 6자리 국내 종목 코드. |
| `codeType` | `KRX`, `NXT` | 국내 종목 상세 거래 route. |
| `itemCodes` | `005930,000660` | comma로 구분한 국내 종목/지수 코드 목록. |
| `reutersCode` | `KOSPI`, `GCcv1` | 시장지표 API에서 쓰는 지수, 선물, 지표 코드. |
| `fqnfTicker` | `BTC_KRW_UPBIT` | 폴링 엔드포인트에서 쓰는 가상자산 ticker. |
| `market` | `UPBIT`, `BITHUMB` | 가상자산 거래소 enum. 대문자가 필요합니다. |

## 국내 주식 API

| 목적 | 상태 | Method | Path / params |
| --- | --- | ---: | --- |
| 종목 상세 | `script-backed` | GET | `/api/domestic/detail/{itemCode}/detail?codeType=KRX` 또는 `NXT` |
| 종목 가격 탭 | `script-backed` | GET | `/api/domestic/detail/{itemCode}/price` |
| 종목 호가 | `script-backed` | GET | `/api/domestic/detail/{itemCode}/hoga` |
| 종목 일별 시세 | `script-backed` | GET | `/api/domestic/detail/{itemCode}/siseDay?pageSize=20&bizdate={yyyyMMdd}` |
| 종목 체결 | `script-backed` | GET | `/api/domestic/detail/{itemCode}/siseTick?startIdx=0&pageSize=20` |
| 종목 투자자 동향 행 | `script-backed` | GET | `/api/domestic/detail/{itemCode}/trend?tradeType=KRX&startIdx=0&pageSize=20` |
| 종목 증권사 거래 정보 | `script-backed` | GET | `/api/domestic/detail/{itemCode}/traderInfo` |
| 종목 차트 payload | `script-backed` | GET | `/api/securityFe/api/fchart/domestic/stock/{itemCode}?periodType=day&range={range}` |
| 시장 구분 | `script-backed` | GET | `/api/domestic/detail/{itemCode}/sosok` |
| 컨센서스 | `script-backed` | GET | `/api/domestic/detail/{itemCode}/consensus` |
| 업종 관련 종목 | `script-backed` | GET | `/api/domestic/detail/{itemCode}/stock/industry?page=1&pageSize=10&marketType=ALL` |
| 종목 뉴스 | `script-backed` | GET | `/api/domestic/detail/news?itemCode={itemCode}&page=1&pageSize=20` |
| 종목 공시 | `script-backed` | GET | `/api/domestic/detail/notice?itemCode={itemCode}&startIdx=0&pageSize=20&causeCode={code}` |
| 종목 IR 목록 | `script-backed` | GET | `/api/domestic/detail/ir?itemCode={itemCode}&startIdx=0&pageSize=20` |
| 종목 IR 상세 | `script-backed` | GET | `/api/domestic/detail/ir/{itemCode}/{articleId}` |
| 집계 투자자 poll 통계 | `script-backed` | GET | `/api/stockDomestic/invest-info/poll/statistics/{itemCode}` |
| 집계 투자자 분포 리소스 | `script-backed` | GET | `/api/myasset/resources/invest/{stock-trade\|stock-investor-rank\|stock-invest-rate\|stock-investor-age\|stock-floor}?item_code={itemCode}` |
| 종목 정보 탭 page route | `observed` | PAGE | `/domestic/stock/{itemCode}/info/{company\|overview\|financial\|investment\|consensus\|industry\|sector\|share\|esg}`. 2026-04-27 직접 확인에서 200을 반환했습니다. 하위 JSON API는 아직 script-backed가 아니므로 필요 시 현재 트래픽으로 재확인합니다. |
| 실시간 폴링 현재가 | `script-backed` | GET | `/api/polling/domestic/stock?itemCodes={codes}` |
| NXT 폴링 현재가 | `observed` | GET | `/api/polling/domestic/NXT/stock?itemCodes={codes}` |
| 국내 시장 기본 종목 목록 | `script-backed` | GET | `/api/domestic/market/stock/default?tradeType=KRX&marketType=ALL&orderType=marketSum&startIdx=0&pageSize=20` |
| 배당 목록 | `script-backed` | GET | `/api/domestic/market/stock/dividend?page=1&pageSize=20` |
| 검색 인기 | `script-backed` | GET | `/api/domestic/market/searchTop?page=1&pageSize=20` |
| IPO 진행 | `script-backed` | GET | `/api/domestic/market/ipo/progress?page=1&pageSize=20` |
| 업종/테마 랭킹 | `script-backed` | GET | `/api/domestic/home/upjongTheme/ranking?rankingType=upjong&page=1&pageSize=20` |
| 업종/테마/그룹사 랭킹 목록 | `script-backed` | GET | `/api/domestic/market/{upjong\|theme\|group}/list?startIdx=0&pageSize=100&sortType=changeRate` |
| 업종/테마/그룹사 상세 정보 | `script-backed` | GET | `/api/domestic/market/{upjong\|theme\|group}/{no}/info?marketType=ALL` |
| 업종/테마/그룹사 구성 종목 | `script-backed` | GET | `/api/domestic/market/{upjong\|theme\|group}/{no}/stocklist?marketType=ALL&orderType=quantTop&startIdx=0&pageSize=20` |
| 시장 집계 투자자 동향 | `needs-recheck` | POST | `/api/domestic/home/marketaggregate/aggregateInvestor`, JSON body는 `sections`, `tradeType`, `marketType`, `periodType`, 날짜를 포함합니다. |
| 시장 집계 투자자 랭킹 | `needs-recheck` | POST | `/api/domestic/home/marketaggregate/aggregateInvestorRanking`, ranking section fields, `startIdx`, `pageSize`를 포함합니다. |
| 투자자 예탁금 목록 | `script-backed` | GET | `/api/domestic/market/trendDeposit?startIdx=0&pageSize=20` |
| 투자자 예탁금 차트 | `script-backed` | GET | `/api/domestic/market/trendDeposit/chart?startDate={yyyyMMdd}&endDate={yyyyMMdd}` |
| 외국인/기관 투자자 동향 랭킹 | `script-backed` | GET | `/api/domestic/market/trend/trendForeignOrg?marketType=ALL&tradeType=KRX&page=1&pageSize=20` |
| 업종 전체 시가총액 | `observed` | GET | `/api/domestic/market/home/upjong/totalMarketSum?type=upjong` |
| ETF 테마 | `observed` | GET | `/api/domestic/market/etf/themes` |
| 국내 ETF 목록 | `script-backed` | GET | `/api/stockSecurity/etfs/v1/domestic?listingType=tradingValueDesc&size=20&index=0` |
| 국내 ETF 카테고리 메타데이터 | `script-backed` | GET | `/api/stockSecurity/etfs/v1/domestic/themes` |
| 국내 ETF 레버리지 메타데이터 | `script-backed` | GET | `/api/stockSecurity/etfs/v1/domestic/leverage-types` |
| ETF 기본 정보 | `script-backed` | GET | `/api/domestic/detail/{itemCode}/ETFBase` |
| ETF 배당 요약 | `script-backed` | GET | `/api/domestic/detail/{itemCode}/ETFDividend` |
| ETF 배당 이력 | `script-backed` | GET | `/api/domestic/detail/{itemCode}/ETFDividendHist?startIdx=0&pageSize=20` |
| ETF 구성 종목 | `script-backed` | GET | `/api/domestic/detail/{itemCode}/ETFComponent?startIdx=0&pageSize=20` |
| ETF 테마 태그 | `script-backed` | GET | `/api/domestic/detail/{itemCode}/ETFTheme` |
| ETF 자금 흐름 일/주 | `script-backed` | GET | `/api/domestic/detail/{itemCode}/ETFSumFlowDayList?count=20`, `/ETFSumFlowWeekList?count=20` |
| 국내 ETN 목록 | `script-backed` | GET | `/api/domestic/market/etn?orderType=AMOUNT_ETN&startIdx=0&pageSize=20` |
| 주목할 ETF | `observed` | GET | `/api/domestic/market/home/notableETF?orderType=up_etf&startIdx=0&pageSize=10` |
| 홈 브리핑 | `observed` | GET | `/api/securityService/home/v3/briefing` |
| 홈 공지 목록 | `observed` | GET | `/api/domestic/home/noticeList?page=1&pageSize=5` |
| 홈 공지 상세 | `observed` | GET | `/api/domestic/home/notice/{noticeId}` |
| 홈 보유자산 랭킹 | `observed` | GET | `/api/domestic/home/ranking/assetAmount/{ageRange}?startIdx=0&pageSize=20`, `ageRange`는 `all`, `20`, `30`, `40`, `50`, `60` |
| 홈 수익률 랭킹 | `observed` | GET | `/api/domestic/home/ranking/earningRate/{ageRange}?startIdx=0&pageSize=20`, `ageRange`는 `all`, `20`, `30`, `40`, `50`, `60` |
| 국내 지수 시간대 시세 | `observed` | GET | `/api/domestic/indexSise/time?koreaIndexType=KOSPI&thistime={yyyyMMddHHmmss}&startIdx=0&pageSize=20` |
| AI 현재 시장 브리핑 | `observed` | GET | `/api/securityAi/marketBriefing/current?marketBriefing={KOSPI\|KOSDAQ}` |

관찰된 종목 목록 `orderType` 값에는 `marketSum`, `accAmount`, `searchTop`, `up`, `steady`, `down`, `quantTop`, 그리고 `investmentCaution`, `investmentWarning`, `investmentRisk` 같은 투자 경고 관련 값이 포함됩니다.

`stock.naver.com/market/stock/kr/{industry|theme|groups}/{rank}` 페이지의 path 값은 현재 카테고리 `no`가 아니라 화면의 랭킹 순번입니다. 먼저 list API에서 현재 카테고리 `no`를 찾은 뒤 `info`와 `stocklist`를 호출합니다. API path는 `industry`에 `upjong`, `theme`에 `theme`, `groups`에 `group`을 사용합니다. `/industry/1`의 `1`은 페이지 rank이며 실제 카테고리 `no`와 다를 수 있습니다.

관찰된 카테고리 종목 목록 `orderType` 값에는 `quantTop`, `priceTop`, `up`, `down`, `marketSum`, `sales`, `operatingProfit`이 포함됩니다. UI chip alias는 `accQuant -> quantTop`, `accAmount -> priceTop`으로 매핑됩니다.

2026-04-27 직접 확인에서 열렸던 국내 주식 메뉴 route: `/market/stock/kr/stocklist/*`, `/market/stock/kr/etf/*`, `/market/stock/kr/etn/*`, `/market/stock/kr/ipo`, `/market/stock/kr/deposit`, `/market/stock/kr/trend/{foreigner|organization|program|trader}`, 종목 상세 하위 페이지 `/domestic/stock/{itemCode}/{price|news|notice|ir|discussion|research}`, 종목 정보 탭 `/domestic/stock/{itemCode}/info/*`. `/domestic/stock/{itemCode}/financial`, `/total`, `/chart`, `/analysis`, `/investment`는 직접 확인에서 404를 반환했습니다.

국내 ETF `listingType` alias는 UI chunk에서 `tradingValueDesc`, `aumDesc`, `changeRateDescUpAll`, `changeRateDescDownAll`, `tradingVolumeDesc`, `tradingVolumeIncreaseRateDesc`, `tradingVolumeIncreaseRateAsc`, `returnRate1mDesc`, `returnRate3mDesc`, `returnRate6mDesc`, `marketCapDesc`, `listedAtDesc`가 관찰되었습니다.

국내 ETN `orderType` 값은 UI chunk에서 `MARKET_SUM_ETN`, `AMOUNT_ETN`, `UP_ETN`, `DOWN_ETN`, `QUANT_ETN`, `QUANT_HIGH_ETN`, `QUANT_LOW_ETN`, `NEW_STOCK_ETN`이 관찰되었습니다.

`/market/stock/global`, `/market/stock/usa/stocklist`, `/market/stock/global/{chn|hkg|jpn|vnm}` 하위 국가 페이지 같은 해외 주식 route도 접근 가능하며 `/api/foreign/*`, `/api/securityService/stock/*`, `/api/securityService/etf/*`, worldstock polling 계열을 노출합니다. 주식 관련이지만 국내 스크립트와 코드 체계를 섞지 않기 위해 별도로 둡니다.

## 시장 지수와 지표

| 목적 | 상태 | Method | Path / params |
| --- | --- | ---: | --- |
| 주요 지수 | `script-backed` | GET | `/api/securityFe/api/index/majors` |
| 시장지표 주요 블록 | `observed` | GET | `/api/securityService/marketindex/majors/{type}`. 관찰된 `type`: `exchange`, `exchangeWorld`, `domesticInterest`, `rpc` |
| 지수 기본 정보 | `observed` | GET | `/api/securityFe/api/index/{reutersCode}/basic` |
| 지수 통합 정보 | `observed` | GET | `/api/securityFe/api/index/{reutersCode}/integration` |
| 지수 가격 이력 | `observed` | GET | `/api/securityFe/api/index/{reutersCode}/price?page=1&pageSize=20` |
| 국내 지수 폴링 | `script-backed` | GET | `/api/polling/domestic/index?itemCodes=KOSPI,KOSDAQ,KPI200` |
| 지수 차트 | `script-backed` | GET | `/api/securityService/chart/domestic/index/{code}?periodType=day` |
| 원자재/운임 지표 | `script-backed` | GET | `/api/securityService/marketindex/energy`, `/metals`, `/agricultural`, `/transport` |
| 국내 금리 | `script-backed` | GET | `/api/securityService/marketindex/domesticInterest` |
| 기타 지표 카테고리 | `observed` | GET | `/api/securityService/marketindex/exchange`, `/bond`, `/standardInterest` 및 각 카테고리 상세 path |
| 지표 상세 | `script-backed` | GET | `/api/securityService/marketindex/{energy\|metals\|agricultural\|exchange}/{reutersCode}` |
| 지표 가격 이력 | `script-backed` | GET | `/api/securityService/marketindex/{energy\|metals\|agricultural\|exchange}/{reutersCode}/prices?page=1&pageSize=20` |
| 국가별 채권 | `script-backed` | GET | `/api/securityService/marketindex/bond/nation/{nationType}?sortType={sortType}` |
| 기준금리 상세 | `script-backed` | GET | `/api/securityService/marketindex/standardInterest/{nationType}` |
| 예정 경제지표 | `script-backed` | GET | `/api/securityService/economic/indicator/nations/upcoming?limit=10&nationTypeList=USA` |
| 발표일별 경제지표 | `script-backed` | GET | `/api/securityService/economic/indicator/nations/releaseDate?page=1&pageSize=20&releaseDate={yyyyMMdd}` |
| 환율 helper | `script-backed` | GET | `/api/stockDomestic/exchangeRates/list?currencies=USD,JPY` |
| 시장지표 폴링 | `observed` | GET | `/api/polling/marketindex/{category}/{codes}` |
| 통합 지표 | `observed` | GET | `/api/securityService/integration/indicators?stockType=domestic&indicatorCodes=KOSPI&indicatorCodes=KOSDAQ` |
| 통합 가격 | `observed` | GET | `/api/securityService/integration/price?domesticKrxCodes=005930&foreignCodes=.IXIC&cryptoCodes=BTC_KRW_UPBIT` |

`/api/securityService/marketindex/majors` 같은 오래된 형태의 route는 2026-04-27에 404를 반환했습니다. 주요 지수에는 `/api/securityFe/api/index/majors`를 사용합니다.

## 가상자산 API

| 목적 | 상태 | Method | Path / params |
| --- | --- | ---: | --- |
| 랭킹 목록 | `script-backed` | GET | `/api/coin/rank/{market}?sortType=marketValue&page=1&pageSize=60` |
| 주요 코인 | `script-backed` | GET | `/api/coin/rank/{market}/majors` |
| 거래소별 코인 가격 | `script-backed` | GET | `/api/coin/price/{market}/{ticker}` |
| 거래소 비교용 코인 가격 | `script-backed` | GET | `/api/coin/price/{ticker}?excludeExchange={market}` |
| 폴링 가격 | `script-backed` | GET | `/api/polling/coin/price?fqnfTickers=BTC_KRW_UPBIT` |
| 분봉 캔들 | `script-backed` | GET | `/api/coin/candle/{market}/KRW/{ticker}/minutes/{unit}/marketInfo?from={iso}&to={iso}` |

`UPBIT` 또는 `BITHUMB`을 대문자로 사용합니다. 폴링 엔드포인트는 `BTC_KRW_UPBIT` 같은 `fqnfTicker` 값을 받습니다. 직접 확인에서 일반 `KRW-BTC`는 빈 list를 반환했습니다.

## 뉴스 API

| 목적 | 상태 | Method | Path / params |
| --- | --- | ---: | --- |
| 뉴스 목록 | `script-backed` | GET | `/api/domestic/news/list?category=mainnews&page=1&pageSize=20` |
| 포커스 뉴스 | `script-backed` | GET | `/api/domestic/news/focus?sid=401&page=1&pageSize=20` |
| 뉴스 검색 | `script-backed` | GET | `/api/domestic/news/search?query=반도체&page=1&pageSize=20` |
| 시장 공시/공지 뉴스 | `script-backed` | GET | `/api/domestic/news/noticeList?page=1&pageSize=20&keyword={keyword}&typeIdx={idx}` |
| 세계/해외 시장 뉴스 | `script-backed` | GET | `/api/foreign/news/worldNews?page=1&pageSize=20&date={yyyyMMdd}` |
| 뉴스 홈 집계 | `script-backed` | GET | `/api/domestic/news/aggregate/home?flashNewsSize=5&mainNewsSize=5&rankingNewsSize=5&overseasNewsSize=5&focusSize=5&moneyStorySize=5&noticeSize=5` |

관찰된 목록 카테고리에는 `mainnews`, `flashnews`, `ranknews`가 있습니다. `stock`, `market`, `all` 같은 임의 값은 실패할 수 있습니다. 관찰된 포커스 섹션 맵: `market-outlook=401`, `company-analysis=402`, `global-market=403`, `bond-futures=404`, `disclosure-memo=406`, `exchange-rate=429`.

## 리서치 API

| 목적 | 상태 | Method | Path / params |
| --- | --- | ---: | --- |
| 리서치 카테고리 목록 | `script-backed` | GET | `/api/domestic/research/category?category=COMPANY&page=1&pageSize=15` |
| 카테고리 상세 | `script-backed` | GET | `/api/domestic/research/category/{researchId}?category=COMPANY` |
| 종목 리포트 목록 | `observed` | GET | `/api/domestic/research/{itemCode}/research?page=0&size=30` |
| 종목 리포트 상세 | `observed` | GET | `/api/domestic/research/{itemCode}/research/{researchId}` |
| 최근 인기 | `script-backed` | GET | `/api/domestic/research/recent-popular` |
| 리서치 홈 집계 | `script-backed` | POST | `/api/domestic/home/researchaggregate/static`, `researchCategory`, `researchRanking`, `recentPopular` 같은 boolean `sections` 포함 |
| 카테고리 최신 | `observed` | GET | `/api/domestic/research/category-lastest` |
| 산업 리서치 | `observed` | GET | `/api/domestic/research/industry-research` |
| 랭킹 | `observed` | GET | `/api/domestic/research/ranking?rankingType={type}&selectedRank={rank}` |
| 증권사 목록 | `script-backed` | GET | `/api/domestic/research/broker-list` |

검증 오류와 chunk에서 관찰된 카테고리 enum: `INVEST`, `MARKET`, `INDUSTRY`, `COMPANY`, `ECONOMY`, `DEBENTURE`.

## 종목토론 API

| 목적 | 상태 | Method | Path / params |
| --- | --- | ---: | --- |
| 인기 feed | `observed` | GET | `/api/community/discussion/posts/hot?pageSize=20&page=1&discussionType={type}&itemCode={itemCode}` |
| 홈 인기 feed | `observed` | GET | `/api/community/discussion/posts/hot/home?pageSize=20&page=1` |
| 글 상세 | `script-backed` | GET | `/api/community/discussion/posts/{postId}` |
| 이전/다음 글 이동 | `script-backed` | GET | `/api/community/discussion/posts/{postId}/adjacent?pageSize=20&itemCode={itemCode}` |
| 관련 인기 글 | `script-backed` | GET | `/api/community/discussion/posts/related/hot?itemCode={itemCode}&pageSize=20&discussionType=domesticStock` |
| 인기 글 | `script-backed` | GET | `/api/community/discussion/posts/popular/hot` |
| 시장 feed | `observed` | GET | `/api/community/discussion/posts/market?offset={offset}&pageSize=20` |
| 종목 글 | `observed` | GET | `/api/community/discussion/posts?itemCode={itemCode}&pageSize=20` |
| 종목별 글 | `observed` | GET | `/api/community/discussion/posts/by-item?itemCode={itemCode}&pageSize=20` |
| 여러 종목 글 | `observed` | GET | `/api/community/discussion/posts/by-item-codes?filterType=itemCodes&pageSize=20&offset={offset}&domesticCodes={codes}` |
| 최신 종목 글 | `observed` | GET | `/api/community/discussion/items/posts/latest?domesticCodes={codes}&limit=10` |
| 댓글 수 | `observed` | GET | `/api/community/discussion/posts/comment-counts?postIds={ids}` |
| 반응 조회 | `observed` | GET | `/api/community/discussion/posts/reactions?postIds={ids}` |
| 랭킹 | `script-backed` | GET | `/api/community/discussion/rankings?nationType=KOR&page=1&size=20&postType=HOT` |
| 종목 통계 | `observed` | GET | `/api/community/discussion/stats/by-items?itemCodes={codes}` |

작성, 프로필 편집, 이미지 업로드, 닉네임 검증/추천, 반응 mutation, 인증된 커뮤니티 프로필 워크플로는 피합니다.

## 제외 계열

| 계열 | 상태 | 이유 |
| --- | --- | --- |
| `/api/auth/*` | `excluded` | 로그인/인증. |
| `/api/personal/users/holding/*` | `excluded` | 계좌 보유종목과 refresh 워크플로. |
| `/api/personal/users/favorite/*` | `excluded` | 사용자별 관심종목과 그룹. |
| `/api/personal/users/notification*` | `excluded` | 사용자 알림 설정/메시지. |
| `/api/community/profile/users/*` mutation-like routes | `excluded` | 사용자 프로필과 이미지 워크플로. |
| `https://finance.naver.com/*` | `excluded` | 이 스킬 범위인 `stock.naver.com` 밖의 구버전 HTML 페이지입니다. 해당 범위는 [dd3ok/naverfinance-api-skills](https://github.com/dd3ok/naverfinance-api-skills)를 참고해 주세요. |
| 텔레메트리, 광고, 정적 chunk, 폰트, 이미지 | `excluded` | 주식 정보 API가 아닙니다. |
