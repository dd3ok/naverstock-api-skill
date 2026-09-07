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
| 홈 브리핑 | `observed` | GET | `/api/securityService/home/v3/briefing`. 2026-09-07 200과 5개 원소 배열 확인 |
| AI 현재 시장 브리핑 | `script-backed` | GET | `/api/securityAi/marketBriefing/current?marketBriefing=domain` |
| AI 시장 브리핑 목록 | `script-backed` | GET | `/api/securityAi/marketBriefing?date={yyyy-MM-dd}&size=20&pageToken={token}` |
| AI 시장 브리핑 상세 | `script-backed` | GET | `/api/securityAi/marketBriefing/{briefingId}` |
| AI 시장 브리핑 v2 목록 | `script-backed` | GET | `/api/securityAi/v2/marketBriefing?date={yyyy-MM-dd}&size=20&pageToken={token}`. `home.py market-briefing-list --api-version v2` |
| AI 시장 브리핑 v2 상세 | `script-backed` | GET | `/api/securityAi/v2/marketBriefing/{briefingId}`. `home.py market-briefing-detail --api-version v2` |
| 지표 AI 브리핑 | `observed` | GET | `/api/securityAi/indicatorBriefing/current?itemCode={code}`. KOSPI 실응답 200 확인. 현재 홈 chunk 호출자의 204→`null` 분기는 실응답 미관찰이며 공통 JSON helper에 빈 응답 허용을 추가하지 않음 |

검색 결과의 최근 기록 endpoint와 `/api/personal/{guest|users}/recent/products`는 개인 상태이므로 호출하지 않습니다.

2026-09-07 [현재 홈](https://stock.naver.com/)이 로드한 [page chunk](https://ssl.pstatic.net/imgstock/fn/real/pc/_next/static/chunks/app/page-ae5fb7f70db05b3d.js)에서 브리핑 목록·상세가 v2를 사용하고, 현재 브리핑은 기존 unversioned 경로를 유지함을 확인했습니다. 날짜는 화면의 로컬 달력 날짜 `YYYY-MM-DD`, 브리핑 시각은 한국 시간 `+09:00`으로 구성합니다. `date=2026-09-04&size=2` 직접 응답은 `items` 2개, `hasMore: true`, `nextPageToken` 문자열을 반환했습니다. 항목의 `id`는 정수이고 `title`, `summary`, `detail`, `briefingDate`, `briefingHour`는 문자열입니다.

v2 첫 요청은 `pageToken`을 생략할 수 있습니다. 다음 요청은 같은 날짜·크기를 유지하고 `hasMore`가 참이며 `nextPageToken`이 있을 때 서버 값을 그대로 전달합니다. 2026-09-07 추가 실검증에서 `date=2026-09-07&size=2`의 첫 목록 `4535,4534`와 서버 cursor를 사용한 다음 목록 `4533,4532`가 모두 200을 반환했습니다. 두 묶음의 ID는 겹치지 않았고 다음 목록은 `hasMore=false`, `nextPageToken=null`로 종료했습니다. 날짜를 2026-09-06으로 바꾸고 cursor를 생략한 목록도 200이었습니다.

실제 목록 ID `4535`, `4534`의 v2 상세도 200이며 `renderMode`, `document.sections`, `visuals`, `briefingMeta`, `createdAtLabel`을 반환했습니다. `4534`의 이전·다음 ID는 각각 `4533`, `4535`였고 브라우저의 상세·이전 이동과 일치했습니다. 실행 중 새 브리핑이 생겨 현재 항목이 `4536`으로 바뀌었으므로 시간차가 있는 목록을 고정 스냅샷처럼 비교하지 않습니다. 기존 unversioned 목록·상세·현재 경로도 200을 확인했습니다. 목록·상세의 `--api-version` 기본은 호환성을 위해 `v1`이며, 이는 경로에 `/v1`을 붙인다는 뜻이 아닙니다. 현재 화면에는 `v2`를 명시하고 자동 fallback이나 원격 JSON 변환은 하지 않습니다.

해외 주목 ETF는 테마 메타데이터에서 선택한 `largeCode`, `middleCode`를 받을 수 있습니다. `home.py notable-etf --nation foreign`에도 `--large-code`, `--middle-code`를 지원하며 국내 요청에는 사용하지 않습니다. `return1Month&startIdx=0&pageSize=2`는 500이었고, 같은 조건에 실제 테마 `middleCode=0101`을 추가하면 200과 2개 행을 반환했습니다. 같은 테마의 화면 크기 `pageSize=10`도 200이었습니다. 테마를 생략하는 모든 요청이 항상 실패한다고 일반화하지 않고, 현재 화면의 테마 선택을 재현합니다. 기본 정렬과 기존 무필터 호출은 유지합니다.

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
| 기타 지표 카테고리 | `script-backed` | GET | `/api/securityService/marketindex/exchange`, `/exchangeWorld`, `/bond`, `/standardInterest` 및 각 카테고리 상세 path. 2026-09-07 bare `/exchange`, `/bond`는 404; 아래 대안과 상세 경로를 구분 |
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
| 통합 가격 | `observed` | GET | `/api/securityService/integration/price?domesticKrxCodes=005930&foreignCodes=NVDA.O&cryptoCodes=BTC_KRW_UPBIT`. 2026-09-07 해외 주식 NVDA.O는 채워짐. 지수 .IXIC는 `foreign={}`여서 별도 지수 basic API 사용 |
| 국내 지수 시간대 시세 | `script-backed` | GET | `/api/domestic/indexSise/time?koreaIndexType=KOSPI&thistime={yyyyMMdd}&startIdx=0&pageSize=20` |

`/api/securityService/marketindex/majors` 같은 오래된 형태의 route는 2026-04-27에 404를 반환했습니다. 주요 지수에는 `/api/securityFe/api/index/majors`를 사용합니다.

2026-09-07 bare `/marketindex/exchange`, `/marketindex/bond`는 404였습니다. 현재 [시장지표 page chunk](https://ssl.pstatic.net/imgstock/fn/real/pc/_next/static/chunks/app/market/marketindex/page-f14046cbecc52d8b.js)는 `/majors/exchange`, `/majors/bond`를 사용하며 두 경로는 각각 5개 요약 지표를 반환했습니다. `marketindex.py major-block --block-type exchange` 또는 `bond`는 요약 대안이고, 전체 환율에는 `exchange-list`, 개별 환율에는 `detail --category exchange --code FX_USDKRW`, 미국 채권에는 `detail --category bond --code USA`를 사용합니다. 이 명령들도 200을 확인했지만 과거 카테고리 목록과 같은 응답이라고 보장하지 않으며 자동 대체하지 않습니다.

같은 날 `market-polling --category exchange --codes FX_USDKRW`는 404였고, 현재 화면의 달러 인덱스 코드 `.DXY`는 200과 `datas`, `pollingInterval`을 반환했습니다. 코드별 지원을 구분하고 환율 폴링 계열 전체가 종료됐다고 판단하지 않습니다. 농산물 `Ccv1`, 운임 `.CCFIDXSSE`, 국내 금리 `KRCALLBOKK`는 실제 목록에서 얻은 코드로 상세를 확인했습니다. 주간 지수 차트의 `priceInfos`는 날짜별 배열을 담은 객체일 수 있으므로 모든 기간을 동일한 배열로 파싱하지 않습니다.

## 펀드 API

2026-08-13 검색 결과의 펀드 링크가 `/domestic/fund/{fundCode}/total`로 연결되고 `total`, `performance`, `allocation` 3개 탭이 정상 렌더링되는 것을 확인했습니다. 목록 정렬·테마 enum은 여전히 충분히 검증되지 않아 노출하지 않고, 상세 화면이 실제 사용하는 아래 8개 GET만 exact-shape allowlist로 제공합니다.

2026-09-07 헤더 검색에 `펀드`를 입력하고 Enter→전체 검색의 펀드 유형을 선택해 `K55301DT3764` 결과에서 종합·성과분석·자산구성 3개 탭에 실제 진입했습니다. 검색은 기존 페이지 위 결과 패널로 표시되어 브라우저 URL이 그대로였으며, 상품 클릭 후에 `/domestic/fund/...`로 이동했습니다. 이 실제 펀드 코드로 아래 8개 GET의 200 응답과 CLI JSON 출력을 확인했습니다. `classes/returns`의 `fund`는 채워졌지만 `classes=[]`였으므로 비어 있지 않은 클래스 표까지 검증한 것은 아닙니다. 일별 가격은 `prices`, 기준가 차트는 `series`, 배분은 `allocationsPortfolio.result` 등 각기 다른 경로를 사용하며 결측값을 0으로 바꾸지 않습니다.

| 목적 | 상태 | Method | Path / params |
| --- | --- | ---: | --- |
| 펀드 공통 상세 | `script-backed` | GET | `/api/fund/funds/{fundCode}/{left-panel\|chart-price-panel\|fund-performance\|fund-allocation}` |
| 펀드 클래스 수익률·지표 | `script-backed` | GET | `/api/fund/funds/{fundCode}/classes/returns`, `/metrics/detail?term=1y` |
| 펀드 가격·차트 | `script-backed` | GET | `/api/fund/funds/{fundCode}/prices/daily?date={yyyy-MM-dd}&size=10`, `/base-price/chart?term=3m` |
| 펀드 목록·테마 후보 | `needs-recheck` | GET | `/api/fund/funds?sort={sort}&page={page}&size={size}`, `/api/fund/funds/themes/{theme}?size={size}`. UI enum 미확정으로 스크립트 미노출 |

실제 펀드 일별 가격의 첫 두 거래일 `2026-09-04`, `2026-09-03`에서 현재 [펀드 화면 코드](https://ssl.pstatic.net/imgstock/fn/real/pc/_next/static/chunks/app/domestic/fund/%5Bcode%5D/total/page-3048e128e644bdc4.js)대로 마지막 `tradeDate`에서 달력 하루를 빼 `date=2026-09-02&size=2`를 요청했습니다. 응답은 200이며 `09-02`, `09-01`로 전진했습니다. 다른 API의 포함·제외 날짜 경계에 이 계산을 그대로 적용하지 않습니다.

같은 날 후속 검색 결과의 `K55301B35070`은 `classes/returns`에서 7개 클래스를 반환했습니다. [성과분석 화면](https://stock.naver.com/domestic/fund/K55301B35070/performance)의 ‘다른 클래스 보기’ 7개 옵션과 표의 코드 링크도 확인했습니다. `K55105B00244`, `K55105B24954`는 정상 200의 빈 classes였으므로 이제 빈/비어 있지 않은 분기를 모두 관찰했습니다. 모든 펀드의 수익률이나 목록·테마 후보의 enum이 검증된 것은 아닙니다. [현재 제한과 처리](known-limitations.md)를 함께 확인하세요.
