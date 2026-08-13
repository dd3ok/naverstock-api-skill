# 홈·시장 지표·펀드 API

상태 라벨, page route, 전송, 식별자와 제외 기준은 [공통 API 인덱스](api-catalog.md)를 따릅니다.

## 홈 및 통합 검색 API

| 목적 | 상태 | Method | Path / params |
| --- | --- | ---: | --- |
| KRX/NXT 시장 상태 | `script-backed` | GET | `/api/domestic/market/{KRX|NXT}/info` |
| 해외 거래소 운영시간 | `script-backed` | GET | `/api/foreign/operatingTime/exchange/{NASDAQ|SHANGHAI|HONG_KONG|TOKYO|HANOI}` |
| 홈 공개 숏텐츠 | `script-backed` | GET | `/api/shorttents?source=pc.npay_finhome&type=compact&category_first=증권&nscs=0` |
| 머니스토리 | `script-backed` | GET | `/api/content/moneyStory?mainCategoryIdList={id}&subCategoryIdList={id}&sort=id%2Cdesc&size={size}`. `subCategoryIdList`와 `sort`는 선택적이며 가상자산 홈에서 각각 `97`, `id,desc`를 사용 |
| 통합 지표 | `script-backed` | GET | `/api/securityService/integration/indicators?indicatorCodes={codes}` |
| 국내·해외 주목 ETF | `script-backed` | GET | `/api/{domestic|foreign}/market/home/notableETF?orderType={type}&startIdx=0&pageSize=10`. 현재 UI enum은 국내 `amount_etf`, `up_etf`, `1week_earn_rate`, `dividend_earn_rate`, 해외 `priceTop`, `up`, `return1Month`, `dividend`입니다. 기본값은 각각 `amount_etf`, `up`이며 다른 국가의 enum은 보내지 않습니다. |
| 중요 경제지표 | `script-backed` | GET | `/api/securityService/economic/indicator/nations/upcoming?gteImportance=3&limit=3&nationTypeList=KOR&nationTypeList=USA` |
| 공개 전체 이용자 자산·수익률 랭킹 | `script-backed` | GET | `/api/domestic/home/ranking/{assetAmount|earningRate}/all?startIdx=0&pageSize=20` |
| 공개 전체 보유종목 랭킹 | `script-backed` | GET | `/api/securityService/home/v3/ranking/more/domestic/holdingStock/all` |
| 관련 국내 종목 | `script-backed` | GET | `/api/securityService/home/v3/stock/{itemCode}/related` |
| 헤더 자동완성 | `script-backed` | GET | `/api/autocomplete/search/autoComplete?query={text}&target=stock,index,marketindicator,coin,ipo,fund` |
| 전체 상품 검색 | `script-backed` | GET | `/api/autocomplete/search?q={text}&target=stock,index,marketindicator,coin,ipo,fund&size=30&page=1` |
| 홈 브리핑 | `observed` | GET | `/api/securityService/home/v3/briefing` |
| AI 현재 시장 브리핑 | `script-backed` | GET | `/api/securityAi/marketBriefing/current?marketBriefing=domain` |
| AI 시장 브리핑 목록 | `script-backed` | GET | `/api/securityAi/marketBriefing?date={yyyy-MM-dd}&size=20&pageToken={token}` |
| AI 시장 브리핑 상세 | `script-backed` | GET | `/api/securityAi/marketBriefing/{briefingId}` |

검색 결과의 최근 기록 endpoint와 `/api/personal/{guest|users}/recent/products`는 개인 상태이므로 호출하지 않습니다.

## 시장 지수와 지표

| 목적 | 상태 | Method | Path / params |
| --- | --- | ---: | --- |
| 주요 지수 | `script-backed` | GET | `/api/securityFe/api/index/majors` |
| 시장지표 주요 블록 | `script-backed` | GET | `/api/securityService/marketindex/majors/{type}`. 관찰된 `type`: `exchange`, `exchangeWorld`, `domesticInterest`, `standardInterest`, `bond`, `rpc` |
| 지수 기본 정보 | `script-backed` | GET | `/api/securityFe/api/index/{reutersCode}/basic` |
| 지수 통합 정보 | `script-backed` | GET | `/api/securityFe/api/index/{reutersCode}/integration` |
| 지수 가격 이력 | `script-backed` | GET | `/api/securityFe/api/index/{reutersCode}/price?page=1&pageSize=20` |
| 국내 지수 차트 메타 | `script-backed` | GET | `/api/securityFe/api/fchart/domestic/index/{reutersCode}` |
| 국내 지수 폴링 | `script-backed` | GET | `/api/polling/domestic/index?itemCodes=KOSPI,KOSDAQ,KPI200` |
| 지수 차트 | `script-backed` | GET | `/api/securityService/chart/domestic/index/{code}?periodType={day\|week\|month\|year}` |
| 해외 지수/선물 차트 | `script-backed` | GET | `/api/securityService/chart/foreign/{index\|futures}/{code}?periodType=day` |
| 원자재/운임 지표 | `script-backed` | GET | `/api/securityService/marketindex/energy`, `/metals`, `/agricultural`, `/transport` |
| 국내 금리 | `script-backed` | GET | `/api/securityService/marketindex/domesticInterest` |
| 기타 지표 카테고리 | `script-backed` | GET | `/api/securityService/marketindex/exchange`, `/exchangeWorld`, `/bond`, `/standardInterest` 및 각 카테고리 상세 path |
| 지표 상세 | `script-backed` | GET | `/api/securityService/marketindex/{energy\|metals\|agricultural\|transport\|domesticInterest\|exchange}/{reutersCode}` |
| 지표 가격 이력 | `script-backed` | GET | `/api/securityService/marketindex/{energy\|metals\|agricultural\|transport\|exchange}/{reutersCode}/prices?page=1&pageSize=20` |
| 지표 차트 메타 | `script-backed` | GET | `/api/securityFe/api/fchart/marketindex/{energy\|metals\|agricultural\|transport\|exchange}/{reutersCode}` |
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
| 통합 가격 | `observed` | GET | `/api/securityService/integration/price?domesticKrxCodes=005930&foreignCodes=.IXIC&cryptoCodes=BTC_KRW_UPBIT` |
| 국내 지수 시간대 시세 | `script-backed` | GET | `/api/domestic/indexSise/time?koreaIndexType=KOSPI&thistime={yyyyMMdd}&startIdx=0&pageSize=20` |

`/api/securityService/marketindex/majors` 같은 오래된 형태의 route는 2026-04-27에 404를 반환했습니다. 주요 지수에는 `/api/securityFe/api/index/majors`를 사용합니다.

## 펀드 API

2026-08-13 검색 결과의 펀드 링크가 `/domestic/fund/{fundCode}/total`로 연결되고 `total`, `performance`, `allocation` 3개 탭이 정상 렌더링되는 것을 확인했습니다. 목록 정렬·테마 enum은 여전히 충분히 검증되지 않아 노출하지 않고, 상세 화면이 실제 사용하는 아래 8개 GET만 exact-shape allowlist로 제공합니다.

| 목적 | 상태 | Method | Path / params |
| --- | --- | ---: | --- |
| 펀드 공통 상세 | `script-backed` | GET | `/api/fund/funds/{fundCode}/{left-panel\|chart-price-panel\|fund-performance\|fund-allocation}` |
| 펀드 클래스 수익률·지표 | `script-backed` | GET | `/api/fund/funds/{fundCode}/classes/returns`, `/metrics/detail?term=1y` |
| 펀드 가격·차트 | `script-backed` | GET | `/api/fund/funds/{fundCode}/prices/daily?date={yyyy-MM-dd}&size=10`, `/base-price/chart?term=3m` |
| 펀드 목록·테마 후보 | `needs-recheck` | GET | `/api/fund/funds?sort={sort}&page={page}&size={size}`, `/api/fund/funds/themes/{theme}?size={size}`. UI enum 미확정으로 스크립트 미노출 |
