# 가상자산 API

상태 라벨, page route, 전송, 식별자와 제외 기준은 [공통 API 인덱스](api-catalog.md)를 따릅니다.

| 목적 | 상태 | Method | Path / params |
| --- | --- | ---: | --- |
| 랭킹 목록 | `script-backed` | GET | `/api/coin/rank/{market}?sortType={top\|up\|down\|marketValue}&page=1&pageSize=100` |
| 주요 코인 | `script-backed` | GET | `/api/coin/rank/{market}/majors` |
| 거래소별 코인 가격 | `script-backed` | GET | `/api/coin/price/{market}/{ticker}` |
| 거래소 비교용 코인 가격 | `script-backed` | GET | `/api/coin/price/{ticker}?excludeExchange={market}` |
| 기간별 등락률 | `script-backed` | GET | `/api/coin/priceChange/{market}/{ticker}`. 2026-08-04 직접 요청은 `1d`부터 `10y`까지 `period`, `changeRate`, `changeValue`, `baseDate`, `basePrice` 9개 행을 반환 |
| 코인 차트 메타 payload | `observed` | GET | `/api/securityFe/api/fchart/crypto/{market}/{ticker}` |
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
