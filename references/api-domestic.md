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
| 외국인/기관 투자자 동향 랭킹 | `script-backed` | GET | `/api/domestic/market/trend/trendForeignOrg?investorType={FOREIGNER\|ORGANIZATION}&tradeType=KRX&marketType=ALL&startIdx=0&pageSize=20&periodType={DAY\|WEEK\|MONTH\|THREE_MONTH}`. 현재 기관 화면은 `startIdx=0`을 유지하고 `pageSize`를 늘림 |
| 투자자 동향 일별 행 | `script-backed` | GET | `/api/domestic/market/trend/daily?tradeType=KRX&marketType=ALL&bizdate={yyyyMMdd}&startIdx=0&pageSize=20` |
| 투자자 동향 시간 차트 | `script-backed` | GET | `/api/domestic/market/trend/chart/time?tradeType=KRX&marketType=ALL&selectedRange=1일&bizdate={yyyyMMdd}&startDate={yyyyMMdd}&endDate={yyyyMMdd}` |
| 프로그램 매매 동향 행 | `script-backed` | GET | `/api/domestic/market/trendProgram?tradeType=KRX&krxMarketType=ALL&bizdate={yyyyMMdd}&startIdx=0&pageSize=20&periodType=TIME` |
| 프로그램 매매 동향 차트 | `script-backed` | GET | `/api/domestic/market/trendProgram/chart?tradeType=KRX&krxMarketType=ALL&bizdate={yyyyMMdd}&startDate={yyyyMMdd}&endDate={yyyyMMdd}&periodType=TIME` |
| 업종 전체 시가총액 | `observed` | GET | `/api/domestic/market/home/upjong/totalMarketSum?type=upjong` |
| ETF 테마 | `observed` | GET | `/api/domestic/market/etf/themes` |
| 국내 ETF 목록 | `script-backed` | GET | `/api/stockSecurity/etfs/v2/domestic?listingType=tradingValueDesc&size=20&index=0`. CLI 저용량 기본은 20, 현재 전체 목록 UI는 `size=100` |
| 홈 국내 ETF v3 목록 | `observed` | GET | `/api/stockSecurity/etfs/v3/domestic?listingType=tradingValueDesc&size=2&index=0` 직접 응답 200 확인. 선택적 카테고리·배율 필터가 있으며 홈 UI는 크기 10 또는 3을 사용. 전체 목록 v2를 대체하지 않음 |
| 국내 인기 ETF | `observed` | GET | `/api/stockSecurity/rankings/v2/domestic/popular-etf?size=10&cursor={cursor}` 및 홈 `/api/stockSecurity/aggregate/domesticPopularEtf?size=10`. 첫 요청은 cursor 생략. 2026-09-07 크기 2의 첫·다음 cursor 응답 200 확인; 전체 끝까지의 순회는 수행하지 않음 |
| 국내 종목 가격 보강 | `observed` | GET | `/api/stockSecurity/items/v2/domestic/prices?itemCodes={code}&itemCodes={code}&recurring={true\|false}`. 홈 인기 ETF는 `recurring=true`, 함수 기본은 false |
| 홈 국내 종목 집계 | `observed` | GET | `/api/stockSecurity/aggregate/domesticStock`의 공통 query는 `type={listing\|popular}`, `exchangeType={KRX\|NXT}`, `size`. listing은 `index`, `listingType`와 선택적 `marketType`; popular는 선택적 `cursor`, `ageGroup`. 현재 홈 기본 호출은 `marketType`·`ageGroup`·첫 cursor를 생략하며 두 type 모두 크기 2의 응답 200 확인 |
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

2026-09-07 공개 검색에서 `0193W0`, `0162Z0`, `0177N0`처럼 영문을 포함한 국내 ETF 코드와 실제 종목 상세 링크를 확인했습니다. [0193W0 가격 화면](https://stock.naver.com/domestic/stock/0193W0/price)에 대응하는 가격 응답은 같은 `itemcode`, 상품명과 `type=EF`를 반환했습니다. 공통 `normalize_item_code`와 이를 사용하는 국내 스크립트는 ASCII 영숫자 6자리를 대문자로 정규화하며, 숫자 6자리와 기존 `A005930` 호환을 유지합니다. Unicode 대문자 변환으로 ASCII 코드가 만들어지는 입력과 경로 구분자는 거절합니다. 종목·리서치·토론·홈·인사이트 명령도 이 형식 확장의 영향을 받습니다. 같은 날 후속 무인증 요청으로 `0193W0`의 상세·KRX 폴링과 ETF 상세 7개 경로도 모두 200을 확인했습니다. 배당 이력은 빈 목록이었고, 구성 종목의 일부 연결 코드와 긴 기간 성과는 null이었습니다. 코드 유효성과 상품별 데이터 보유 여부는 별개입니다. endpoint allowlist는 변경하지 않았고 WiseReport의 숫자 코드 제한은 별도로 유지합니다.

2026-07-21 현재 종목 목록 UI에서 확인하고 live 요청으로 검증한 의미 매핑은 `market-cap -> marketSum`, `rise -> up`, `flat -> flat`, `fall -> down`, `volume -> quantTop`, `volume-surge -> upperQuantTop`, `volume-drop -> lowerQuantTop`, `trading-value -> priceTop`, `new-stock -> newStock`, `foreign-hold -> frgnRate`, `52-week-high -> high52week`, `52-week-low -> low52week`, `management -> statusTag`, `trading-halt -> tradeStopYn`입니다.

투자주의·경고·위험은 독립 `orderType`이 아닙니다. 반드시 `orderType=marketAlertType`과 `alertType=01`, `02`, `03`을 조합합니다. 문자열 `investmentWarning` 등을 `orderType`이나 `alertType`에 넣으면 400 또는 필터 무시가 발생할 수 있습니다. `market_stock.py ranking`은 이 조합을 대신 구성하고, 저수준 `default` 명령도 모호한 조합을 거절합니다.

2026-09-07 `default`의 과거 입력 `accAmount`, `steady`를 서버에 그대로 보내면 각각 400이었고, 현재 값 `priceTop`, `flat`은 200이었습니다. CLI는 기존 입력을 유지하면서 `accAmount -> priceTop`, `steady -> flat`으로 변환합니다. 수정한 두 CLI 호출의 실응답도 200을 확인했으며 NXT·KONEX 조합 제한은 유지합니다.

KONEX 화면은 `marketType=KONEX&orderType=quantTop&tradeType=KRX` 조합만 사용합니다. 서버가 KONEX와 다른 `orderType` 조합을 오류 없이 받아도 KOSPI 목록을 반환하는 사례가 있으므로 지원으로 간주하지 않습니다.

NXT 화면은 `marketSum`, `up`, `down`, `quantTop`, `searchTop`만 사용합니다. `market_stock.py`는 NXT와 그 밖의 랭킹 조합을 거절해 필터가 무시된 KRX 결과를 NXT 데이터로 오인하지 않게 합니다.

`stock.naver.com/market/stock/kr/{industry|theme|groups}/{rank}` 페이지의 path 값은 현재 카테고리 `no`가 아니라 화면의 랭킹 순번입니다. 먼저 list API에서 현재 카테고리 `no`를 찾은 뒤 `info`와 `stocklist`를 호출합니다. API path는 `industry`에 `upjong`, `theme`에 `theme`, `groups`에 `group`을 사용합니다. `/industry/1`의 `1`은 페이지 rank이며 실제 카테고리 `no`와 다를 수 있습니다.

2026-09-07 현재 업종 화면의 정렬 chip은 `marketSum`, `accAmount`, `up`, `down`, `accQuant` 5개이며 `accQuant -> quantTop`, `accAmount -> priceTop`으로 매핑됩니다. [현재 공통 요청 함수](https://ssl.pstatic.net/imgstock/fn/real/pc/_next/static/chunks/21546-69c5522fc70c96ac.js)는 `sales`, `operatingProfit`도 그대로 매핑하지만 추가 필수 query나 대체 enum은 없습니다. 현재 list에서 얻은 업종·테마·그룹사 `no`로 `marketType=ALL&startIdx=0&pageSize=2`를 사용했을 때 이 두 정렬은 세 유형 모두 500으로 실패했고, 나머지 5개 정렬은 200이었습니다. 금융 항목은 표의 열에도 나타나지만 현재 정렬 chip에는 없으므로 정상 지원 정렬로 권하지 않습니다. `category_detail.py`의 호환 입력은 유지하며 오류를 빈 목록이나 다른 정렬 결과로 바꾸지 않습니다.

카테고리 구성 종목의 현재 hook은 `startIdx=0`으로 시작하고 다음 묶음에 1, 2처럼 페이지 수를 전달합니다. v2 업종·테마·그룹 랭킹은 `hasNext`, `items`, `cursor`를 반환하며 세 유형 모두 크기 2의 첫 응답과 실제 반환 cursor를 사용한 다음 응답이 200이었습니다. cursor를 디코딩·계산하지 않고 같은 정렬·기간·크기를 유지합니다.

2026-08-04 국내 홈/토론 화면의 기본 종목 목록에서는 `foreignPureBuy`, `organizationPureBuy`도 관찰됐습니다. 각각 외국인·기관 순매수 UI에 대응하지만 목록 helper의 안정 enum으로 승격하기 전에는 현재 화면 요청을 다시 확인합니다. `/market/stock/kr/trend/trader`와 `/market/stock/kr/deposit`의 숫자 페이지 2를 직접 눌렀을 때 API는 각각 `startIdx=1&pageSize=30`, `startIdx=1&pageSize=20`을 보냈습니다. 이 두 endpoint에서 `startIdx`는 행 offset이 아니라 0부터 시작하는 페이지 index입니다.

2026-07-21 브라우저 직접 확인에서 국내 주식·ETF·ETN의 모든 목록 탭, 종목 상세 하위 탭, 9개 종목분석 탭, ESG, KRX 공매도 iframe이 데이터 또는 정상 외부 화면을 렌더링했습니다. `/domestic/stock/{itemCode}/info`는 `company`로 이동합니다. `/domestic/stock/{itemCode}/financial`, `/total`, `/chart`, `/analysis`, `/investment`는 직접 확인에서 404를 반환했습니다.

국내 ETF `listingType` alias는 UI chunk에서 `tradingValueDesc`, `aumDesc`, `changeRateDescUpAll`, `changeRateDescDownAll`, `tradingVolumeDesc`, `tradingVolumeIncreaseRateDesc`, `tradingVolumeIncreaseRateAsc`, `returnRate1mDesc`, `returnRate3mDesc`, `returnRate6mDesc`, `marketCapDesc`, `listedAtDesc`가 관찰되었습니다.

2026-07-20 확인에서 ETF 목록과 테마의 v1 route는 404였고 v2 route가 200을 반환했습니다. 레버리지 메타데이터는 현재 chunk가 계속 `/api/stockSecurity/etfs/v1/domestic/leverage-types`를 사용하므로 이 한 경로만 v1을 유지합니다.

2026-09-07 [홈 chunk](https://ssl.pstatic.net/imgstock/fn/real/pc/_next/static/chunks/app/page-ae5fb7f70db05b3d.js)에서 홈 ETF 랭킹·테마 카드의 v3와 전체 목록의 v2가 공존함을 확인했습니다. v3의 `listingType=tradingValueDesc&size=2&index=0` 실응답은 `hasNext`, `totalCount`, `items`, `size`, `index`를 반환했고 항목 가격은 `krx` 안에 있으며 `nxt`는 null일 수 있었습니다. 가격 필드가 항목 바로 아래 있는 v2와 같은 출력으로 취급하지 않습니다. 전체 목록 hook은 여전히 v2, `size=100`, `index=0`으로 시작해 `hasNext`일 때 index를 1 증가시킵니다.

[현재 ETF 화면](https://stock.naver.com/market/stock/kr/etf/priceTop)은 기존 11개 정렬에 `/top` 인기 종목이 추가된 12개 링크를 노출합니다. [ETF page chunk](https://ssl.pstatic.net/imgstock/fn/real/pc/_next/static/chunks/app/market/stock/kr/etf/%5Bchip%5D/page-ffb06b08cd432c13.js)의 인기 요청은 일반 ETF `listingType`과 별개입니다. `domestic_etf.py list --listing-type top`을 인기 조회로 안내하지 않습니다. 인기 탭의 대분류·중분류·배율 필터는 비활성화되며, 일반 탭에서는 주식→대형주→일반 선택을 확인했습니다. 개장 전에는 안내만 표시됐지만 같은 날 개장 후 재방문에서 priceTop 100행, 인기 100행과 `목록의 마지막입니다`를 확인했습니다. 12개 경로에 진입했으나 나머지 탭의 비동기 로딩 완료·모든 필터 조합까지 검증한 것은 아닙니다. UI 필터 라벨을 API 코드값으로 추정하지 않습니다.

개장 후 v2 일반 목록에 `listingType=tradingValueDesc&size=2`를 고정해 `index=0`과 `1`을 직접 조회했습니다. 각각 2개 항목과 `hasNext: true`, 서로 다른 코드 묶음(`122630,069500` → `233740,459580`)을 확인했습니다. `totalCount`, `size`, `index`와 가격·수익률 필드는 문자열이므로 숫자로 단정하지 않습니다. 후속 요청에서는 스크립트에 선언된 12개 정렬을 각각 크기 2로 조회해 200을 확인했습니다. 현재 메타데이터가 반환한 `largeCategoryCode=0101`, 그 하위 `middleCategoryCode=0101001`, `leverageType=P1`을 사용한 대분류·중분류·배율·결합 필터 4건도 각각 200이었고 `totalCount`가 달랐습니다. 모든 분류·배율·정렬 조합의 의미까지 검증한 것은 아닙니다.

국내 인기 ETF는 별도로 첫 요청의 cursor를 생략하고, 반환된 값을 그대로 넣은 다음 요청까지 크기 2로 확인했습니다. 응답은 `rankingBaseAt`, `hasNext`, `items`, `cursor`이며 항목은 `no`, `ranking`, `previousRanking`, `itemCode`, `hitCount`를 포함했습니다. 첫·다음 묶음의 항목 순번은 1·2와 3·4였고 둘 다 `hasNext=true`였습니다. 따라서 첫 continuation은 확인했지만 API의 마지막 cursor까지 순회한 것으로 기록하지 않습니다.

홈 `domesticStock` 집계의 `listing`은 KRX의 `marketCapDesc`, `tradingValueDesc`, `changeRateDescUpAll`, `changeRateDescDownAll`, `tradingVolumeDesc`와 NXT의 `marketCapDesc`를 크기 2로 확인해 모두 200이었습니다. `popular`도 KRX·NXT의 첫 응답이 200이었습니다. listing의 가격은 항목 바로 아래 있고 `totalCount`, `size`, `index`가 문자열인 반면, popular는 `cursor`와 항목별 `price.krx`·`price.nxt` 구조를 사용합니다. 선택적 `marketType`, `ageGroup`과 모든 교차 조합은 이 기본 호출 결과로 검증됐다고 보지 않습니다.

국내 ETN `orderType` 값은 UI chunk에서 `MARKET_SUM_ETN`, `AMOUNT_ETN`, `UP_ETN`, `DOWN_ETN`, `QUANT_ETN`, `QUANT_HIGH_ETN`, `QUANT_LOW_ETN`, `NEW_STOCK_ETN`이 관찰되었습니다.

2026-09-07 ETN 8개 무필터 정렬의 크기 2 응답은 모두 200이었습니다. [현재 ETN chunk](https://ssl.pstatic.net/imgstock/fn/real/pc/_next/static/chunks/app/market/stock/kr/etn/%5Bchip%5D/page-cf834f1f4f441227.js)는 ETF v2 테마 메타데이터 hook을 실제로 공유하고 그 선택값을 `largeCodeList`, `middleCodeList`로 보냅니다. 실제 메타데이터의 `0101`·`0101001`을 넣은 `AMOUNT_ETN` 결합 필터도 크기 2에서 200과 두 종목 행을 반환했습니다. 현재 화면에서는 8개 탭의 주식→대형주 필터와 행 표시를 확인했습니다. 이 화면 확인을 모든 정렬·필터 조합의 API 검증으로 확대하지 않습니다.

ETN `priceTop` 화면에 새로 진입했을 때는 대분류·중분류가 모두 전체였고, 처음 표시된 100행에서 명시적인 `항목 더보기` 버튼을 누르자 URL 변경 없이 200행이 표시됐으며 버튼도 남아 있었습니다. 일반 ETN 목록의 요청 hook은 다음 `startIdx`를 1씩 증가시킵니다. `quantHigh`, `quantLow`, `new` 탭은 현재 hook이 첫 페이지에서 종료하므로 같은 더 보기 동작을 가정하지 않습니다.

[현재 기관 동향 chunk](https://ssl.pstatic.net/imgstock/fn/real/pc/_next/static/chunks/app/market/stock/kr/trend/organization/page-403e5dccb6248be5.js)는 `investorType=ORGANIZATION`과 `DAY`, `WEEK`, `MONTH`, `THREE_MONTH`를 사용합니다. `ORGANIZATION`·`DAY`·크기 2의 실제 응답은 200이며 `sections.buyRankList`, `sections.sellRankList`가 각각 두 행인 객체였습니다. 현재 더 보기 구현은 `startIdx=0`을 유지하고 `pageSize`를 20씩 늘립니다. 프로그램 동향은 별도로 `startIdx=1&pageSize=2` 응답에서 `pageable.pageNumber="1"`, `offset="2"`를 확인했으므로 여기서는 0-based 페이지 index입니다.

집계 투자자 리소스 5개는 `005930`의 무인증 응답이 모두 200이었습니다. `stock-trade`, `stock-investor-rank`는 목록, `stock-invest-rate`, `stock-investor-age`, `stock-floor`는 각각 다른 필드를 가진 객체였습니다. 특히 `stock-invest-rate?size=2`의 `rate_list`는 101개였으므로 요청 크기 옵션이 반환 배열 길이를 보장한다고 가정하지 않습니다. 이 집계 응답을 계정별 데이터 조회로 확대하지 않습니다.

후속 검증은 실제 목록에서 얻은 식별자와 제한된 첫·다음 묶음을 사용했습니다. IR은 현재 목록의 `BOARD75384` 상세가 같은 `articleId`·`itemCode`와 200을 반환했습니다. 확인한 두 목록 묶음에는 숫자 전용·PLAN ID가 없어 이 두 형식의 새 실응답 표본은 남기지 않았습니다. 이는 IR 상세 endpoint 전체가 미검증이라는 뜻과 다르며, 미래 식별자·전체 날짜·모든 필터 조합이나 원천 값의 정확성을 보증하지 않습니다. 확인된 500, 빈 목록, null 필드를 서로 구분합니다.

추가로 같은 ETN 대분류·중분류를 유지한 나머지 7개 정렬도 크기 2의 200 응답을 확인했습니다. 외국인·기관 각각 `DAY`, `WEEK`, `MONTH`, `THREE_MONTH`와 DAY의 크기 2→4 증가 요청이 200이었습니다. 이는 문서화된 기간 분기와 표본 조건의 수신 검증이며 원천 순매수 값·정렬의 수치 정확성을 보증하지 않습니다.
