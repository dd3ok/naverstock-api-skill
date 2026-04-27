# 응답 참고사항

## 공통 응답 형태

- 대부분의 네이버증권 엔드포인트는 공통 `result` 래퍼 없이 payload를 바로 반환한다.
- 검증 오류는 `detailCode`와 `message`를 반환하는 경우가 많다. 스크립트는 HTTP 상태만으로 충분하지 않을 때 이 값을 실패로 처리한다.
- 국내 종목 상세 필드는 `itemcode`, `itemname`, `nowPrice`, `prevChangeRate`, `marketSum`처럼 기존 lowercase 키를 사용한다.
- 폴링 엔드포인트는 `{ "pollingInterval": ..., "datas": [...] }` 형태를 반환한다.
- 리서치 카테고리 응답은 `{ "content": [...], "totalElements": ... }` 형태를 반환한다.
- 가상자산 랭킹 응답은 `{ "contents": [...] }` 형태이고, 주요 코인 엔드포인트는 list를 반환한다.

## 유용한 enum

- 국내 `codeType`: `KRX`, `NXT`.
- 국내 시장 목록 `tradeType`: `KRX`, `NXT`.
- 국내 시장 목록 `marketType`: `ALL`, `KOSPI`, `KOSDAQ`.
- 리서치 카테고리: `INVEST`, `MARKET`, `INDUSTRY`, `COMPANY`, `ECONOMY`, `DEBENTURE`.
- 가상자산 거래소: `UPBIT`, `BITHUMB`.
- 뉴스 포커스 slug: `market-outlook`, `company-analysis`, `global-market`, `bond-futures`, `disclosure-memo`, `exchange-rate`.
- 뉴스 목록 카테고리: `mainnews`, `flashnews`, `ranknews`.
- 카테고리 페이지 타입: `industry`, `theme`, `groups`; API path 타입: `upjong`, `theme`, `group`.
- 카테고리 종목 목록 chip alias: `accQuant -> quantTop`, `accAmount -> priceTop`, 그리고 `up`, `down`, `marketSum`, `sales`, `operatingProfit`.
- ETF 목록 alias: `priceTop -> tradingValueDesc`, `capitalization -> aumDesc`, `upper -> changeRateDescUpAll`, `lower -> changeRateDescDownAll`, `trading -> tradingVolumeDesc`.
- ETN 목록 alias: `priceTop -> AMOUNT_ETN`, `marketSum -> MARKET_SUM_ETN`, `trading -> QUANT_ETN`, `upper -> UP_ETN`, `lower -> DOWN_ETN`.

## 주의사항

- 사용자에게 답변할 때 데이터가 비공식 `stock.naver.com/api` 호출에서 왔음을 밝히고, 공식 지원·정확성 보장·투자 적합성을 암시하지 않는다.
- 2026-04-27 확인 기준 `/api/securityService/marketindex/majors`는 404를 반환했고 `/api/securityFe/api/index/majors`는 동작했다.
- 가상자산 폴링에는 `KRW-BTC`가 아니라 `BTC_KRW_UPBIT` 같은 `fqnfTicker`가 필요하다.
- 검증에서 뉴스 목록 카테고리 `main`은 실패했다. 새 라이브 트래픽에서 다른 값을 확인하지 않는 한 `mainnews`를 사용한다.
- 일부 차트 route는 path enum에 엄격하다. 새 차트 스크립트 경로를 추가하기 전에 작은 요청으로 검증한다.
- 네이버증권은 폴링 응답에서 숫자 필드를 comma가 포함된 문자열로, 상세 응답에서 일반 숫자 문자열로 포맷할 수 있다.
- 스킬 범위는 `stock.naver.com`으로 유지한다. 테마나 업종 구성 종목을 추론하기 위해 `finance.naver.com` 그룹 상세 HTML을 사용하지 않는다.
- `/market/stock/kr/{industry|theme|groups}/{rank}` route의 path 값은 rank다. `info` 또는 `stocklist` 호출 전에 `/api/domestic/market/{upjong|theme|group}/list`로 현재 카테고리 `no`를 찾아야 한다.
- 종목 공시/IR 엔드포인트는 `startIdx`를 사용하고, 종목 뉴스는 `page`를 사용한다. 상세 하위 페이지 전체에 하나의 페이징 방식을 가정하지 않는다.
- 가격 탭 엔드포인트는 페이징 방식이 섞여 있다. `siseDay`는 `pageSize`와 선택적 `bizdate`, `siseTick`과 투자자 `trend`는 `startIdx`와 `pageSize`를 사용한다.
- `/api/myasset/resources/invest/*` 엔드포인트는 종목 상세 페이지에서 관찰되었고 검사 당시 인증 없이 집계 투자자 분포를 반환했다. 다만 `/api/personal/users/*` 아래 계정/보유종목 엔드포인트는 계속 제외한다.
