# 가상자산 API

상태 라벨, page route, 전송, 식별자와 제외 기준은 [공통 API 인덱스](api-catalog.md)를 따릅니다.

| 목적 | 상태 | Method | Path / params |
| --- | --- | ---: | --- |
| 랭킹 목록 | `script-backed` | GET | `/api/coin/rank/{market}?sortType={top\|up\|down\|marketValue}&page=1&pageSize=100` |
| 주요 코인 | `script-backed` | GET | `/api/coin/rank/{market}/majors` |
| 거래소별 코인 가격 | `script-backed` | GET | `/api/coin/price/{market}/{ticker}` |
| 거래소 비교용 코인 가격 | `script-backed` | GET | `/api/coin/price/{ticker}?excludeExchange={market}` |
| 기간별 등락률 | `script-backed` | GET | `/api/coin/priceChange/{market}/{ticker}`. 2026-09-07 UPBIT·BITHUMB의 BTC 직접 요청은 `1d`부터 `10y`까지 `period`, `changeRate`, `changeValue`, `baseDate`, `basePrice` 9개 행을 반환 |
| 코인 차트 메타 payload | `observed` | GET | `/api/securityFe/api/fchart/crypto/{market}/{ticker}`. 2026-09-07 UPBIT/BTC는 HTTP 200으로 `chartNationType`, `chartInfoType`, `itemCode`, `fqnfTicker` 등이 있는 메타데이터 객체를 반환 |
| 폴링 가격 | `script-backed` | GET | `/api/polling/coin/price?fqnfTickers=BTC_KRW_UPBIT` |
| 분봉 캔들 | `script-backed` | GET | `/api/coin/candle/{market}/KRW/{ticker}/minutes/{unit}/marketInfo?from={iso}&to={iso}` |
| 기간 캔들 | `script-backed` | GET | `/api/coin/candle/{market}/KRW/{ticker}/{year\|weeks\|quarter\|months\|days}?from={iso}&to={iso}` |
| 상세 분봉 캔들 | `script-backed` | GET | `/api/coin/candle/{market}/KRW/{ticker}/minutes/{unit}?from={iso}&to={iso}` |
| 국내 지수 비교 차트 | `script-backed` | GET | `/api/securityService/chart/compare/domestic/index/{code}/{day\|week}?startDateTime={yyyyMMddHHmmss}&endDateTime={yyyyMMddHHmmss}` |
| 해외 지수/선물 비교 차트 | `script-backed` | GET | `/api/securityService/chart/compare/foreign/{index\|futures}/{code}/{day\|week}?startDateTime={yyyyMMddHHmmss}&endDateTime={yyyyMMddHHmmss}` |
| 해외 지수/선물 분봉 비교 차트 | `script-backed` | GET | `/api/securityService/chart/foreign/{INDEX\|FUTURES}/{NASDAQ\|NYSE\|COMEX\|ICE_US}/{code}/interval/{1\|5}?startDateTime={yyyyMMddHHmmss}&endDateTime={yyyyMMddHHmmss}&utc=true` |
| 글로벌 뉴스 | `script-backed` | GET | `/api/coin/globalNews/{ticker}?pageSize=20&offsetTimestamp={timestamp}` |
| 시장 업데이트 | `script-backed` | GET | `/api/coin/marketUpdates/{ticker}?pageSize=20&offsetTimestamp={timestamp}` |
| 전체 시장 업데이트 | `script-backed` | GET | `/api/coin/marketUpdates?pageSize=9&offsetTimestamp={timestamp}` |
| 전문가 콘텐츠 | `script-backed` | GET | `/api/coin/expertContents?pageSize=10&offsetTimestamp={timestamp}` |
| 업데이트·전문가 콘텐츠 상세 | `script-backed` | GET | `/api/coin/marketUpdates/detail/{id}`, `/api/coin/expertContents/{id}` |
| 종목별 전문가 콘텐츠 | `script-backed` | GET | `/api/coin/{ticker}/expertContents?pageSize=10&offsetTimestamp={cursor}` |
| 코인 프로필 | `script-backed` | GET | `/api/coin/profile/{ticker}` |
| 카테고리 랭킹 | `script-backed` | GET | `/api/coin/categories/ranking?exchangeType=UPBIT&page=1&pageSize=50`. 2026-08-04 섹터 화면은 첫 진입에서 page 1·2·3을 연속 선조회했으므로 호출량을 화면과 동일하게 무제한 재현하지 않음 |
| 카테고리 상세·종목 카테고리 | `script-backed` | GET | `/api/coin/categories/{categoryId}?exchangeType=UPBIT`, `/api/coin/{ticker}/categories?exchangeType=UPBIT` |
| 코인 ETF 노출 | `script-backed` | GET | `/api/coin/etf/{ticker}?sortType=holdingWeight&size=20&page=1` 또는 `pageToken` |
| 여러 코인 가격 | `script-backed` | GET | `/api/coin/prices?fqnfTickers=BTC_KRW_UPBIT&fqnfTickers=ETH_KRW_UPBIT` |
| 글로벌 시장 동향 | `script-backed` | GET | `/api/coin/globalMarketTrend` |
| CMC 커뮤니티 feed | `script-backed` | GET | `/api/coin/globalCommunity/cmc/latest/{ticker}?pageSize=30&offsetPostTime={lastPostTime}`. 응답 `items`, `hasNext`; 개인정보 필드는 sanitizer로 제거 |
| 코인 매크로 뉴스 | `script-backed` | GET | `/api/securityFe/api/news/coinmacro?page=1&pageSize=10` |
| AI 코인 브리핑 | `script-backed` | GET | `/api/securityAi/coinBriefing/current?exchangeType=UPBIT&nfTicker=BTC` |
| AI 코인 브리핑 이력·상세 | `script-backed` | GET | `/api/securityAi/coinBriefings?exchangeType=UPBIT&nfTicker=BTC&size=20&date={yyyy-MM-dd}&pageToken={token}`, `/api/securityAi/coinBriefing/{id}` |

`UPBIT` 또는 `BITHUMB`을 대문자로 사용합니다. 폴링 엔드포인트는 `BTC_KRW_UPBIT` 같은 `fqnfTicker` 값을 받고, 뉴스/업데이트/프로필 엔드포인트는 `BTC` 같은 plain ticker를 받습니다. 직접 확인에서 일반 `KRW-BTC`는 빈 list를 반환했습니다.

## 직접 확인한 응답 구조와 후속 조회

2026-09-07 소량 직접 요청에서 UPBIT·BITHUMB의 가격·랭킹·캔들·카테고리·AI 브리핑과 BTC의 뉴스·시장 업데이트·전문가 콘텐츠·ETF 노출을 확인했습니다. 목록에서 얻은 실제 ID로 시장 업데이트·전문가 콘텐츠·카테고리·AI 브리핑 상세도 HTTP 200을 확인했습니다. 아래는 해당 표본의 구조이며 모든 종목·날짜 조합의 응답을 보증하지 않습니다.

| 응답 종류 | 행 위치와 확인 기준 |
| --- | --- |
| 코인·카테고리 랭킹 | `contents[]`. `page`, `pageSize`와 함께 확인하며 카테고리 랭킹에는 `hasNext`가 있음 |
| 뉴스·시장 업데이트·전문가 콘텐츠 | `items[]`. 전체 건수와 실제 반환 행 수를 구분 |
| 카테고리 상세·종목 카테고리 | 상세의 `coins[]`, 종목 응답의 `categories[]`; 최상위 목록으로 가정하지 않음 |
| 분봉 `marketInfo` | `priceInfos[]`와 장 시작 정보. 상세 분봉·기간 캔들은 최상위 list |
| 해외 분봉 비교 차트 | `candleList[]`와 시장 메타데이터. 빈 list와 응답 객체의 필드 수를 혼동하지 않음 |
| ETF 노출·AI 브리핑 이력 | `items[]`, `hasMore`, `nextPageToken` |

해외 분봉 비교는 현재 공개 메타데이터의 유형·거래소·코드 조합을 유지합니다. 직접 확인한 조합은 `INDEX/NASDAQ/.IXIC`, `INDEX/NYSE/.INX`, `FUTURES/COMEX/GCcv1`, `INDEX/ICE_US/.DXY`입니다. 특히 달러 지수 `.DXY`를 `FUTURES`로 추정하지 않습니다.

UPBIT의 코인 랭킹·카테고리 랭킹과 코인 매크로 뉴스는 같은 크기 2로 page 2를 요청해 첫 페이지와 다른 종목·카테고리·기사 ID를 확인했습니다. UPBIT/BTC의 AI 브리핑 이력도 반환된 `nextPageToken`으로 다음 2행을 조회해 더 이른 브리핑 시각과 다른 ID를 확인했습니다. 이 한 번의 후속 조회를 근거로 전체 이력의 완전성이나 변동 중인 랭킹의 무중복을 보증하지 않습니다.

ETF 노출은 첫 페이지의 `nextPageToken`을 같은 정렬·크기의 `pageToken`으로 보내 다음 ETF 2행이 반환되는 것을 확인했습니다. 이 값은 공개 ETF 목록의 최상위 페이지 커서이며 로그인·세션 토큰이 아닙니다. 응답의 정확한 `nextPageToken`만 사용하고 임의의 `token` 필드를 수집하거나 해석하지 않습니다. CMC 커뮤니티도 마지막 `items[].postTime`을 `offsetPostTime`으로 보낸 다음 페이지에서 다른 게시글 ID를 확인했습니다. 원문 개인정보 필드는 기존 sanitizer로 제거합니다.

현재 공개 화면 소스는 전체·종목별 시장 업데이트의 마지막 `items[].updateTimestamp`, 전체·종목별 전문가 콘텐츠의 마지막 `items[].publishedAt`을 변환 없이 다음 `offsetTimestamp`에 전달합니다. 이 네 목록은 전체 또는 BTC·크기 2 조건을 유지한 실제 후속 요청에서 더 이른 시각과 다른 콘텐츠 ID를 반환했습니다. 첫 요청은 커서를 생략하고, 비어 있지 않은 응답에서 확인한 값만 다음 요청에 사용합니다. 확인용 기록에는 공개 콘텐츠 ID·페이지 날짜와 응답 구조만 남기고 코인 프로필의 `persons`나 콘텐츠 작성자 정보를 복사하지 않습니다.

글로벌 뉴스는 화면 호출자의 커서 선택 코드를 확인하지 못해 별도의 파라미터 실험으로 구분했습니다. BTC·`pageSize=2` 첫 응답의 마지막 `releasedAt=2026-09-07T09:58:08`을 그대로 `offsetTimestamp`에 넣은 요청도 200이었고, 다음 두 기사의 시각은 `09:43:12`, `09:06:29`로 더 이전이며 첫 묶음과 겹치지 않았습니다. 이는 이 표본의 실제 날짜 경계 동작이며 브라우저 트래픽을 캡처한 근거는 아닙니다. 다른 콘텐츠의 `publishedAt`이나 `updateTimestamp`를 이 뉴스 필드와 혼용하지 않습니다.
