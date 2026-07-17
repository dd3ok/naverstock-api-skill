# NaverStock Web API 카탈로그

기준 관찰일: 2026-05-05, 부분 재점검: 2026-07-09, 전범위 재감사: 2026-07-17
관찰 출처: 로그인하지 않은 공개 `https://stock.naver.com/` 페이지와 Next.js chunk  
기본 호스트: `https://stock.naver.com`

네이버증권 내부 API는 미문서화 상태이며 예고 없이 바뀔 수 있습니다. 이 카탈로그는 정답이 아니라 관찰 기록입니다. 운영에 의존하기 전에 현재 공개 페이지 트래픽, Next.js chunk, 소량 read-only 요청으로 다시 확인합니다.

이 카탈로그는 레거시 `finance.naver.com` HTML 페이지를 의도적으로 제외합니다. 구버전 네이버 증권 페이지가 필요하면 [dd3ok/naverfinance-api-skills](https://github.com/dd3ok/naverfinance-api-skills)를 참고해 주세요. 이 카탈로그에는 `stock.naver.com` 페이지 또는 상대 `stock.naver.com/api/...` 호출에서 확인되는 엔드포인트만 추가합니다.

## 목차

- [상태 라벨](#상태-라벨)
- [페이지 점검 메모](#페이지-점검-메모)
- [식별자 규칙](#식별자-규칙)
- [국내 주식 API](#국내-주식-api)
- [해외 주식 API](#해외-주식-api)
- [홈 및 통합 검색 API](#홈-및-통합-검색-api)
- [시장 지수와 지표](#시장-지수와-지표)
- [펀드 API 후보](#펀드-api-후보)
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
| `/market` | 307 | 2026-07-17 무쿠키 직접 요청은 `/market/stock/kr/`로 이동했고, 일부 브라우저 세션에서는 `/market/stock/usa`도 관찰됨. 상태 의존 기본값 대신 목적 route를 직접 지정 |
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
| `/market/crypto/ranking/top?exchangeType={UPBIT\|BITHUMB}` | 200 | 거래소별 가상자산 랭킹 탭 |
| `/market/crypto/news/{domesticNews\|expertContent\|marketUpdates}` | 200 | 가상자산 국내뉴스·전문가·시장 업데이트 탭 |
| `/market/crypto/sector/{UPBIT\|BITHUMB}?id={categoryId}` | 200 | 거래소별 가상자산 섹터 상세. category API와 구성 코인 목록을 사용 |
| `/crypto/{upbit\|bithumb}/{ticker}/price` | 200 | 코인 상세 가격 화면. 프로필·콘텐츠·기간/분봉 candle API를 사용 |
| `/market/marketindex` | 307 | `/market/marketindex/major/`로 이동 |
| `/market/marketindex/{major\|energy\|metals\|agricultural\|transport}` | 200 | 주요 시장지표 탭 |
| `/market/marketindex/exchangeRate/exchange` | 200 | 환율 탭. `/exchangeRate`는 이 경로로 이동 |
| `/market/marketindex/bondAndInterest/{bond\|domesticInterest\|standardInterest}` | 200 | 채권/금리 탭 |
| `/market/stock/global`, `/market/stock/usa` | 200 | 해외 주식 메인 |
| `/market/stock/usa/stocklist/{top\|priceTop\|up\|down\|marketValue\|dividend}` | 200 | 미국 종목 정렬 탭 |
| `/market/stock/usa/etf` | 307 | `/market/stock/usa/etf/priceTop`으로 이동 |
| `/market/stock/usa/industry/{industryCode}` | 200 | 미국 업종 상세와 구성 종목 |
| `/market/stock/global/{chn\|hkg\|jpn\|vnm}/top` | 200 | 해외 국가별 상위 목록 |
| `/market/stock/global/industry/{chn\|hkg\|jpn\|vnm}` | 307 | 현재 첫 industry code로 이동 |
| `/market/stock/global/industry/{chn\|hkg\|jpn\|vnm}/{industryCode}` | 200 | 국가별 업종 상세와 구성 종목 |
| `/domestic/stock/{itemCode}` | 307 | `/price`로 이동 |
| `/domestic/stock/{itemCode}/{price\|news\|notice\|ir\|discussion\|research\|shortTrade\|investmentinfo}` | 200 | 종목 상세 하위 페이지 |
| `/domestic/stock/{itemCode}/info/{company\|overview\|financial\|investment\|consensus\|industry\|sector\|share\|esg}` | 200 | 종목 정보 탭 page route |
| `/domestic/stock/{itemCode}/info/summary` | 200 | ETF 정보 요약 route |
| `/news`, `/news/flashnews`, `/news/mainnews`, `/news/ranknews`, `/news/section`, `/news/worldnews`, `/notice` | 200 | 뉴스/뉴스포커스/해외뉴스/공지 페이지 |
| `/research`, `/research/{daily\|company\|industry\|invest\|economy}` | 200 | 리서치 페이지. `/research/firm`은 404 |
| `/discussion`, `/discussion/feed/{all\|domesticStock\|market\|my}` | 200 | 토론 페이지. `/discussion/feed`는 `/discussion/feed/all`로 이동 |

`/domestic/stock/{itemCode}/shortTrade`는 `stock.naver.com` JSON API가 아니라 `https://data.krx.co.kr/comm/srt/srtLoader/index.cmd?screenId=MDCSTAT300&isuCd={itemCode}` iframe을 렌더링합니다. 이 외부 KRX 화면을 `stock.naver.com/api/...` 엔드포인트처럼 취급하지 않습니다.

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
| 종목 차트 메타 payload | `script-backed` | GET | `/api/securityFe/api/fchart/domestic/stock/{itemCode}?periodType={day\|week\|month\|year}`. `range=1m`은 2026-07-09 재점검에서 유효하지 않았습니다. |
| 종목 차트 가격 행 | `script-backed` | GET | `/api/securityService/chart/domestic/item/{itemCode}?periodType={day\|week\|month\|year}`. 기본 호출은 `range`를 생략합니다. |
| 시장 구분 | `script-backed` | GET | `/api/domestic/detail/{itemCode}/sosok` |
| 컨센서스 | `script-backed` | GET | `/api/domestic/detail/{itemCode}/consensus` |
| 업종 관련 종목 | `script-backed` | GET | `/api/domestic/detail/{itemCode}/stock/industry?page=1&pageSize=10&marketType=ALL` |
| 종목 뉴스 | `script-backed` | GET | `/api/domestic/detail/news?itemCode={itemCode}&page=1&pageSize=20` |
| 종목 공시 | `script-backed` | GET | `/api/domestic/detail/notice?itemCode={itemCode}&startIdx=0&pageSize=20&causeCode={code}` |
| 종목 IR 목록 | `script-backed` | GET | `/api/domestic/detail/ir?itemCode={itemCode}&startIdx=0&pageSize=20` |
| 종목 IR 상세 | `script-backed` | GET | `/api/domestic/detail/ir/{itemCode}/{articleId}` |
| 집계 투자자 poll 통계 | `script-backed` | GET | `/api/stockDomestic/invest-info/poll/statistics/{itemCode}` |
| 집계 투자자 분포 리소스 | `script-backed` | GET | `/api/myasset/resources/invest/{stock-trade\|stock-investor-rank\|stock-invest-rate\|stock-investor-age\|stock-floor}?item_code={itemCode}` |
| 재무 메뉴 메타데이터 | `script-backed` | GET | `/api/stockSecurity/finances/v1/domestic/{itemCode}/menu-info` |
| ESG 정보 | `script-backed` | GET | `/api/stockSecurity/finances/v1/domestic/{itemCode}/esg` |
| 종목 정보 탭 page route | `observed` | PAGE | `/domestic/stock/{itemCode}/info/{company\|overview\|financial\|investment\|consensus\|industry\|sector\|share\|esg}`. 2026-04-27 직접 확인에서 200을 반환했습니다. 하위 JSON API는 아직 script-backed가 아니므로 필요 시 현재 트래픽으로 재확인합니다. |
| 실시간 폴링 현재가 | `script-backed` | GET | `/api/polling/domestic/stock?itemCodes={codes}` |
| NXT 폴링 현재가 | `observed` | GET | `/api/polling/domestic/NXT/stock?itemCodes={codes}` |
| 국내 시장 기본 종목 목록 | `script-backed` | GET | `/api/domestic/market/stock/default?tradeType=KRX&marketType=ALL&orderType=marketSum&startIdx=0&pageSize=20` |
| 배당 목록 | `script-backed` | GET | `/api/domestic/market/stock/dividend?tradeType=KRX&marketType=ALL&dividend=dividendRate&startIdx=0&pageSize=20` |
| 검색 인기 | `script-backed` | GET | `/api/domestic/market/searchTop?nationType=KOR&startIdx=0&pageSize=20` |
| IPO 진행 | `script-backed` | GET | `/api/domestic/market/ipo/progress?IpoProgressType=LISTING&startIdx=0&pageSize=20` |
| 업종/테마 랭킹 | `script-backed` | GET | `/api/domestic/home/upjongTheme/ranking?sortType=changeRate` |
| 업종/테마/그룹사 랭킹 목록 | `script-backed` | GET | `/api/domestic/market/{upjong\|theme\|group}/list?startIdx=0&pageSize=100&sortType=changeRate` |
| 업종/테마/그룹사 상세 정보 | `script-backed` | GET | `/api/domestic/market/{upjong\|theme\|group}/{no}/info?marketType=ALL` |
| 업종/테마/그룹사 구성 종목 | `script-backed` | GET | `/api/domestic/market/{upjong\|theme\|group}/{no}/stocklist?marketType=ALL&orderType=quantTop&startIdx=0&pageSize=20` |
| 시장 집계 투자자 동향 | `script-backed` | POST | `/api/domestic/home/marketaggregate/aggregateInvestor`, JSON body는 `sections`, `tradeType`, `marketType`, `periodType`, 날짜를 포함합니다. 출력 이상 또는 4xx가 있으면 현재 페이지에서 재확인합니다. |
| 시장 집계 투자자 랭킹 | `needs-recheck` | POST | `/api/domestic/home/marketaggregate/aggregateInvestorRanking`, ranking section fields, `startIdx`, `pageSize`를 포함합니다. |
| 투자자 예탁금 목록 | `script-backed` | GET | `/api/domestic/market/trendDeposit?startIdx=0&pageSize=20` |
| 투자자 예탁금 차트 | `script-backed` | GET | `/api/domestic/market/trendDeposit/chart?startDate={yyyyMMdd}&endDate={yyyyMMdd}` |
| 외국인/기관 투자자 동향 랭킹 | `script-backed` | GET | `/api/domestic/market/trend/trendForeignOrg?investorType=FOREIGNER&tradeType=KRX&marketType=ALL&startIdx=0&pageSize=20&periodType=DAY` |
| 투자자 동향 일별 행 | `script-backed` | GET | `/api/domestic/market/trend/daily?tradeType=KRX&marketType=ALL&bizdate={yyyyMMdd}&startIdx=0&pageSize=20` |
| 투자자 동향 시간 차트 | `script-backed` | GET | `/api/domestic/market/trend/chart/time?tradeType=KRX&marketType=ALL&selectedRange=1일&bizdate={yyyyMMdd}&startDate={yyyyMMdd}&endDate={yyyyMMdd}` |
| 프로그램 매매 동향 행 | `script-backed` | GET | `/api/domestic/market/trendProgram?tradeType=KRX&krxMarketType=ALL&bizdate={yyyyMMdd}&startIdx=0&pageSize=20&periodType=TIME` |
| 프로그램 매매 동향 차트 | `script-backed` | GET | `/api/domestic/market/trendProgram/chart?tradeType=KRX&krxMarketType=ALL&bizdate={yyyyMMdd}&startDate={yyyyMMdd}&endDate={yyyyMMdd}&periodType=TIME` |
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
| 주목할 ETF | `script-backed` | GET | `/api/domestic/market/home/notableETF?orderType=up_etf&startIdx=0&pageSize=10` |
| 홈 브리핑 | `observed` | GET | `/api/securityService/home/v3/briefing` |
| 서비스 공지 목록 | `script-backed` | GET | `/api/stockSecurity/notices/v2?size=20&cursor={cursor}` |
| 서비스 공지 상세 | `script-backed` | GET | `/api/stockSecurity/notices/v2/{noticeId}` |
| 서비스 공지 배너 | `script-backed` | GET | `/api/stockSecurity/notices/v2/banners?size=2&type=PC_TOP` |
| 홈 공지 목록 legacy | `needs-recheck` | GET | `/api/domestic/home/noticeList?page=1&pageSize=5`. 2026-07-09 직접 확인에서 404를 반환했습니다. 서비스 공지는 `stockSecurity/notices/v2`를 우선 사용합니다. |
| 홈 공지 상세 legacy | `needs-recheck` | GET | `/api/domestic/home/notice/{noticeId}`. 새 경로는 `/api/stockSecurity/notices/v2/{noticeId}`입니다. |
| 홈 공개 보유자산 랭킹 | `script-backed` | GET | `/api/domestic/home/ranking/assetAmount/all?startIdx=0&pageSize=20` |
| 홈 공개 수익률 랭킹 | `script-backed` | GET | `/api/domestic/home/ranking/earningRate/all?startIdx=0&pageSize=20` |
| 홈 공개 보유종목 랭킹 | `script-backed` | GET | `/api/securityService/home/v3/ranking/more/domestic/holdingStock/all` |
| 홈 관련 국내 종목 | `script-backed` | GET | `/api/securityService/home/v3/stock/{itemCode}/related` |
| 국내 지수 시간대 시세 | `observed` | GET | `/api/domestic/indexSise/time?koreaIndexType=KOSPI&thistime={yyyyMMddHHmmss}&startIdx=0&pageSize=20` |
| AI 현재 시장 브리핑 | `script-backed` | GET | `/api/securityAi/marketBriefing/current?marketBriefing=domain` |
| AI 시장 브리핑 목록 | `script-backed` | GET | `/api/securityAi/marketBriefing?date={yyyy-MM-dd}&size=20&pageToken={token}` |
| AI 시장 브리핑 상세 | `script-backed` | GET | `/api/securityAi/marketBriefing/{briefingId}` |

관찰된 종목 목록 `orderType` 값에는 `marketSum`, `accAmount`, `searchTop`, `up`, `steady`, `down`, `quantTop`, 그리고 `investmentCaution`, `investmentWarning`, `investmentRisk` 같은 투자 경고 관련 값이 포함됩니다.

`stock.naver.com/market/stock/kr/{industry|theme|groups}/{rank}` 페이지의 path 값은 현재 카테고리 `no`가 아니라 화면의 랭킹 순번입니다. 먼저 list API에서 현재 카테고리 `no`를 찾은 뒤 `info`와 `stocklist`를 호출합니다. API path는 `industry`에 `upjong`, `theme`에 `theme`, `groups`에 `group`을 사용합니다. `/industry/1`의 `1`은 페이지 rank이며 실제 카테고리 `no`와 다를 수 있습니다.

관찰된 카테고리 종목 목록 `orderType` 값에는 `quantTop`, `priceTop`, `up`, `down`, `marketSum`, `sales`, `operatingProfit`이 포함됩니다. UI chip alias는 `accQuant -> quantTop`, `accAmount -> priceTop`으로 매핑됩니다.

2026-04-27 직접 확인에서 열렸고 2026-07-09 정적 route로 재확인한 국내 주식 메뉴 route: `/market/stock/kr/stocklist/*`, `/market/stock/kr/etf/*`, `/market/stock/kr/etn/*`, `/market/stock/kr/ipo`, `/market/stock/kr/deposit`, `/market/stock/kr/trend/{foreigner|organization|program|trader}`, 종목 상세 하위 페이지 `/domestic/stock/{itemCode}/{price|news|notice|ir|discussion|research|shortTrade|investmentinfo}`, 종목 정보 탭 `/domestic/stock/{itemCode}/info/*`와 ETF `/domestic/stock/{itemCode}/info/summary`. `/domestic/stock/{itemCode}/financial`, `/total`, `/chart`, `/analysis`, `/investment`는 직접 확인에서 404를 반환했습니다.

국내 ETF `listingType` alias는 UI chunk에서 `tradingValueDesc`, `aumDesc`, `changeRateDescUpAll`, `changeRateDescDownAll`, `tradingVolumeDesc`, `tradingVolumeIncreaseRateDesc`, `tradingVolumeIncreaseRateAsc`, `returnRate1mDesc`, `returnRate3mDesc`, `returnRate6mDesc`, `marketCapDesc`, `listedAtDesc`가 관찰되었습니다.

국내 ETN `orderType` 값은 UI chunk에서 `MARKET_SUM_ETN`, `AMOUNT_ETN`, `UP_ETN`, `DOWN_ETN`, `QUANT_ETN`, `QUANT_HIGH_ETN`, `QUANT_LOW_ETN`, `NEW_STOCK_ETN`이 관찰되었습니다.

`/market/stock/global`, `/market/stock/usa/stocklist`, `/market/stock/global/{chn|hkg|jpn|vnm}` 하위 국가 페이지 같은 해외 주식 route도 접근 가능하며 `/api/foreign/*`, `/api/securityService/stock/*`, `/api/securityService/etf/*`, worldstock polling 계열을 노출합니다. 주식 관련이지만 국내 스크립트와 코드 체계를 섞지 않기 위해 별도로 둡니다.

## 해외 주식 API

| 목적 | 상태 | Method | Path / params |
| --- | --- | ---: | --- |
| 국가별 종목 목록 | `script-backed` | GET | `/api/foreign/market/stock/global?nation={usa|chn|hkg|jpn|vnm}&tradeType={type}&orderType={type}&startIdx=0&pageSize=20` |
| 국가별 업종 | `script-backed` | GET | `/api/foreign/market/{USA|CHN|HKG|JPN|VNM}/upjong/list` |
| 해외 업종 구성 종목 | `script-backed` | GET | `/api/foreign/market/{nation}/upjong/{industryCode}/list?orderType=marketValue&startIdx=0&pageSize=20` |
| 미국 ETF 테마 | `script-backed` | GET | `/api/foreign/market/etf/themes` |
| 미국 ETF 목록 | `script-backed` | GET | `/api/foreign/market/etf/usa?orderType=marketValue&largeCode=all&middleCode=all&startIdx=0&pageSize=20` |
| 미국 주목 ETF | `script-backed` | GET | `/api/foreign/market/home/notableETF?orderType={priceTop\|up\|return1Month\|dividend}&startIdx=0&pageSize=20` |
| ETF 테마 종목 | `script-backed` | GET | `/api/foreign/market/usa/etf/themeList?middleCode={code}&count=3` |
| 해외 주식 기본/컨센서스/개요 | `script-backed` | GET | `/api/securityService/stock/{reutersCode}/{basic|consensus|overview}` |
| 해외 주식 일별 시세 | `script-backed` | GET | `/api/securityService/stock/{reutersCode}/price?page=1&pageSize=20` |
| 해외 종목 재무 개요·요약 | `script-backed` | GET | `/api/securityService/stock/overview?reutersCode={code}`, `/api/securityService/stock/finance/summary?reutersCode={code}` |
| 해외 종목 재무제표 | `script-backed` | GET | `/api/securityService/stock/finance/{annual|quarter}?reutersCode={code}`, `/api/securityService/stock/finance/{ratios|balance|income|cash}/{annual|quarter}?reutersCode={code}` |
| 해외 종목 글로벌·국내 뉴스 | `script-backed` | GET | `/api/foreign/worldStock/list?reutersCode={code}&page=1&pageSize=20`, `/api/domestic/detail/news?itemCode={code}&page=1&pageSize=20` |
| 해외 주식·ETF master detail | `script-backed` | GET | `/api/foreign/{reutersCode}/detail?codeType=ETF`. 2026-07-17 현재 일반 주식도 literal `ETF`를 사용합니다. |
| 해외 ETF 시세·관련 ETF | `script-backed` | GET | `/api/securityService/etf/{reutersCode}/price`, `/api/foreign/v2/market/etf/usa/{reutersCode}` |
| 해외 지수 기본/시세/구성 | `script-backed` | GET | `/api/securityService/index/{reutersCode}/{basic|price|enrollStocks}` |
| 해외 종목 폴링 | `script-backed` | GET | `/api/polling/worldstock/{stock|etf|index}?reutersCodes={codes}` |
| 해외 거래소 운영시간 | `script-backed` | GET | `/api/foreign/operatingTime/exchange/{NASDAQ|NYSE|AMEX}` |

## 홈 및 통합 검색 API

| 목적 | 상태 | Method | Path / params |
| --- | --- | ---: | --- |
| KRX/NXT 시장 상태 | `script-backed` | GET | `/api/domestic/market/{KRX|NXT}/info` |
| 해외 거래소 운영시간 | `script-backed` | GET | `/api/foreign/operatingTime/exchange/{NASDAQ|SHANGHAI|HONG_KONG|TOKYO|HANOI}` |
| 홈 공개 숏텐츠 | `script-backed` | GET | `/api/shorttents?source=pc.npay_finhome&type=compact&category_first=증권&nscs=0` |
| 머니스토리 | `script-backed` | GET | `/api/content/moneyStory?mainCategoryIdList={id}&size={size}` |
| 통합 지표 | `script-backed` | GET | `/api/securityService/integration/indicators?indicatorCodes={codes}` |
| 국내·해외 주목 ETF | `script-backed` | GET | `/api/{domestic|foreign}/market/home/notableETF?orderType={type}&startIdx=0&pageSize=10`. 현재 UI enum은 국내 `amount_etf`, `up_etf`, `1week_earn_rate`, `dividend_earn_rate`, 해외 `priceTop`, `up`, `return1Month`, `dividend`입니다. 기본값은 각각 `amount_etf`, `up`이며 다른 국가의 enum은 보내지 않습니다. |
| 중요 경제지표 | `script-backed` | GET | `/api/securityService/economic/indicator/nations/upcoming?gteImportance=3&limit=3&nationTypeList=KOR&nationTypeList=USA` |
| 공개 전체 이용자 자산·수익률 랭킹 | `script-backed` | GET | `/api/domestic/home/ranking/{assetAmount|earningRate}/all?startIdx=0&pageSize=20` |
| 공개 전체 보유종목 랭킹 | `script-backed` | GET | `/api/securityService/home/v3/ranking/more/domestic/holdingStock/all` |
| 관련 국내 종목 | `script-backed` | GET | `/api/securityService/home/v3/stock/{itemCode}/related` |
| 헤더 자동완성 | `script-backed` | GET | `/api/autocomplete/search/autoComplete?query={text}&target=stock,index,marketindicator,coin,ipo,fund` |
| 전체 상품 검색 | `script-backed` | GET | `/api/autocomplete/search?q={text}&target=stock,index,marketindicator,coin,ipo,fund&size=30&page=1` |

검색 결과의 최근 기록 endpoint와 `/api/personal/{guest|users}/recent/products`는 개인 상태이므로 호출하지 않습니다.

## 시장 지수와 지표

| 목적 | 상태 | Method | Path / params |
| --- | --- | ---: | --- |
| 주요 지수 | `script-backed` | GET | `/api/securityFe/api/index/majors` |
| 시장지표 주요 블록 | `script-backed` | GET | `/api/securityService/marketindex/majors/{type}`. 관찰된 `type`: `exchange`, `exchangeWorld`, `domesticInterest`, `bond`, `rpc` |
| 지수 기본 정보 | `observed` | GET | `/api/securityFe/api/index/{reutersCode}/basic` |
| 지수 통합 정보 | `observed` | GET | `/api/securityFe/api/index/{reutersCode}/integration` |
| 지수 가격 이력 | `observed` | GET | `/api/securityFe/api/index/{reutersCode}/price?page=1&pageSize=20` |
| 국내 지수 폴링 | `script-backed` | GET | `/api/polling/domestic/index?itemCodes=KOSPI,KOSDAQ,KPI200` |
| 지수 차트 | `script-backed` | GET | `/api/securityService/chart/domestic/index/{code}?periodType={day\|week\|month\|year}` |
| 해외 지수/선물 차트 | `script-backed` | GET | `/api/securityService/chart/foreign/{index\|futures}/{code}?periodType=day` |
| 원자재/운임 지표 | `script-backed` | GET | `/api/securityService/marketindex/energy`, `/metals`, `/agricultural`, `/transport` |
| 국내 금리 | `script-backed` | GET | `/api/securityService/marketindex/domesticInterest` |
| 기타 지표 카테고리 | `observed` | GET | `/api/securityService/marketindex/exchange`, `/bond`, `/standardInterest` 및 각 카테고리 상세 path |
| 지표 상세 | `script-backed` | GET | `/api/securityService/marketindex/{energy\|metals\|agricultural\|transport\|domesticInterest\|exchange}/{reutersCode}` |
| 지표 가격 이력 | `script-backed` | GET | `/api/securityService/marketindex/{energy\|metals\|agricultural\|transport\|exchange}/{reutersCode}/prices?page=1&pageSize=20` |
| 국가별 채권 | `script-backed` | GET | `/api/securityService/marketindex/bond/nation/{nationType}?sortType={sortType}` |
| 기준금리 상세 | `script-backed` | GET | `/api/securityService/marketindex/standardInterest/{nationType}` |
| 기준금리 달력 | `script-backed` | GET | `/api/securityService/marketindex/standardInterest/{nationType}/calendars?page=1&pageSize=20` |
| 예정 경제지표 | `script-backed` | GET | `/api/securityService/economic/indicator/nations/upcoming?limit=10&nationTypeList=USA&nationTypeList=KOR`. 2026-07-09 재점검에서 파라미터 생략 또는 반복 `nationTypeList`는 동작했고, 단일 `nationTypeList=USA`는 400을 반환했습니다. |
| 발표일별 경제지표 | `script-backed` | GET | `/api/securityService/economic/indicator/nations/releaseDate?page=1&pageSize=20&releaseDate={yyyyMMdd}` |
| 환율 helper | `script-backed` | GET | `/api/stockDomestic/exchangeRates/list?currencies=USD,JPY` |
| 환율 목록 | `script-backed` | GET | `/api/domestic/exchange/List` |
| 통화별 환율 시세 | `script-backed` | GET | `/api/domestic/exchange/{currency}/list?startIdx=0&pageSize=20` |
| 은행 환율 요약 | `script-backed` | GET | `/api/securityService/marketindex/exchange/banksExchanges?bankType=HNB` |
| 은행 환율 회차 차트 | `script-backed` | GET | `/api/stockSecurity/exchange-rates/v2/{currency}/charts/round?bankType=hana` |
| KRX 금 시세 | `script-backed` | GET | `/api/stockDomestic/gold/sise/krx` |
| 시장지표 폴링 | `script-backed` | GET | `/api/polling/marketindex/{energy\|metals\|exchange}/{codes}`. KRX 금은 `metals/M04020000`을 사용합니다. |
| 통합 지표 | `observed` | GET | `/api/securityService/integration/indicators?stockType=domestic&indicatorCodes=KOSPI&indicatorCodes=KOSDAQ` |
| 통합 가격 | `observed` | GET | `/api/securityService/integration/price?domesticKrxCodes=005930&foreignCodes=.IXIC&cryptoCodes=BTC_KRW_UPBIT` |

`/api/securityService/marketindex/majors` 같은 오래된 형태의 route는 2026-04-27에 404를 반환했습니다. 주요 지수에는 `/api/securityFe/api/index/majors`를 사용합니다.

## 펀드 API 후보

2026-07-17 현재 `/fund`와 `/domestic/fund` page route는 모두 404입니다. 공통 정적 chunk에는 아래 helper 문자열이 남아 있지만, 로드 가능한 펀드 화면과 실제 UI 요청이 없어 `sort`, `term`, `fundCode`, theme enum을 검증할 수 없습니다. 따라서 요청 helper도 `/api/fund/` family를 broad allowlist하지 않고, 스크립트 명령을 제공하지 않습니다.

| 목적 | 상태 | Method | Path / params |
| --- | --- | ---: | --- |
| 펀드 목록·상세 후보 | `needs-recheck` | GET | `/api/fund/funds?sort={sort}&page={page}&size={size}`, `/api/fund/funds/{fundCode}/{left-panel|themes|chart-price-panel|fund-performance|fund-allocation}` |
| 수익·보수·상세 지표 후보 | `needs-recheck` | GET | `/api/fund/funds/{fundCode}/classes/{returns|fees}`, `/metrics/detail?term={term}` |
| 가격·차트 후보 | `needs-recheck` | GET | `/prices/daily?date={date}&size={size}`, `/base-price/chart?term={term}`, `/return/chart?term={term}` |
| 테마·다중 가격 후보 | `needs-recheck` | GET | `/api/fund/funds/themes/{theme}?size={size}`, `/api/fund/funds/prices?fundCodes={codes}` |

## 가상자산 API

| 목적 | 상태 | Method | Path / params |
| --- | --- | ---: | --- |
| 랭킹 목록 | `script-backed` | GET | `/api/coin/rank/{market}?sortType=marketValue&page=1&pageSize=60` |
| 주요 코인 | `script-backed` | GET | `/api/coin/rank/{market}/majors` |
| 거래소별 코인 가격 | `script-backed` | GET | `/api/coin/price/{market}/{ticker}` |
| 거래소 비교용 코인 가격 | `script-backed` | GET | `/api/coin/price/{ticker}?excludeExchange={market}` |
| 폴링 가격 | `script-backed` | GET | `/api/polling/coin/price?fqnfTickers=BTC_KRW_UPBIT` |
| 분봉 캔들 | `script-backed` | GET | `/api/coin/candle/{market}/KRW/{ticker}/minutes/{unit}/marketInfo?from={iso}&to={iso}` |
| 기간 캔들 | `script-backed` | GET | `/api/coin/candle/{market}/KRW/{ticker}/{year\|weeks\|quarter\|months\|days}?from={iso}&to={iso}` |
| 상세 분봉 캔들 | `script-backed` | GET | `/api/coin/candle/{market}/KRW/{ticker}/minutes/{unit}?from={iso}&to={iso}` |
| 국내 지수 비교 차트 | `script-backed` | GET | `/api/securityService/chart/compare/domestic/index/{code}/{day\|week}?startDateTime={yyyyMMddHHmmss}&endDateTime={yyyyMMddHHmmss}` |
| 해외 지수/선물 비교 차트 | `script-backed` | GET | `/api/securityService/chart/compare/foreign/{index\|futures}/{code}/{day\|week}?startDateTime={yyyyMMddHHmmss}&endDateTime={yyyyMMddHHmmss}` |
| 해외 지수/선물 분봉 비교 차트 | `script-backed` | GET | `/api/securityService/chart/foreign/{INDEX\|FUTURES}/{NASDAQ\|NYSE\|COMEX\|ICE_US}/{code}/interval/{1\|5}?startDateTime={yyyyMMddHHmmss}&endDateTime={yyyyMMddHHmmss}&utc=true` |
| 글로벌 뉴스 | `script-backed` | GET | `/api/coin/globalNews/{ticker}?pageSize=20&offsetTimestamp={timestamp}` |
| 시장 업데이트 | `script-backed` | GET | `/api/coin/marketUpdates/{ticker}?pageSize=20&offsetTimestamp={timestamp}` |
| 전체 시장 업데이트 | `script-backed` | GET | `/api/coin/marketUpdates?pageSize=9` |
| 전문가 콘텐츠 | `script-backed` | GET | `/api/coin/expertContents?pageSize=10` |
| 업데이트·전문가 콘텐츠 상세 | `script-backed` | GET | `/api/coin/marketUpdates/detail/{id}`, `/api/coin/expertContents/{id}` |
| 종목별 전문가 콘텐츠 | `script-backed` | GET | `/api/coin/{ticker}/expertContents?pageSize=10&offsetTimestamp={cursor}` |
| 코인 프로필 | `script-backed` | GET | `/api/coin/profile/{ticker}` |
| 카테고리 랭킹 | `script-backed` | GET | `/api/coin/categories/ranking?exchangeType=UPBIT&page=1&pageSize=20` |
| 카테고리 상세·종목 카테고리 | `script-backed` | GET | `/api/coin/categories/{categoryId}?exchangeType=UPBIT`, `/api/coin/{ticker}/categories?exchangeType=UPBIT` |
| 코인 ETF 노출 | `script-backed` | GET | `/api/coin/etf/{ticker}?sortType=holdingWeight&size=20&page=1` 또는 `pageToken` |
| 여러 코인 가격 | `script-backed` | GET | `/api/coin/prices?fqnfTickers=BTC_KRW_UPBIT&fqnfTickers=ETH_KRW_UPBIT` |
| 글로벌 시장 동향 | `script-backed` | GET | `/api/coin/globalMarketTrend` |
| 가격 변동 legacy 후보 | `needs-recheck` | GET | `/api/coin/priceChange/{ticker}?exchangeType=UPBIT`. 정적 chunk 문자열은 관찰됐지만 2026-07-09 직접 요청에서 404를 반환해 스크립트로 노출하지 않습니다. |
| 코인 매크로 뉴스 | `script-backed` | GET | `/api/securityFe/api/news/coinmacro?page=1&pageSize=10` |
| AI 코인 브리핑 | `script-backed` | GET | `/api/securityAi/coinBriefing/current?exchangeType=UPBIT&nfTicker=BTC` |
| AI 코인 브리핑 이력·상세 | `script-backed` | GET | `/api/securityAi/coinBriefings?exchangeType=UPBIT&nfTicker=BTC&size=20&date={yyyy-MM-dd}&pageToken={token}`, `/api/securityAi/coinBriefing/{id}` |

`UPBIT` 또는 `BITHUMB`을 대문자로 사용합니다. 폴링 엔드포인트는 `BTC_KRW_UPBIT` 같은 `fqnfTicker` 값을 받고, 뉴스/업데이트/프로필 엔드포인트는 `BTC` 같은 plain ticker를 받습니다. 직접 확인에서 일반 `KRW-BTC`는 빈 list를 반환했습니다.

## 뉴스 API

| 목적 | 상태 | Method | Path / params |
| --- | --- | ---: | --- |
| 뉴스 목록 | `script-backed` | GET | `/api/domestic/news/list?category=mainnews&page=1&pageSize=20` |
| 포커스 뉴스 (`/news/section`) | `script-backed` | GET | `/api/domestic/news/focus?sid=401&page=1&pageSize=20` |
| 뉴스포커스 해외증시 후보 (`/news/section`, `global-market`) | `script-backed` | GET | `/api/domestic/news/focus?sid=403&page=1&pageSize=20`. 2026-05-06 재확인에서 빈 결과가 나왔으므로 미국 public briefing의 단독 해외뉴스 소스로 쓰지 않습니다. |
| 뉴스 검색 | `script-backed` | GET | `/api/domestic/news/search?query=반도체&page=1&pageSize=20` |
| 시장 공시/공지 뉴스 | `script-backed` | GET | `/api/domestic/news/noticeList?page=1&pageSize=20&keyword={keyword}&typeIdx={idx}` |
| 해외뉴스 목록 (`/news/worldnews`) | `script-backed` | GET | `/api/foreign/news/worldNews?page=1&pageSize=20&date={yyyyMMdd}`. Reuters/해외 시장 뉴스 목록입니다. |
| 해외뉴스 상세 (`/news/worldnews/{aid}`) | `script-backed` | GET | `/api/foreign/news/worldNews/{aid}` |
| 뉴스 홈 집계 | `script-backed` | GET | `/api/domestic/news/aggregate/home?flashNewsSize=5&mainNewsSize=5&rankingNewsSize=5&overseasNewsSize=5&focusSize=5&moneyStorySize=5&noticeSize=5` |

관찰된 목록 카테고리에는 `mainnews`, `flashnews`, `ranknews`가 있습니다. `stock`, `market`, `all` 같은 임의 값은 실패할 수 있습니다.

2026-05-05 직접 확인에서 뉴스 상단 탭 route는 `/news/flashnews`, `/news/mainnews`, `/news/ranknews`, `/news/section`, `/news/worldnews`였습니다. `/news/worldnews`는 `page`가 1부터 증가하는 목록 API를 사용하고, 날짜 필터는 `date=yyyyMMdd`를 추가합니다. 각 목록 item의 `aid`로 `/news/worldnews/{aid}` 페이지와 `/api/foreign/news/worldNews/{aid}` 상세 API를 조회할 수 있습니다. 상세 응답은 `{ "article": ..., "latestList": [...] }` 형태이며 `article.subcontent`에 HTML 원문/고지 문구가 포함될 수 있습니다.

`/news/section`의 포커스 뉴스는 `/api/domestic/news/focus`를 사용하며, 하위 탭은 query `tab`으로 선택됩니다. 관찰된 탭/섹션 맵은 `market-outlook=401`(시황·전망), `company-analysis=402`(기업·종목분석), `global-market=403`(해외증시), `bond-futures=404`(채권·선물), `disclosure-memo=406`(공시·메모), `exchange-rate=429`(환율)입니다. 최신순 기본 호출은 현재 날짜 `date=yyyyMMdd`와 `enableFallback=true`를 함께 보내 과거 기사로 fallback할 수 있고, 직접 지정 시 `maxDays`는 1-7 범위만 허용됩니다. 날짜별 필터에서는 선택 날짜의 기사만 남기도록 클라이언트가 추가 필터링합니다. 단, 2026-05-06 재확인에서 `global-market`/`sid=403`은 빈 결과였고 실제 해외뉴스 목록은 `/news/worldnews`의 `/api/foreign/news/worldNews`가 반환했습니다. 미국장/해외뉴스 briefing에는 `/api/foreign/news/worldNews`를 우선 사용하고, `sid=403`은 포커스 섹션 보조 후보로만 취급합니다.

## 리서치 API

| 목적 | 상태 | Method | Path / params |
| --- | --- | ---: | --- |
| 리서치 카테고리 목록 | `script-backed` | GET | `/api/domestic/research/category?category=COMPANY&page=1&pageSize=15` |
| 카테고리 상세 | `script-backed` | GET | `/api/domestic/research/category/{researchId}?category=COMPANY` |
| 종목 리포트 목록 | `script-backed` | GET | `/api/domestic/research/{itemCode}/research?page=0&size=30` |
| 종목 리포트 상세 | `observed` | GET | `/api/domestic/research/{itemCode}/research/{researchId}` |
| 최근 인기 | `script-backed` | GET | `/api/domestic/research/recent-popular` |
| 리서치 홈 집계 legacy | `needs-recheck` | POST | `/api/domestic/home/researchaggregate/static`. 2026-07-09 직접 확인에서 404를 반환했습니다. 새 리서치 홈은 `stockSecurity/researches/v1` 계열을 우선 사용합니다. |
| 카테고리 최신 | `script-backed` | GET | `/api/domestic/research/category-lastest`. API path의 `lastest` 오탈자 형태를 그대로 사용합니다. |
| 산업 리서치 | `script-backed` | GET | `/api/domestic/research/industry-research` |
| 랭킹 | `script-backed` | GET | `/api/domestic/research/ranking?rankingType={type}&selectedRank={rank}` |
| 증권사 목록 | `script-backed` | GET | `/api/domestic/research/broker-list` |
| v1 리서치 카테고리 목록 | `script-backed` | GET | `/api/stockSecurity/researches/v1/{company\|industry\|invest\|economy}?index=0&size=15` |
| v1 증권사 목록 | `script-backed` | GET | `/api/stockSecurity/researches/v1/brokers` |
| v1 최신 리서치 블록 | `script-backed` | GET | `/api/stockSecurity/researches/v1/latestResearch?size=5` |
| v1 종목별 회사 리서치 | `script-backed` | GET | `/api/stockSecurity/researches/v1/company/by-items?itemCodes=005930&itemCodes=000660&size=5` |
| v1 분석 포커스 | `script-backed` | GET | `/api/stockSecurity/researches/v1/analysis-focus` |

검증 오류와 chunk에서 관찰된 카테고리 enum: `INVEST`, `MARKET`, `INDUSTRY`, `COMPANY`, `ECONOMY`, `DEBENTURE`.

## 종목토론 API

| 목적 | 상태 | Method | Path / params |
| --- | --- | ---: | --- |
| 인기 feed | `observed` | GET | `/api/community/discussion/posts/hot?pageSize=20&page=1&discussionType={type}&itemCode={itemCode}` |
| 홈 인기 feed | `script-backed` | GET | `/api/community/discussion/posts/hot/home?pageSize=20&page=1` |
| 글 상세 | `script-backed` | GET | `/api/community/discussion/posts/{postId}` |
| 이전/다음 글 이동 | `script-backed` | GET | `/api/community/discussion/posts/{postId}/adjacent?pageSize=20&itemCode={itemCode}` |
| 관련 인기 글 | `script-backed` | GET | `/api/community/discussion/posts/related/hot?itemCode={itemCode}&pageSize=20&discussionType=domesticStock` |
| 인기 글 | `script-backed` | GET | `/api/community/discussion/posts/popular/hot` |
| 일반 feed | `script-backed` | GET | `/api/community/discussion/posts?pageSize=20&offset={offset}` |
| 시장 feed | `script-backed` | GET | `/api/community/discussion/posts/market?filterType=marketIndex&offset={offset}&pageSize=20` |
| 종목 글 | `observed` | GET | `/api/community/discussion/posts?itemCode={itemCode}&pageSize=20` |
| 종목별 글 | `script-backed` | GET | `/api/community/discussion/posts/by-item?itemCode={itemCode}&discussionType=domesticStock&pageSize=20&isHolderOnly=false&excludesItemNews=false&isItemNewsOnly=false` |
| 여러 종목 글 | `observed` | GET | `/api/community/discussion/posts/by-item-codes?filterType=itemCodes&pageSize=20&offset={offset}&domesticCodes={codes}` |
| 최신 종목 글 | `observed` | GET | `/api/community/discussion/items/posts/latest?domesticCodes={codes}&limit=10` |
| 댓글 수 | `observed` | GET | `/api/community/discussion/posts/comment-counts?postIds={ids}` |
| 반응 조회 | `observed` | GET | `/api/community/discussion/posts/reactions?postIds={ids}` |
| 랭킹 | `script-backed` | GET | `/api/community/discussion/rankings?nationType=KOR&page=1&size=20&postType=HOT` |
| 종목 통계 | `script-backed` | GET | `/api/community/discussion/stats/by-items?startDate={yyyy-MM-dd}&domesticCodes={codes}&foreignCodes={codes}`. 2026-07-09 기준 `startDate`가 필요하고, legacy `itemCodes`만 보내는 호출은 400을 반환했습니다. |

작성, 프로필 편집, 이미지 업로드, 닉네임 검증/추천, 반응 mutation, 인증된 커뮤니티 프로필 워크플로는 피합니다.

## 제외 계열

| 계열 | 상태 | 이유 |
| --- | --- | --- |
| `/api/auth/*` | `excluded` | 로그인/인증. |
| `/api/personal/users/holding/*` | `excluded` | 계좌 보유종목과 refresh 워크플로. |
| `/api/personal/users/favorite/*` | `excluded` | 사용자별 관심종목과 그룹. |
| `/api/personal/users/notification*` | `excluded` | 사용자 알림 설정/메시지. |
| `/api/community/profile/users/*` mutation-like routes | `excluded` | 사용자 프로필과 이미지 워크플로. |
| `/api/domestic/home/recommend-aggregate` | `excluded` | 현재 웹 번들은 credentials 포함 POST와 연령/자산 범위 개인화 필드를 사용합니다. |
| `/api/autocomplete/search/recent`, `/api/personal/*/recent/products` | `excluded` | 최근 검색·최근 상품 개인 상태. |
| `https://finance.naver.com/*` | `excluded` | 이 스킬 범위인 `stock.naver.com` 밖의 구버전 HTML 페이지입니다. 해당 범위는 [dd3ok/naverfinance-api-skills](https://github.com/dd3ok/naverfinance-api-skills)를 참고해 주세요. |
| 텔레메트리, 광고, 정적 chunk, 폰트, 이미지 | `excluded` | 주식 정보 API가 아닙니다. |
