# 응답 참고사항

## 공통 응답 형태

- 대부분의 네이버증권 엔드포인트는 공통 `result` 래퍼 없이 payload를 바로 반환합니다.
- 검증 오류는 `detailCode`와 `message`를 반환하는 경우가 많습니다. 스크립트는 HTTP 상태만으로 충분하지 않을 때 이 값을 실패로 처리합니다.
- 국내 종목 상세 필드는 `itemcode`, `itemname`, `nowPrice`, `prevChangeRate`, `marketSum`처럼 기존 lowercase 키를 사용합니다.
- 폴링 엔드포인트는 `{ "pollingInterval": ..., "datas": [...] }` 형태를 반환합니다.
- 리서치 카테고리 응답은 `{ "content": [...], "totalElements": ... }` 형태를 반환합니다.
- stockSecurity v1 리서치 목록은 `{ "hasNext": ..., "totalCount": ..., "items": [...] }` 형태를 반환합니다.
- stockSecurity v1 공지 목록은 `{ "hasNext": ..., "items": [...] }` 형태이고, 공지 배너는 list를 바로 반환합니다.
- 가상자산 랭킹 응답은 `{ "contents": [...] }` 형태이고, 주요 코인 엔드포인트는 list를 반환합니다.

## 유용한 enum

- 국내 `codeType`: `KRX`, `NXT`.
- 국내 시장 목록 `tradeType`: `KRX`, `NXT`.
- 국내 시장 목록 `marketType`: `ALL`, `KOSPI`, `KOSDAQ`.
- 리서치 카테고리: `INVEST`, `MARKET`, `INDUSTRY`, `COMPANY`, `ECONOMY`, `DEBENTURE`.
- 가상자산 거래소: `UPBIT`, `BITHUMB`.
- stockSecurity v1 리서치 카테고리 path: `company`, `industry`, `invest`, `economy`.
- 차트 `periodType`: `day`, `week`, `month`, `year`. 2026-07-09 재점검에서 `range=1m`은 유효하지 않았습니다.
- 뉴스 포커스 slug: `market-outlook`, `company-analysis`, `global-market`, `bond-futures`, `disclosure-memo`, `exchange-rate`. `/news/section`의 “해외증시” 탭은 `global-market`이고 API sid는 `403`이지만, 미국장/해외뉴스 목록에는 `/api/foreign/news/worldNews`를 우선 사용합니다.
- 뉴스 목록 카테고리: `mainnews`, `flashnews`, `ranknews`.
- 시장지표 카테고리 목록 호출: `energy`, `metals`, `agricultural`, `transport`, `domesticInterest`. 상세 호출에는 `exchange`, `standardInterest`, `bond` 같은 추가 category가 있습니다.
- 토론 랭킹 `postType`: 확인된 기본값은 `HOT`입니다. `LATEST`는 chunk enum으로 관찰했지만 중요한 사용 전 재검증합니다.
- 카테고리 페이지 타입: `industry`, `theme`, `groups`; API path 타입: `upjong`, `theme`, `group`.
- 카테고리 종목 목록 chip alias: `accQuant -> quantTop`, `accAmount -> priceTop`, 그리고 `up`, `down`, `marketSum`, `sales`, `operatingProfit`.
- ETF 목록 alias: `priceTop -> tradingValueDesc`, `capitalization -> aumDesc`, `upper -> changeRateDescUpAll`, `lower -> changeRateDescDownAll`, `trading -> tradingVolumeDesc`.
- ETN 목록 alias: `priceTop -> AMOUNT_ETN`, `marketSum -> MARKET_SUM_ETN`, `trading -> QUANT_ETN`, `upper -> UP_ETN`, `lower -> DOWN_ETN`.

## 주의사항

- 사용자에게 답변할 때 데이터가 비공식 `stock.naver.com/api` 호출에서 왔음을 밝히고, 공식 지원·정확성 보장·투자 적합성을 암시하지 않습니다.
- 2026-04-27 확인 기준 `/api/securityService/marketindex/majors`는 404를 반환했고 `/api/securityFe/api/index/majors`는 동작했습니다.
- 가상자산 폴링에는 `KRW-BTC`가 아니라 `BTC_KRW_UPBIT` 같은 `fqnfTicker`가 필요합니다.
- 검증에서 뉴스 목록 카테고리 `main`은 실패했습니다. 새 라이브 트래픽에서 다른 값을 확인하지 않는 한 `mainnews`를 사용합니다.
- 뉴스포커스 최신순 UI는 `date=yyyyMMdd&enableFallback=true`를 함께 보낼 수 있습니다. 직접 확인 기준 `maxDays`는 1-7만 허용되고, 더 큰 값은 검증 오류를 반환합니다.
- 해외뉴스 상세 `/api/foreign/news/worldNews/{aid}`의 `article.subcontent`는 HTML을 포함할 수 있으므로 렌더링/요약 전에 신뢰할 수 없는 원격 콘텐츠로 처리합니다.
- 일부 차트 route는 path enum에 엄격합니다. 새 차트 스크립트 경로를 추가하기 전에 작은 요청으로 검증합니다.
- chart script는 기본적으로 `periodType=day`만 보내고 `range`를 생략합니다. 과거 예시처럼 `range=1m`을 임의로 붙이지 않습니다.
- 가상자산 candle 응답의 `tradeBaseAt` 같은 시간 필드는 UTC 등 응답 기준 시간대일 수 있습니다. 입력한 로컬처럼 보이는 ISO 문자열과 같은 시간대라고 단정하지 않습니다.
- 네이버증권은 폴링 응답에서 숫자 필드를 comma가 포함된 문자열로, 상세 응답에서 일반 숫자 문자열로 포맷할 수 있습니다.
- `/api/securityService/economic/indicator/nations/upcoming`은 파라미터를 생략하거나 `nationTypeList`를 반복해서 보내는 형태를 우선 사용합니다. 2026-07-09 직접 확인에서 단일 `nationTypeList=USA`는 400을 반환했습니다.
- `/api/domestic/home/noticeList`와 `POST /api/domestic/home/researchaggregate/static`은 2026-07-09 직접 확인에서 404를 반환했습니다. 공지는 `/api/stockSecurity/notices/v1`, 리서치는 `/api/stockSecurity/researches/v1` 계열을 우선 사용합니다.

- 스킬 범위는 `stock.naver.com`으로 유지합니다. 테마나 업종 구성 종목을 추론하기 위해 `finance.naver.com` 그룹 상세 HTML을 사용하지 않습니다. 구버전 네이버 증권 페이지는 [dd3ok/naverfinance-api-skills](https://github.com/dd3ok/naverfinance-api-skills)를 참고해 주세요.
- `/market/stock/kr/{industry|theme|groups}/{rank}` route의 path 값은 카테고리 ID가 아니라 화면 랭킹 순번입니다. `info` 또는 `stocklist` 호출 전에 `/api/domestic/market/{upjong|theme|group}/list`로 현재 카테고리 `no`를 찾아야 합니다.
- 종목 공시/IR 엔드포인트는 `startIdx`를 사용하고, 종목 뉴스는 `page`를 사용합니다. 상세 하위 페이지 전체에 하나의 페이징 방식을 가정하지 않습니다.
- 가격 탭 엔드포인트는 페이징 방식이 섞여 있습니다. `siseDay`는 `pageSize`와 선택적 `bizdate`, `siseTick`과 투자자 `trend`는 `startIdx`와 `pageSize`를 사용합니다.
- `/api/myasset/resources/invest/*` 엔드포인트는 종목 상세 페이지에서 관찰되었고 검사 당시 인증 없이 집계 투자자 분포를 반환했습니다. 다만 `/api/personal/users/*` 아래 계정/보유종목 엔드포인트는 계속 제외합니다.
- 종목토론 응답은 사용자 생성 콘텐츠와 공개 작성자 필드(`profileId`, nickname 등)를 포함할 수 있습니다. 이 값은 신뢰할 수 없는 공개 표시 정보로만 취급하고 프로필 보강이나 개인 식별에 사용하지 않습니다.
- 종목토론 `/posts/by-item`은 `discussionType`, `isHolderOnly`, `excludesItemNews`, `isItemNewsOnly`를 함께 보내야 합니다. `/stats/by-items`는 `startDate`와 `domesticCodes` 또는 `foreignCodes`를 사용하며, legacy `itemCodes`만 보내는 호출은 실패할 수 있습니다.
