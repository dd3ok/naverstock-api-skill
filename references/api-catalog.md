# NaverStock Web API 카탈로그

기준 관찰일: 2026-05-05, 부분 재점검: 2026-07-09, 전범위 재감사: 2026-07-17, 전체 정적 재점검 및 변경 경로 실호출: 2026-07-20, 브라우저·탭·페이징 재점검: 2026-07-21, route·transport·chunk 재점검: 2026-08-04, 전체 링크·탭·페이징 재감사: 2026-08-13
관찰 출처: 로그인하지 않은 공개 `https://stock.naver.com/` 페이지와 Next.js chunk  
기본 호스트: `https://stock.naver.com`

네이버증권 내부 API는 미문서화 상태이며 예고 없이 바뀔 수 있습니다. 이 카탈로그는 정답이 아니라 관찰 기록입니다. 운영에 의존하기 전에 현재 공개 페이지 트래픽, Next.js chunk, 소량 read-only 요청으로 다시 확인합니다.

이 카탈로그에는 `stock.naver.com` 페이지 또는 상대 `stock.naver.com/api/...` 호출에서 확인되는 엔드포인트만 추가합니다. 제한된 WiseReport v3와 레거시 조건검색은 별도 [외부 공개 소스 문서](external-sources.md)에서 관리합니다.

## 목차

- [상태 라벨](#상태-라벨)
- [페이지 점검 메모](#페이지-점검-메모)
- [전송 방식](#전송-방식)
- [식별자 규칙](#식별자-규칙)
- [도메인별 API 상세](#도메인별-api-상세)
- [제외 계열](#제외-계열)

## 상태 라벨

| 상태 | 의미 |
| --- | --- |
| `script-backed` | 번들 스크립트가 이 엔드포인트 계열을 호출합니다. |
| `observed` | 공개 페이지 트래픽 또는 정적 chunk에서 관찰했지만 스크립트로 감싸지 않았습니다. |
| `needs-recheck` | route, enum, 인증 민감도, 페이징 형태를 새로 검증해야 합니다. |
| `excluded` | 읽기 전용 주식/시장 정보 범위 밖입니다. 호출하지 않습니다. |

## 페이지 점검 메모

2026-04-27 재점검에서는 `https://stock.naver.com/` 루트 HTML과 루트가 로드하는 Next.js chunk 58개에서 route/API 문자열을 추출하고, 후보 route를 작은 직접 요청으로 확인했습니다. 2026-07-20에는 국내 종목, 국내 시장, ETF, 투자자 동향, 시장지표, 가상자산, 뉴스, 리서치, 토론의 공개 page route 10개와 중복 제거한 chunk 123개를 정적으로 대조했습니다. 2026-07-21에는 로그인하지 않은 in-app 브라우저에서 국내 주식 20개·ETF 11개·ETN 8개 목록 탭, 종목 상세 17개 하위 탭, 뉴스포커스 5개 탭, 글로벌 지표 8개 탭과 주요 부모 route를 직접 이동해 hydration 후 화면·redirect·빈 상태를 확인하고, 페이징 API를 `startIdx`/`page` 구간으로 소량 호출했습니다. `robots.txt`는 `Disallow: /`이고 sitemap은 404라서 대량 크롤링은 하지 않습니다.

2026-08-04에는 로그인하지 않은 in-app 브라우저에서 홈, 국내·미국·글로벌, 가상자산, 시장지표, 뉴스, 리서치, 토론, 국내 종목·지수와 해외 종목의 현재 메뉴 route 및 하위 탭을 다시 이동했습니다. 화면이 실제로 로드한 중복 제거 Next.js/공유 script 227개를 정적 검사해 API literal 236개와 WebSocket/SSE 관련 코드를 대조했습니다. 공개 시세·시장 데이터에서는 REST polling만 관찰됐고, WebSocket은 로그인 보유종목 refresh 모듈에서만 확인됐습니다. 공통 Fender bundle의 범용 SSE client는 구체적인 증권 데이터 stream URL을 노출하지 않았습니다.

2026-08-13에는 홈과 모든 주요 상단 메뉴에서 연결되는 국내·해외 주식, 지수, ETF, 업종·테마·그룹사, 시장지표, 가상자산, 뉴스, 리서치, 공지, 토론의 링크·탭·상세·더보기/무한스크롤 요청을 다시 대조했습니다. 종목 리서치와 리서치 카테고리의 `index`는 0부터 1씩 증가하는 페이지 index이며, 종목 뉴스는 1-based `page`, 종목 공시·IR과 국내 지수 시간대 시세는 0-based `startIdx`를 사용합니다.

목록 화면의 요청 크기와 저용량 CLI 기본값은 구분합니다. 국내·해외 주식, ETF, ETN의 전체 목록 UI는 현재 주로 100건을 한 번에 요청하지만, 범용 목록 helper는 자동 대량 조회를 피하려고 기본 20건을 유지합니다. 화면 요청을 정확히 재현해야 할 때만 `--page-size 100` 또는 `--size 100`을 명시합니다. 반면 화면 전용 흐름으로 추가한 명령은 확인된 UI 기본값을 그대로 사용합니다.

확인된 주요 페이지 route:

| Route | 결과 | 메모 |
| --- | --- | --- |
| `/market` | 307 | 2026-07-17 무쿠키 직접 요청은 `/market/stock/kr/`로 이동했고, 일부 브라우저 세션에서는 `/market/stock/usa`도 관찰됨. 상태 의존 기본값 대신 목적 route를 직접 지정 |
| `/market/stock` | 307 | `/market/stock/kr`로 이동 |
| `/market/stock/kr` | 200 | 국내 주식 메인 |
| `/market/stock/kr/stocklist` | 307 | `/market/stock/kr/stocklist/priceTop`으로 이동 |
| `/market/stock/kr/stocklist/{capitalization\|priceTop\|top\|upper\|flat\|lower\|trading\|quantHigh\|quantLow\|high52week\|low52week\|dividend\|new\|konex\|foreignHold\|management\|tradingHalt\|investmentAlert\|investmentWarning\|investmentRisk}` | 200 | 기존 목록 탭 route. 표는 기본 100행을 렌더링하고 `목록의 마지막입니다` sentinel로 끝나며, API는 `startIdx`·`pageSize`를 사용 |
| `/market/stock/kr/{dividend\|foreignHold\|new\|konex\|management}` | 200/redirect | 2026-08-04 현재 상단 메뉴 route. 배당은 `/dividend/revenue`, 관리종목은 `/management` 계열을 사용 |
| `/market/stock/kr/dividend/{revenue\|order}` | 200 | 수익률순은 `dividendRate`, 배당금순은 `dividend` query를 사용 |
| `/market/stock/kr/management/{tradingHalt\|investmentAlert\|investmentWarning\|investmentRisk}` | 200 | 관리·거래정지·투자주의/경고/위험 현재 route |
| `/market/stock/kr/{industry\|theme\|groups}` | 307 | 각각 `/1`로 이동 |
| `/market/stock/kr/{industry\|theme\|groups}/{rank}?no={actualId}` | 200 | path 숫자는 현재 랭킹 순번이며 query/API category `no`와 다를 수 있음 |
| `/market/stock/kr/etf` | 307 | `/market/stock/kr/etf/priceTop?etfListEntry=1`로 이동 |
| `/market/stock/kr/etf/{capitalization\|priceTop\|return1m\|return3m\|return6m\|upper\|lower\|trading\|quantHigh\|quantLow\|new}` | 200 | 현재 국내 ETF UI에서 확인한 11개 목록 탭 |
| `/market/stock/kr/etn` | 307 | `/market/stock/kr/etn/priceTop?etnListEntry=1`로 이동 |
| `/market/stock/kr/etn/{capitalization\|priceTop\|upper\|lower\|trading\|quantHigh\|quantLow\|new}` | 200 | 현재 국내 ETN UI에서 확인한 8개 목록 탭 |
| `/market/stock/kr/ipo`, `/market/stock/kr/ipo/recent` | 200 | 각각 상장 진행 중(타입 생략), 상장 완료(`LISTING`) 탭. `/market/stock/kr/ipo/progress`는 404 |
| `/market/stock/kr/deposit` | 200 | 예탁금 페이지 |
| `/market/stock/kr/trend/{foreigner\|organization\|program\|trader}` | 200 | 투자자 동향 페이지 |
| `/market/crypto` | 200 | 가상자산 페이지. `/crypto`는 404 |
| `/market/crypto/ranking/top?exchangeType={UPBIT\|BITHUMB}` | 200 | 거래소별 가상자산 랭킹 탭 |
| `/market/crypto/news/{domesticNews\|expertContent\|marketUpdates}` | 200 | 가상자산 국내뉴스·전문가·시장 업데이트 탭 |
| `/market/crypto/news/{marketUpdates\|expertContent}/posts/{id}` | 200 | 가상자산 전역 콘텐츠 상세 |
| `/market/crypto/sector/{UPBIT\|BITHUMB}?id={categoryId}` | 200 | 거래소별 가상자산 섹터 상세. category API와 구성 코인 목록을 사용 |
| `/crypto/{UPBIT\|BITHUMB}/{ticker}` | 307 | `/price`로 이동. 현재 화면 링크는 거래소를 대문자로 사용 |
| `/crypto/{UPBIT\|BITHUMB}/{ticker}/price` | 200 | 코인 상세 가격 화면. 프로필·기간/분봉 candle API를 사용 |
| `/crypto/{UPBIT\|BITHUMB}/{ticker}/discussion/{Npay\|CMC}` | 200 | 네이버 공개 토론과 CMC 미러 feed. Npay의 `filter`가 뉴스 포함 방식을 바꿈 |
| `/crypto/{UPBIT\|BITHUMB}/{ticker}/news` | 307 | `/news/marketUpdates`로 이동 |
| `/crypto/{UPBIT\|BITHUMB}/{ticker}/news/{marketUpdates\|domesticNews\|expertContent}` | 200 | 코인 뉴스 하위 탭 |
| `/crypto/{UPBIT\|BITHUMB}/{ticker}/news/{marketUpdates\|expertContent}/posts/{id}` | 200 | 코인 콘텐츠 상세 |
| `/market/marketindex` | 200 | 현재 시장지표 홈. 과거 `/major/` redirect를 기본 동작으로 가정하지 않음 |
| `/market/marketindex/{major\|energy\|metals\|agricultural\|transport}` | 200 | 주요 시장지표 탭 |
| `/market/marketindex/exchangeRate/{exchange\|exchangeWorld}` | 200 | 국내·세계 환율 탭. `/exchangeRate`는 `exchange`로 이동 |
| `/market/marketindex/bondAndInterest/{bond\|domesticInterest\|standardInterest}` | 200 | 채권/금리 탭 |
| `/market/stock/global`, `/market/stock/usa` | 200 | 해외 주식 메인 |
| `/market/stock/usa/stocklist` | 307 | `/market/stock/usa/stocklist/priceTop`으로 이동 |
| `/market/stock/usa/stocklist/{top\|priceTop\|up\|down\|marketValue}` | 200 | 미국 종목 정렬 탭. 배당은 별도 `/market/stock/usa/dividend` |
| `/market/stock/usa/etf` | 307 | `/market/stock/usa/etf/priceTop`으로 이동 |
| `/market/stock/usa/industry/{rank}?no={industryCode}` | 200 | path는 랭킹 순번, `no`는 실제 업종 ID |
| `/market/stock/global/{chn\|hkg\|jpn\|vnm}/{marketValue\|priceTop\|up\|down\|top\|dividend}` | 200 | 해외 국가별 목록 |
| `/market/stock/global/industry/{chn\|hkg\|jpn\|vnm}` | 307 | 현재 첫 industry code로 이동 |
| `/market/stock/global/industry/{chn\|hkg\|jpn\|vnm}/{industryCode}` | 200 | 국가별 업종 상세와 구성 종목 |
| `/domestic/stock/{itemCode}` | 307 | `/price`로 이동 |
| `/domestic/stock/{itemCode}/{price\|news\|notice\|ir\|discussion\|research\|shortTrade\|investmentinfo}` | 200 | 종목 상세 하위 페이지 |
| `/domestic/stock/{itemCode}/{notice\|ir\|research}/{articleId}` | 200 | 공시·IR·종목 리서치 상세. IR ID는 숫자 외 `BOARD...`, `PLAN...`도 사용 |
| `/domestic/index/{indexCode}/price` | 200 | 국내 지수 상세. 기본·장중·일별 시세와 차트 메타를 로드 |
| `/domestic/stock/{itemCode}/info` | 307 | `/info/company`로 이동 |
| `/domestic/stock/{itemCode}/info/{company\|overview\|financial\|investment\|consensus\|industry\|sector\|share\|esg}` | 200 | 종목 정보 탭 page route |
| `/domestic/stock/{itemCode}/info/summary` | 200 | ETF 정보 요약 route |
| `/worldstock/stock/{reutersCode}/{price\|discussion\|finance\|worldnews\|investmentinfo}` | 200/redirect | 해외 종목 탭. `finance`는 `/finance/overview`로 이동 |
| `/worldstock/stock/{reutersCode}/finance/{overview\|primary\|ratios\|balance\|income\|cash}` | 200 | 해외 종목 재무 하위 탭 |
| `/worldstock/etf/{code}/{price\|discussion\|finance\|investmentinfo}` | 200/redirect | 해외 ETF 탭 |
| `/worldstock/index/{code}/{price\|discussion}` | 200 | 해외 지수 탭 |
| `/domestic/fund/{fundCode}/{total\|performance\|allocation}` | 200 | 검색 결과가 연결하는 공개 펀드 상세 3개 탭 |
| `/news`, `/news/{flashnews\|mainnews\|ranknews\|section\|worldnews\|marketNotice}`, `/notice` | 200 | 뉴스/뉴스포커스/해외뉴스/공시/서비스 공지 페이지 |
| `/news/{worldnews\|marketNotice}/{articleId}`, `/notice/{noticeId}` | 200 | 해외뉴스·시장 공시·서비스 공지 상세 |
| `/research`, `/research/{daily\|company\|industry\|invest\|economy\|debenture}` | 200 | 리서치 홈과 카테고리 페이지 |
| `/research/{daily\|company\|industry\|invest\|economy\|debenture}/{researchId}` | 200 | 리서치 상세. `daily` 화면의 API type은 `market` |
| `/research/firm/{brokerId}` | 200 | 리서치 홈의 발행사 링크. 발행사에 따라 하나 이상의 `brokerCodes`를 반복해 `market` 목록을 조회 |
| `/discussion`, `/discussion/feed/{all\|hot\|marketindex\|my}` | 200 | `/discussion/feed`는 `/all`로 이동. `my`는 로그인 개인 영역이라 제외 |

`/domestic/stock/{itemCode}/shortTrade`는 `stock.naver.com` JSON API가 아니라 `https://data.krx.co.kr/comm/srt/srtLoader/index.cmd?screenId=MDCSTAT300&isuCd={itemCode}` iframe을 렌더링합니다. 이 외부 KRX 화면을 `stock.naver.com/api/...` 엔드포인트처럼 취급하지 않습니다.

확인했지만 스킬 범위에서 제외하거나 404였던 route:

- `/market/domestic`, `/market/domestic/stock`, `/market/domestic/etf`, `/market/domestic/etn`, `/market/domestic/ipo`는 404였습니다.
- `/marketindex`는 404였고 `/market/marketindex`를 사용합니다.
- `/my/favorite`는 200이지만 개인/관심종목 페이지라 제외합니다.
- `/market/my/order`, `/my/timeline`, `/my/subscriptions`는 404였습니다.

## 전송 방식

| 방식 | 상태 | 관찰 결과 |
| --- | --- | --- |
| REST polling | `script-backed` | 공개 현재가·지수·원자재·가상자산 갱신은 `/api/polling/domestic/*`, `/api/polling/worldstock/*`, `/api/polling/marketindex/*`, `/api/polling/coin/price`를 사용합니다. 응답의 `pollingInterval` 이상을 다음 호출 전 최소 대기 간격으로 사용해 호출 빈도를 제한합니다. |
| Socket.IO WebSocket | `excluded` | 보유종목 refresh chunk가 `GET /api/personal/users/holding/refresh/session-io`로 세션 URL을 받고 `http(s)`를 `ws(s)`로 바꿔 `transports: ["websocket"]`로 연결합니다. `nchat:channel`에 `user_{nidNo}`를 subscribe하고 `holding_stock`, `FEStockConnected` 이벤트를 받지만 로그인·개인 보유종목 범위라 연결·기록·재현하지 않습니다. 트리거 POST는 `/api/personal/users/holding/stocks/refresh`입니다. |
| SSE | `excluded` | 공통 Fender script에 `text/event-stream`을 처리하는 범용 fetch client가 있으나, 로그인하지 않은 증권 페이지 네트워크와 stock chunk에서 구체적인 공개 증권 SSE URL은 확인되지 않았습니다. 공유 bundle의 `/api/chat` 계열도 증권 데이터 API로 분류하지 않습니다. |

따라서 공개 시세용 `ws://`/`wss://` 주소를 추정하거나 Socket.IO 세션 URL을 하드코딩하지 않습니다. transport 문자열이 bundle에 있다는 사실만으로 공개 데이터 API라고 판단하지 않습니다.

## 식별자 규칙

| 식별자 | 예시 | 의미 |
| --- | --- | --- |
| `itemCode` | `005930` | 6자리 국내 종목 코드. |
| `codeType` | `KRX`, `NXT` | 국내 종목 상세 거래 route. |
| `itemCodes` | `005930,000660` 또는 반복 query | 국내 종목/지수 코드 목록. 폴링은 comma 구분 문자열을, 리서치 v2는 `itemCodes=005930&itemCodes=000660` 같은 반복 query를 사용합니다. |
| `reutersCode` | `KOSPI`, `GCcv1` | 시장지표 API에서 쓰는 지수, 선물, 지표 코드. |
| `fqnfTicker` | `BTC_KRW_UPBIT` | 폴링 엔드포인트에서 쓰는 가상자산 ticker. |
| `market` | `UPBIT`, `BITHUMB` | 가상자산 거래소 enum. 대문자가 필요합니다. |

## 도메인별 API 상세

| 작업 범위 | 상세 문서 |
| --- | --- |
| 국내 종목·시장 랭킹·업종/테마·ETF/ETN·투자자 동향 | [국내 주식 API](api-domestic.md) |
| 해외 종목·업종·ETF·지수·선물 | [해외 주식 API](api-foreign.md) |
| 홈·통합 검색·시장 지수/지표·펀드 | [홈·시장 지표·펀드 API](api-home-market-fund.md) |
| 가상자산 시세·차트·콘텐츠·AI 브리핑 | [가상자산 API](api-crypto.md) |
| 서비스 공지·뉴스·리서치·종목토론 | [콘텐츠 API](api-content.md) |

해당 작업의 상세 문서만 읽고, 상태·페이지 route·전송·식별자·제외 기준은 이 인덱스를 단일 기준으로 사용합니다.

## 제외 계열

| 계열 | 상태 | 이유 |
| --- | --- | --- |
| `/api/auth/*` | `excluded` | 로그인/인증. |
| `/api/personal/users/holding/*` | `excluded` | 계좌 보유종목과 refresh 워크플로. |
| 보유종목 Socket.IO session URL과 channel/event | `excluded` | `/api/personal/users/holding/refresh/session-io`, `nchat:channel`, `user_{nidNo}`, `holding_stock`, `FEStockConnected`는 로그인·개인 보유종목 refresh 전용입니다. |
| 공통 Fender SSE/Chat code | `excluded` | 공유 script의 범용 `text/event-stream` client와 `/api/chat`·`/api/chats` 문자열은 공개 증권 데이터 endpoint로 관찰되지 않았습니다. |
| `/api/personal/users/favorite/*` | `excluded` | 사용자별 관심종목과 그룹. |
| `/api/personal/users/notification*` | `excluded` | 사용자 알림 설정/메시지. |
| `/api/community/profile/users/*` mutation-like routes | `excluded` | 사용자 프로필과 이미지 워크플로. |
| `/api/domestic/home/recommend-aggregate` | `excluded` | 현재 웹 번들은 credentials 포함 POST와 연령/자산 범위 개인화 필드를 사용합니다. |
| `/api/autocomplete/search/recent`, `/api/personal/*/recent/products` | `excluded` | 최근 검색·최근 상품 개인 상태. |
| `/api/stockSecurity/researches/v2/{type}/{id}/view` | `excluded` | GET이지만 조회수·최근 열람 상태를 기록할 가능성이 있어 호출하지 않음. 안전한 core detail 사용 |
| allowlist 밖의 `https://finance.naver.com/*`와 WiseReport URL | `excluded` | 외부 소스는 [external-sources.md](external-sources.md)의 고정 host/path/query만 허용합니다. 전체 레거시 비교는 [dd3ok/naverfinance-api-skill](https://github.com/dd3ok/naverfinance-api-skill)을 참고합니다. |
| 텔레메트리, 광고, 정적 chunk, 폰트, 이미지 | `excluded` | 주식 정보 API가 아닙니다. |
