# 국내 주식 API

상태 라벨, page route, 전송, 식별자와 제외 기준은 [공통 API 인덱스](api-catalog.md)를 따릅니다.

## 목차

- [엔드포인트](#엔드포인트)
- [검증 메모](#검증-메모)

## 엔드포인트

| 목적 | 상태 | Method | Path / params |
| --- | --- | ---: | --- |
| 종목 상세 | `script-backed` | GET | `/api/domestic/detail/{itemCode}/detail?codeType=KRX` 또는 `NXT` |
| 종목 가격 탭 | `script-backed` | GET | `/api/domestic/detail/{itemCode}/price` |
| 종목 호가 | `script-backed` | GET | `/api/domestic/detail/{itemCode}/hoga` |
| 종목 일별 시세 | `script-backed` | GET | `/api/domestic/detail/{itemCode}/siseDay?pageSize=20&bizdate={yyyyMMdd}` |
| 종목 체결 | `script-backed` | GET | `/api/domestic/detail/{itemCode}/siseTick?startIdx=0&pageSize=20` |
| 종목 투자자 동향 행 | `script-backed` | GET | `/api/domestic/detail/{itemCode}/trend?tradeType=KRX&startIdx=0&pageSize=20` |
| 종목 증권사 거래 정보 | `script-backed` | GET | `/api/domestic/detail/{itemCode}/traderInfo` |
| 종목 차트 메타 payload | `script-backed` | GET | `/api/securityFe/api/fchart/domestic/stock/{itemCode}?periodType={day\|week\|month\|year}`. `range=1m`은 2026-07-09 재점검에서 유효하지 않았습니다. |
| 종목 차트 가격 행 | `script-backed` | GET | `/api/securityService/chart/domestic/item/{itemCode}?periodType={day\|week\|month\|year}`. 기본 호출은 `range`를 생략합니다. |
| 시장 구분 | `script-backed` | GET | `/api/domestic/detail/{itemCode}/sosok` |
| 컨센서스 | `script-backed` | GET | `/api/domestic/detail/{itemCode}/consensus` |
| 업종 관련 종목 | `script-backed` | GET | `/api/domestic/detail/{itemCode}/stock/industry?page=1&pageSize=10&marketType=ALL` |
| 종목 뉴스 | `script-backed` | GET | `/api/domestic/detail/news?itemCode={itemCode}&page=1&pageSize=15` |
| 종목 공시 | `script-backed` | GET | `/api/domestic/detail/notice?itemCode={itemCode}&startIdx=0&pageSize=30&causeCode={code}` |
| 종목 IR 목록 | `script-backed` | GET | `/api/domestic/detail/ir?itemCode={itemCode}&startIdx=0&pageSize=60` |
| 종목 IR 상세 | `script-backed` | GET | `/api/domestic/detail/ir/{itemCode}/{articleId}`. 현재 ID는 숫자 외 `BOARD75384`, `PLAN8570` 형태도 사용 |
| 집계 투자자 poll 통계 | `script-backed` | GET | `/api/stockDomestic/invest-info/poll/statistics/{itemCode}` |
| 집계 투자자 분포 리소스 | `script-backed` | GET | `/api/myasset/resources/invest/{stock-trade\|stock-investor-rank\|stock-invest-rate\|stock-investor-age\|stock-floor}?item_code={itemCode}` |
| 재무 메뉴 메타데이터 | `script-backed` | GET | `/api/stockSecurity/finances/v1/domestic/{itemCode}/menu-info` |
| ESG 정보 | `script-backed` | GET | `/api/stockSecurity/finances/v1/domestic/{itemCode}/esg` |
| 종목 정보 탭 page route | `observed` | PAGE | `/domestic/stock/{itemCode}/info/{company\|overview\|financial\|investment\|consensus\|industry\|sector\|share\|esg}`. 2026-04-27 직접 확인에서 200을 반환했습니다. 하위 JSON API는 아직 script-backed가 아니므로 필요 시 현재 트래픽으로 재확인합니다. |
| 실시간 폴링 현재가 | `script-backed` | GET | `/api/polling/domestic/stock?itemCodes={codes}` |
| NXT 폴링 현재가 | `script-backed` | GET | `/api/polling/domestic/NXT/stock?itemCodes={codes}` |
| 국내 시장 기본 종목 목록 | `script-backed` | GET | `/api/domestic/market/stock/default?tradeType=KRX&marketType=ALL&orderType=marketSum&startIdx=0&pageSize=20` |
| 국내 시장 의미 기반 랭킹 | `script-backed` | GET | 같은 `default` endpoint를 `market_stock.py ranking {kind}`로 호출합니다. 현재 UI chip과 검증된 enum만 노출합니다. |
| 배당 목록 | `script-backed` | GET | `/api/domestic/market/stock/dividend?tradeType=KRX&marketType=ALL&dividend={dividendRate\|dividend}&startIdx=0&pageSize=20`. 현재 UI는 수익률순/배당금순을 각각 매핑 |
| 검색 인기 | `script-backed` | GET | `/api/domestic/market/searchTop?nationType=KOR&startIdx=0&pageSize=20` |
| 상장 진행 중 | `script-backed` | GET | `/api/domestic/market/ipo/progress?startIdx=0&pageSize=101` |
| 상장 완료 | `script-backed` | GET | `/api/domestic/market/ipo/progress?IpoProgressType=LISTING&startIdx=0&pageSize=100` |
| 업종/테마 랭킹 | `script-backed` | GET | `/api/domestic/home/upjongTheme/ranking?sortType=changeRate` |
| 업종/테마/그룹사 랭킹 목록 | `script-backed` | GET | `/api/domestic/market/{upjong\|theme\|group}/list?startIdx=0&pageSize=100&sortType=changeRate` |
| 국내 업종·테마·그룹 v2 랭킹 | `script-backed` | GET | `/api/stockSecurity/rankings/v2/domestic/{industries\|themes\|groups}?sortType={changeRate\|marketCap}&size=100&excludeCodes=25&period={daily\|weekly\|monthly}&cursor={cursor}`. `cursor`는 opaque 서버 값 |
| 국내 업종·테마 전체 시가총액 | `script-backed` | GET | `/api/stockSecurity/rankings/v2/domestic/{industries\|themes}/total-market-cap` |
| 업종/테마/그룹사 상세 정보 | `script-backed` | GET | `/api/domestic/market/{upjong\|theme\|group}/{no}/info?marketType=ALL` |
| 업종/테마/그룹사 구성 종목 | `script-backed` | GET | `/api/domestic/market/{upjong\|theme\|group}/{no}/stocklist?marketType=ALL&orderType=quantTop&startIdx=0&pageSize=20` |
| 시장 집계 투자자 동향 | `script-backed` | POST | `/api/domestic/home/marketaggregate/aggregateInvestor`, JSON body는 `sections`, `tradeType`, `marketType`, `periodType`, 날짜를 포함합니다. 출력 이상 또는 4xx가 있으면 현재 페이지에서 재확인합니다. |
| 시장 집계 투자자 랭킹 | `observed` | POST | `/api/domestic/home/marketaggregate/aggregateInvestorRanking`. 2026-08-04 현재 페이지가 `Content-Type: application/json`, `credentials: include`로 호출하며 body는 `sections.{investorTrend,programTrend,foreignTop,orgTop}`에 `tradeType`, `marketType`, `periodType`, 날짜, `rankingType`, `side`, `startIdx=0`, `pageSize=10`을 구성합니다. 개인 식별 필드는 없지만 스크립트로는 아직 노출하지 않습니다. |
| 투자자 예탁금 목록 | `script-backed` | GET | `/api/domestic/market/trendDeposit?startIdx=0&pageSize=20` |
| 투자자 예탁금 차트 | `script-backed` | GET | `/api/domestic/market/trendDeposit/chart?startDate={yyyyMMdd}&endDate={yyyyMMdd}` |
| 외국인/기관 투자자 동향 랭킹 | `script-backed` | GET | `/api/domestic/market/trend/trendForeignOrg?investorType=FOREIGNER&tradeType=KRX&marketType=ALL&startIdx=0&pageSize=20&periodType=DAY` |
| 투자자 동향 일별 행 | `script-backed` | GET | `/api/domestic/market/trend/daily?tradeType=KRX&marketType=ALL&bizdate={yyyyMMdd}&startIdx=0&pageSize=20` |
| 투자자 동향 시간 차트 | `script-backed` | GET | `/api/domestic/market/trend/chart/time?tradeType=KRX&marketType=ALL&selectedRange=1일&bizdate={yyyyMMdd}&startDate={yyyyMMdd}&endDate={yyyyMMdd}` |
| 프로그램 매매 동향 행 | `script-backed` | GET | `/api/domestic/market/trendProgram?tradeType=KRX&krxMarketType=ALL&bizdate={yyyyMMdd}&startIdx=0&pageSize=20&periodType=TIME` |
| 프로그램 매매 동향 차트 | `script-backed` | GET | `/api/domestic/market/trendProgram/chart?tradeType=KRX&krxMarketType=ALL&bizdate={yyyyMMdd}&startDate={yyyyMMdd}&endDate={yyyyMMdd}&periodType=TIME` |
| 업종 전체 시가총액 | `observed` | GET | `/api/domestic/market/home/upjong/totalMarketSum?type=upjong` |
| ETF 테마 | `observed` | GET | `/api/domestic/market/etf/themes` |
| 국내 ETF 목록 | `script-backed` | GET | `/api/stockSecurity/etfs/v2/domestic?listingType=tradingValueDesc&size=20&index=0`. CLI 저용량 기본은 20, 현재 전체 목록 UI는 `size=100` |
| 홈 국내 ETF v3 목록 | `observed` | GET | `/api/stockSecurity/etfs/v3/domestic`에 `listingType`, `size`, `index`와 선택적 카테고리·배율 필터. 홈 랭킹은 `size=10`, 테마 카드는 `size=3`, `index=0`. 전체 목록 v2를 대체하지 않음 |
| 국내 인기 ETF | `observed` | GET | `/api/stockSecurity/rankings/v2/domestic/popular-etf?size=10&cursor={cursor}` 및 홈 `/api/stockSecurity/aggregate/domesticPopularEtf?size=10`. 인기 화면과 해당 요청 함수는 관찰했지만 cursor 응답·종료 계약은 미검증 |
| 국내 종목 가격 보강 | `observed` | GET | `/api/stockSecurity/items/v2/domestic/prices?itemCodes={code}&itemCodes={code}&recurring={true\|false}`. 홈 인기 ETF는 `recurring=true`, 함수 기본은 false |
| 홈 국내 종목 집계 | `observed` | GET | `/api/stockSecurity/aggregate/domesticStock`의 공통 query는 `type={listing\|popular}`, `exchangeType`, `size`. listing은 `index`, `listingType`, `marketType`; popular는 `cursor`, `ageGroup`. 호출자 정적 관찰이며 직접 응답 미검증 |
| 국내 ETF 카테고리 메타데이터 | `script-backed` | GET | `/api/stockSecurity/etfs/v2/domestic/themes` |
| 국내 ETF 레버리지 메타데이터 | `script-backed` | GET | `/api/stockSecurity/etfs/v1/domestic/leverage-types` |
| ETF 기본 정보 | `script-backed` | GET | `/api/domestic/detail/{itemCode}/ETFBase` |
| ETF 배당 요약 | `script-backed` | GET | `/api/domestic/detail/{itemCode}/ETFDividend` |
| ETF 배당 이력 | `script-backed` | GET | `/api/domestic/detail/{itemCode}/ETFDividendHist?startIdx=0&pageSize=20` |
| ETF 구성 종목 | `script-backed` | GET | `/api/domestic/detail/{itemCode}/ETFComponent?startIdx=0&pageSize=20` |
| ETF 테마 태그 | `script-backed` | GET | `/api/domestic/detail/{itemCode}/ETFTheme` |
| ETF 자금 흐름 일/주 | `script-backed` | GET | `/api/domestic/detail/{itemCode}/ETFSumFlowDayList?count=20`, `/ETFSumFlowWeekList?count=20` |
| 국내 ETN 목록 | `script-backed` | GET | `/api/domestic/market/etn?orderType=AMOUNT_ETN&startIdx=0&pageSize=20` |
| 종목 인사이트 보유자 랭킹·가상 투자 | `script-backed` | GET | `/api/securityService/home/v3/mystock/ranking/{itemCode}`, `/api/securityService/home/v3/whatIf/{domestic\|worldstock}/{code}?periodType=year&range=5` |

## 검증 메모

2026-09-07 공개 검색에서 `0193W0`, `0162Z0`, `0177N0`처럼 영문을 포함한 국내 ETF 코드와 실제 종목 상세 링크를 확인했습니다. [0193W0 가격 화면](https://stock.naver.com/domestic/stock/0193W0/price)에 대응하는 가격 응답은 같은 `itemcode`, 상품명과 `type=EF`를 반환했습니다. 공통 `normalize_item_code`와 이를 사용하는 국내 스크립트는 ASCII 영숫자 6자리를 대문자로 정규화하며, 숫자 6자리와 기존 `A005930` 호환을 유지합니다. Unicode 대문자 변환으로 ASCII 코드가 만들어지는 입력과 경로 구분자는 거절합니다. 종목·리서치·토론·홈·인사이트 명령도 이 형식 확장의 영향을 받습니다. 코드 유효성과 개별 상품의 데이터 지원은 별개이며, 이번 실응답 검증은 가격에 한정됩니다. endpoint allowlist는 변경하지 않았고 WiseReport의 숫자 코드 제한은 별도로 유지합니다.

2026-07-21 현재 종목 목록 UI에서 확인하고 live 요청으로 검증한 의미 매핑은 `market-cap -> marketSum`, `rise -> up`, `flat -> flat`, `fall -> down`, `volume -> quantTop`, `volume-surge -> upperQuantTop`, `volume-drop -> lowerQuantTop`, `trading-value -> priceTop`, `new-stock -> newStock`, `foreign-hold -> frgnRate`, `52-week-high -> high52week`, `52-week-low -> low52week`, `management -> statusTag`, `trading-halt -> tradeStopYn`입니다.

투자주의·경고·위험은 독립 `orderType`이 아닙니다. 반드시 `orderType=marketAlertType`과 `alertType=01`, `02`, `03`을 조합합니다. 문자열 `investmentWarning` 등을 `orderType`이나 `alertType`에 넣으면 400 또는 필터 무시가 발생할 수 있습니다. `market_stock.py ranking`은 이 조합을 대신 구성하고, 저수준 `default` 명령도 모호한 조합을 거절합니다.

KONEX 화면은 `marketType=KONEX&orderType=quantTop&tradeType=KRX` 조합만 사용합니다. 서버가 KONEX와 다른 `orderType` 조합을 오류 없이 받아도 KOSPI 목록을 반환하는 사례가 있으므로 지원으로 간주하지 않습니다.

NXT 화면은 `marketSum`, `up`, `down`, `quantTop`, `searchTop`만 사용합니다. `market_stock.py`는 NXT와 그 밖의 랭킹 조합을 거절해 필터가 무시된 KRX 결과를 NXT 데이터로 오인하지 않게 합니다.

`stock.naver.com/market/stock/kr/{industry|theme|groups}/{rank}` 페이지의 path 값은 현재 카테고리 `no`가 아니라 화면의 랭킹 순번입니다. 먼저 list API에서 현재 카테고리 `no`를 찾은 뒤 `info`와 `stocklist`를 호출합니다. API path는 `industry`에 `upjong`, `theme`에 `theme`, `groups`에 `group`을 사용합니다. `/industry/1`의 `1`은 페이지 rank이며 실제 카테고리 `no`와 다를 수 있습니다.

관찰된 카테고리 종목 목록 `orderType` 값에는 `quantTop`, `priceTop`, `up`, `down`, `marketSum`, `sales`, `operatingProfit`이 포함됩니다. UI chip alias는 `accQuant -> quantTop`, `accAmount -> priceTop`으로 매핑됩니다.

2026-08-04 국내 홈/토론 화면의 기본 종목 목록에서는 `foreignPureBuy`, `organizationPureBuy`도 관찰됐습니다. 각각 외국인·기관 순매수 UI에 대응하지만 목록 helper의 안정 enum으로 승격하기 전에는 현재 화면 요청을 다시 확인합니다. `/market/stock/kr/trend/trader`와 `/market/stock/kr/deposit`의 숫자 페이지 2를 직접 눌렀을 때 API는 각각 `startIdx=1&pageSize=30`, `startIdx=1&pageSize=20`을 보냈습니다. 이 두 endpoint에서 `startIdx`는 행 offset이 아니라 0부터 시작하는 페이지 index입니다.

2026-07-21 브라우저 직접 확인에서 국내 주식·ETF·ETN의 모든 목록 탭, 종목 상세 하위 탭, 9개 종목분석 탭, ESG, KRX 공매도 iframe이 데이터 또는 정상 외부 화면을 렌더링했습니다. `/domestic/stock/{itemCode}/info`는 `company`로 이동합니다. `/domestic/stock/{itemCode}/financial`, `/total`, `/chart`, `/analysis`, `/investment`는 직접 확인에서 404를 반환했습니다.

국내 ETF `listingType` alias는 UI chunk에서 `tradingValueDesc`, `aumDesc`, `changeRateDescUpAll`, `changeRateDescDownAll`, `tradingVolumeDesc`, `tradingVolumeIncreaseRateDesc`, `tradingVolumeIncreaseRateAsc`, `returnRate1mDesc`, `returnRate3mDesc`, `returnRate6mDesc`, `marketCapDesc`, `listedAtDesc`가 관찰되었습니다.

2026-07-20 확인에서 ETF 목록과 테마의 v1 route는 404였고 v2 route가 200을 반환했습니다. 레버리지 메타데이터는 현재 chunk가 계속 `/api/stockSecurity/etfs/v1/domestic/leverage-types`를 사용하므로 이 한 경로만 v1을 유지합니다.

2026-09-07 [홈 chunk](https://ssl.pstatic.net/imgstock/fn/real/pc/_next/static/chunks/app/page-ae5fb7f70db05b3d.js)에서 홈 ETF 랭킹·테마 카드의 v3와 전체 목록의 v2가 공존함을 확인했습니다. v3 항목은 `krx`·`nxt` 가격 분기를 가지므로 기존 v2 출력과 동일하다고 가정하지 않습니다. 전체 목록 hook은 여전히 v2, `size=100`, `index=0`으로 시작해 `hasNext`일 때 index를 1 증가시킵니다.

[현재 ETF 화면](https://stock.naver.com/market/stock/kr/etf/priceTop)은 기존 11개 정렬에 `/top` 인기 종목이 추가된 12개 링크를 노출합니다. [ETF page chunk](https://ssl.pstatic.net/imgstock/fn/real/pc/_next/static/chunks/app/market/stock/kr/etf/%5Bchip%5D/page-ffb06b08cd432c13.js)의 인기 요청은 일반 ETF `listingType`과 별개입니다. `domestic_etf.py list --listing-type top`을 인기 조회로 안내하지 않습니다. 인기 탭의 대분류·중분류·배율 필터는 비활성화되며, 일반 탭에서는 주식→대형주→일반 선택을 확인했습니다. 개장 전에는 안내만 표시됐지만 같은 날 개장 후 재방문에서 priceTop 100행, 인기 100행과 `목록의 마지막입니다`를 확인했습니다. 12개 경로에 진입했으나 나머지 탭의 비동기 로딩 완료·모든 필터 조합까지 검증한 것은 아닙니다. UI 필터 라벨을 API 코드값으로 추정하지 않습니다.

개장 후 v2 일반 목록에 `listingType=tradingValueDesc&size=2`를 고정해 `index=0`과 `1`을 직접 조회했습니다. 각각 2개 항목과 `hasNext: true`, 서로 다른 코드 묶음(`122630,069500` → `233740,459580`)을 확인했습니다. `totalCount`, `size`, `index`와 가격·수익률 필드는 문자열이므로 숫자로 단정하지 않습니다. 이 결과를 인기 ETF의 cursor 계약이나 v3 응답 검증으로 확대하지 않습니다.

국내 ETN `orderType` 값은 UI chunk에서 `MARKET_SUM_ETN`, `AMOUNT_ETN`, `UP_ETN`, `DOWN_ETN`, `QUANT_ETN`, `QUANT_HIGH_ETN`, `QUANT_LOW_ETN`, `NEW_STOCK_ETN`이 관찰되었습니다.
