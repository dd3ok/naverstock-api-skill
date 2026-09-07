# 해외 주식 API

상태 라벨, page route, 전송, 식별자와 제외 기준은 [공통 API 인덱스](api-catalog.md)를 따릅니다.

`script-backed`와 `observed`는 CLI 래퍼 유무를 구분하며, HTTP 성공 여부를 뜻하지 않습니다. 아래 날짜별 실호출 기록은 해당 쿼리 조합에 한정합니다.

## 목차

- [엔드포인트](#엔드포인트)
- [검증 메모](#검증-메모)
- [2026-09-07 ETF·집계 계약](#2026-09-07-etf집계-계약)

## 엔드포인트

| 목적 | 상태 | Method | Path / params |
| --- | --- | ---: | --- |
| 국가별 종목 목록 | `script-backed` | GET | `/api/foreign/market/stock/global?nation={usa\|chn\|hkg\|jpn\|vnm}&tradeType={type}&orderType={type}&startIdx=0&pageSize=20` |
| 국가별 업종 | `script-backed` | GET | `/api/foreign/market/{USA\|CHN\|HKG\|JPN\|VNM}/upjong/list` |
| 해외 업종 구성 종목 | `script-backed` | GET | `/api/foreign/market/{nation}/upjong/{industryCode}/list?orderType=marketValue&startIdx=0&pageSize=20` |
| 해외 업종 v2 상세 | `script-backed` | GET | `/api/stockSecurity/sectors/v2/foreign/{nation}/{industryCode}` |
| 미국 ETF 테마 | `script-backed` | GET | `/api/foreign/market/etf/themes` |
| 미국 ETF 목록 | `script-backed` | GET | `/api/foreign/market/etf/usa?orderType=marketValue&largeCode=all&middleCode=all&startIdx=0&pageSize=20` |
| 미국 주목 ETF | `script-backed` | GET | `/api/foreign/market/home/notableETF?orderType={priceTop\|up\|return1Month\|dividend}&startIdx=0&pageSize=20`. 선택 `largeCode`, `middleCode`; `return1Month`의 확인된 테마·크기 조합은 아래 참조 |
| ETF 테마 종목 | `script-backed` | GET | `/api/foreign/market/usa/etf/themeList?middleCode={code}&count=3`. `count`를 실제 반환 개수의 상한으로 가정하지 않음 |
| 해외 주식 기본/컨센서스/개요 | `script-backed` | GET | `/api/securityService/stock/{reutersCode}/{basic\|consensus\|overview}` |
| 해외 주식 일별 시세 | `script-backed` | GET | `/api/securityService/stock/{reutersCode}/price?page=1&pageSize=20` |
| 해외 종목 재무 개요·요약 | `script-backed` | GET | `/api/securityService/stock/overview?reutersCode={code}`, `/api/securityService/stock/finance/summary?reutersCode={code}` |
| 해외 종목 재무제표 | `script-backed` | GET | `/api/securityService/stock/finance/{annual\|quarter}?reutersCode={code}`, `/api/securityService/stock/finance/{ratios\|balance\|income\|cash}/{annual\|quarter}?reutersCode={code}` |
| 해외 종목 글로벌·국내 뉴스 | `script-backed` | GET | `/api/foreign/worldStock/list?reutersCode={code}&page=1&pageSize=15`, `/api/domestic/detail/news?itemCode={code}&page=1&pageSize=15` |
| 해외 주식·ETF master detail | `script-backed` | GET | `/api/foreign/{reutersCode}/detail?codeType=ETF`. 2026-07-17 현재 일반 주식도 literal `ETF`를 사용합니다. |
| 미국 섹터 v2 랭킹·전체 시가총액 | `observed` | GET | `/api/stockSecurity/rankings/v2/foreign/USA/sectors?sortType={changeRate\|marketCap}&size={size}&period=daily`, `/api/stockSecurity/rankings/v2/foreign/USA/sectors/total-market-cap`. 2026-09-07 두 정렬 `size=2`와 전체 시가총액 200 확인, CLI 미노출 |
| 해외 ETF 시세·관련 ETF | `script-backed` | GET | `/api/securityService/etf/{reutersCode}/price`, `/api/foreign/v2/market/etf/usa/{reutersCode}` |
| 해외 ETF 구성 | `script-backed` | GET | `/api/stockSecurity/etfs/v2/foreign/{reutersCode}/composition`. 응답에 `exposures`, `holdings` 포함 |
| 해외 지수 기본/시세/구성 | `script-backed` | GET | `/api/securityService/index/{reutersCode}/{basic\|price\|enrollStocks}` |
| 해외 주식·ETF·지수 차트 메타 | `script-backed` | GET | `/api/securityFe/api/fchart/foreign/{stock\|index}/{reutersCode}`. ETF는 `stock` family 사용 |
| 해외 종목·선물 폴링 | `script-backed` | GET | `/api/polling/worldstock/{stock\|etf\|index\|futures}?reutersCodes={codes}` |
| 해외 거래소 운영시간 | `script-backed` | GET | `/api/foreign/operatingTime/exchange/{NASDAQ\|NYSE\|AMEX}` |
| 해외 인기 ETF | `observed` | GET | `/api/stockSecurity/rankings/v2/foreign/popular-etf?size={size}&nationType={nation}&cursor={cursor}`. 첫 요청은 cursor 생략, 이후 응답값을 그대로 전달. 2026-09-07 `nationType=USA&size=2` 첫·다음 응답 200 확인, CLI 미노출. 홈 집계 `/api/stockSecurity/aggregate/foreignPopularEtf?size={size}`와 구분 |
| 해외 인기 종목 집계 | `observed` | GET | `/api/stockSecurity/aggregate/foreignPopularStock?size={size}`. 미국 전체 목록 인기 탭은 `size=100`, 응답의 `type=popular`일 때 `items` 사용. 일반 목록 `orderType=top`이 아님 |
| 해외 종목 가격 보강 | `observed` | GET | `/api/stockSecurity/items/v1/foreign/prices?itemCodes={code}&itemCodes={code}`. 2026-09-07 NVDA.O·AAPL.O 반복 query는 종목 코드를 키로 한 객체와 200 반환. 국내 v2의 `recurring` query를 그대로 복사하지 않음 |
| 홈 해외 종목 집계 | `observed` | GET | `/api/stockSecurity/aggregate/foreignStock`: `type`, `nationType`(기본 USA), `size`; listing은 `index`, `sortType`, `sortDirection`, `exchangeType`, `filterType`, `includeOverMarket`; popular는 `cursor`, `ageGroup`. 2026-09-07 아래 listing 5조합과 popular 첫 요청을 `size=2`로 200 확인, CLI 미노출 |

## 검증 메모

2026-09-07 홈 하락 목록이 반환한 `RIV_r`를 그대로 기본 정보에 넣으면 200이지만, 기존 CLI가 `RIV_R`로 바꾸면 409였습니다. 해외 코드 정규화는 이제 underscore 뒤에서 거래소 구분점 앞까지의 접미사 철자를 보존합니다. `riv_r`는 `RIV_r`, 일반 입력 `nvda.o`는 기존처럼 `NVDA.O`가 됩니다. 수정한 CLI의 기본 정보와 주식 폴링이 실제로 200과 `reutersCode=RIV_r`를 반환했습니다. 해외 종목 인사이트에도 같은 정규화를 적용하며 각 명령의 기존 허용 문자·길이 제한은 유지합니다. 선물 `GCcv1`의 별도 정규화는 바꾸지 않습니다. 이 표본으로 모든 혼합 대소문자 코드의 지원을 보증하지 않고 서버가 준 철자를 사용합니다.

`/market/stock/global`, `/market/stock/usa/stocklist`, `/market/stock/global/{chn|hkg|jpn|vnm}` 하위 국가 페이지 같은 해외 주식 route도 접근 가능하며 `/api/foreign/*`, `/api/securityService/stock/*`, `/api/securityService/etf/*`, worldstock polling 계열을 노출합니다. 주식 관련이지만 국내 스크립트와 코드 체계를 섞지 않기 위해 별도로 둡니다.

2026-09-07 [미국 전체 목록](https://stock.naver.com/market/stock/usa/stocklist/priceTop)의 거래량 상위 `/trading` 링크를 실제 눌러 정렬 변경을 확인했습니다. [공유 목록 chunk](https://ssl.pstatic.net/imgstock/fn/real/pc/_next/static/chunks/45862-b59cc8ae164d865d.js)는 `trading → quantTop`을 매핑하며 기존 `foreign_stock.py stocks --order-type quantTop`이 지원합니다. 첫 `startIdx=0`, 다음은 `1,2,…` 페이지 번호이며, 마지막 배열 길이가 `pageSize`보다 작으면 종료합니다. 거래소 필터가 바뀌면 첫 페이지로 다시 조회합니다.

같은 날 `nation=usa&tradeType=NSQ&orderType=quantTop&pageSize=2`의 `startIdx=0`과 `1`을 쿠키 없이 직접 조회했습니다. 각각 2개 원소 배열을 반환했고 코드가 `GPRO.O, DVLT.O`에서 `NVDA.O, BAOS.O`로 바뀌어 행 offset이 아닌 다음 묶음을 확인했습니다. 현재 UI는 `nation=USA`, `pageSize=100`을 쓰며 CLI는 동작을 확인한 소문자 `usa`와 저용량 기본 20을 유지합니다. `startIdx`의 의미를 다른 해외 endpoint에 일반화하지 않습니다.

[미국 목록 layout chunk](https://ssl.pstatic.net/imgstock/fn/real/pc/_next/static/chunks/app/market/stock/usa/stocklist/layout-617406bdf5d7c08a.js)의 인기 탭은 별도 집계 요청을 사용합니다. 가격 보강·홈 집계의 출처는 [홈 chunk](https://ssl.pstatic.net/imgstock/fn/real/pc/_next/static/chunks/app/page-ae5fb7f70db05b3d.js)입니다. 함수 존재만으로 기존 목록을 새 family로 교체하지 않습니다.

같은 날 USA·CHN·HKG·JPN·VNM의 종목 목록, 업종 목록, 업종 구성·v2 상세를 각각 무인증으로 조회해 200을 확인했습니다. 업종 코드는 국가별 목록에서 선택했으며 한 국가의 코드를 다른 국가에 임의로 적용하지 않았습니다. 재무 overview·summary와 finance/ratios/balance/income/cash의 annual·quarter, 주식·ETF·지수 상세·차트 메타 및 공개 polling 각 유형도 표본 상품으로 응답을 확인했습니다. 이 결과는 다른 모든 상품의 지원 여부, 재무 단위·기간 값, 정렬 정확성까지 검증했다는 뜻은 아닙니다.

## 2026-09-07 ETF·집계 계약

- `notableETF?orderType=return1Month&startIdx=0&pageSize=2`는 HTTP 500을 반환했습니다. 현재 홈 chunk는 해외 테마를 선택한 뒤 `middleCode`와 `return1Month`를 함께 보내고, 요청 빌더의 기본 `pageSize`는 10입니다. 실제 테마 목록에서 확인한 `0101`을 추가한 `orderType=return1Month&middleCode=0101&startIdx=0&pageSize=10`은 HTTP 200과 10개 배열을 반환했습니다. 처음에는 테마와 크기가 동시에 달라 원인을 분리할 수 없었으나, 이후 같은 `startIdx=0&pageSize=2`에 `middleCode=0101`만 추가한 요청도 200과 2개 배열을 반환했습니다. 이 표본에서는 테마를 포함한 조합이 동작했지만 모든 요청에서 테마가 필수라고 단정하거나 일시적 서버 오류 가능성을 배제하지 않습니다. enum은 유지하고 500을 빈 목록으로 숨기지 않습니다.
- `themeList?middleCode=0101&count=2`는 HTTP 200과 **3개** 배열을 반환했습니다. 요청한 count와 실제 배열 길이를 따로 기록합니다. 관련 ETF `/foreign/v2/market/etf/usa/VOO`는 최상위 배열이 아니라 `largeThemaCode`, `middleThemaCode`, `list`를 가진 객체였습니다.
- `popular-etf?nationType=USA&size=2`는 `hasNext`, `items`, `cursor`를 가진 객체였습니다. 받은 cursor를 그대로 전달한 다음 응답의 종목 코드와 순번이 바뀌어 페이지 진행을 확인했습니다. 두 응답 모두 `hasNext=true`여서 마지막 페이지 종료까지 검증한 것은 아닙니다.
- `foreignPopularEtf?size=2`는 2개 배열, `foreignPopularStock?size=2`는 `hasNext`, `cursor`, `items`와 항목별 `price`를 가진 객체를 반환했습니다. 두 집계와 `popular-etf` 랭킹은 별도 계약입니다.
- 미국 섹터 v2 랭킹은 `period=daily`, `size=2`의 `changeRate`·`marketCap` 정렬에서 `hasNext`, `items`, `cursor` 객체를 반환했습니다. 전체 시가총액은 `totalMarketCap`, `sectorCount`, `totalRisingCount`, `totalUnchangedCount`, `totalFallingCount`, `updatedAt` 필드를 가진 객체였습니다. 응답 구조와 표본 종목 코드는 확인했지만 합계 수치, 정렬 정확성, 다음 cursor까지 검증한 것은 아닙니다.

홈 `foreignStock`의 현재 호출자는 `nationType=USA`, `size=10`을 사용합니다. listing은 `index=0`, `includeOverMarket=true`와 아래 정렬값을 보내며, popular 첫 요청은 `type=popular`만 추가합니다. 초기 호출은 `exchangeType`, `filterType`, `ageGroup`, `cursor`를 보내지 않습니다. 이 값들은 빌더에 선택 인자가 있다는 이유만으로 임의 지정하지 않습니다.

| 홈 탭 | `sortType` | `sortDirection` |
| --- | --- | --- |
| 상승 | `changeRate` | `desc` |
| 하락 | `changeRate` | `asc` |
| 시가총액 | `marketCap` | `desc` |
| 거래량 | `tradingVolume` | `desc` |
| 기본 거래대금 | `tradingValue` | `desc` |

위 listing 5조합과 popular를 `size=2`로 줄여 직접 확인했으며 모두 HTTP 200과 `items` 2개를 반환했습니다. listing 항목에는 가격 필드가 직접 있고, popular 항목에는 `itemCode`와 중첩 `price`가 있습니다. listing의 `totalCount`는 관찰한 정렬 조합에 따라 달랐으므로 동일 모집단이나 단순 정렬만의 차이를 가정하지 않습니다. 수치 정렬의 정확성, 추가 페이지, 선택 필터 전체 조합은 이번 표본 응답만으로 확인되지 않았습니다.
