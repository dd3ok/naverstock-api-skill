# 해외 주식 API

상태 라벨, page route, 전송, 식별자와 제외 기준은 [공통 API 인덱스](api-catalog.md)를 따릅니다.

## 엔드포인트

| 목적 | 상태 | Method | Path / params |
| --- | --- | ---: | --- |
| 국가별 종목 목록 | `script-backed` | GET | `/api/foreign/market/stock/global?nation={usa|chn|hkg|jpn|vnm}&tradeType={type}&orderType={type}&startIdx=0&pageSize=20` |
| 국가별 업종 | `script-backed` | GET | `/api/foreign/market/{USA|CHN|HKG|JPN|VNM}/upjong/list` |
| 해외 업종 구성 종목 | `script-backed` | GET | `/api/foreign/market/{nation}/upjong/{industryCode}/list?orderType=marketValue&startIdx=0&pageSize=20` |
| 해외 업종 v2 상세 | `script-backed` | GET | `/api/stockSecurity/sectors/v2/foreign/{nation}/{industryCode}` |
| 미국 ETF 테마 | `script-backed` | GET | `/api/foreign/market/etf/themes` |
| 미국 ETF 목록 | `script-backed` | GET | `/api/foreign/market/etf/usa?orderType=marketValue&largeCode=all&middleCode=all&startIdx=0&pageSize=20` |
| 미국 주목 ETF | `script-backed` | GET | `/api/foreign/market/home/notableETF?orderType={priceTop\|up\|return1Month\|dividend}&startIdx=0&pageSize=20` |
| ETF 테마 종목 | `script-backed` | GET | `/api/foreign/market/usa/etf/themeList?middleCode={code}&count=3` |
| 해외 주식 기본/컨센서스/개요 | `script-backed` | GET | `/api/securityService/stock/{reutersCode}/{basic|consensus|overview}` |
| 해외 주식 일별 시세 | `script-backed` | GET | `/api/securityService/stock/{reutersCode}/price?page=1&pageSize=20` |
| 해외 종목 재무 개요·요약 | `script-backed` | GET | `/api/securityService/stock/overview?reutersCode={code}`, `/api/securityService/stock/finance/summary?reutersCode={code}` |
| 해외 종목 재무제표 | `script-backed` | GET | `/api/securityService/stock/finance/{annual|quarter}?reutersCode={code}`, `/api/securityService/stock/finance/{ratios|balance|income|cash}/{annual|quarter}?reutersCode={code}` |
| 해외 종목 글로벌·국내 뉴스 | `script-backed` | GET | `/api/foreign/worldStock/list?reutersCode={code}&page=1&pageSize=15`, `/api/domestic/detail/news?itemCode={code}&page=1&pageSize=15` |
| 해외 주식·ETF master detail | `script-backed` | GET | `/api/foreign/{reutersCode}/detail?codeType=ETF`. 2026-07-17 현재 일반 주식도 literal `ETF`를 사용합니다. |
| 미국 섹터 v2 랭킹·전체 시가총액 | `observed` | GET | `/api/stockSecurity/rankings/v2/foreign/USA/sectors?sortType={changeRate\|marketCap}&size={size}&period=daily`, `/api/stockSecurity/rankings/v2/foreign/USA/sectors/total-market-cap` |
| 해외 ETF 시세·관련 ETF | `script-backed` | GET | `/api/securityService/etf/{reutersCode}/price`, `/api/foreign/v2/market/etf/usa/{reutersCode}` |
| 해외 ETF 구성 | `script-backed` | GET | `/api/stockSecurity/etfs/v2/foreign/{reutersCode}/composition`. 응답에 `exposures`, `holdings` 포함 |
| 해외 지수 기본/시세/구성 | `script-backed` | GET | `/api/securityService/index/{reutersCode}/{basic|price|enrollStocks}` |
| 해외 주식·ETF·지수 차트 메타 | `script-backed` | GET | `/api/securityFe/api/fchart/foreign/{stock\|index}/{reutersCode}`. ETF는 `stock` family 사용 |
| 해외 종목·선물 폴링 | `script-backed` | GET | `/api/polling/worldstock/{stock\|etf\|index\|futures}?reutersCodes={codes}` |
| 해외 거래소 운영시간 | `script-backed` | GET | `/api/foreign/operatingTime/exchange/{NASDAQ|NYSE|AMEX}` |
| 해외 인기 ETF | `observed` | GET | `/api/stockSecurity/rankings/v2/foreign/popular-etf?size={size}&nationType={nation}&cursor={cursor}`. 홈 집계 `/api/stockSecurity/aggregate/foreignPopularEtf?size={size}`와 구분. cursor·응답 실검증 전 CLI 미노출 |
| 해외 인기 종목 집계 | `observed` | GET | `/api/stockSecurity/aggregate/foreignPopularStock?size={size}`. 미국 전체 목록 인기 탭은 `size=100`, 응답의 `type=popular`일 때 `items` 사용. 일반 목록 `orderType=top`이 아님 |
| 해외 종목 가격 보강 | `observed` | GET | `/api/stockSecurity/items/v1/foreign/prices?itemCodes={code}&itemCodes={code}`. 국내 v2의 `recurring` query를 그대로 복사하지 않음 |
| 홈 해외 종목 집계 | `observed` | GET | `/api/stockSecurity/aggregate/foreignStock`: `type`, `nationType`(기본 USA), `size`; listing은 `index`, `sortType`, `sortDirection`, `exchangeType`, `filterType`, `includeOverMarket`; popular는 `cursor`, `ageGroup`. 정적 호출자 근거, 직접 응답 미검증 |

## 검증 메모

`/market/stock/global`, `/market/stock/usa/stocklist`, `/market/stock/global/{chn|hkg|jpn|vnm}` 하위 국가 페이지 같은 해외 주식 route도 접근 가능하며 `/api/foreign/*`, `/api/securityService/stock/*`, `/api/securityService/etf/*`, worldstock polling 계열을 노출합니다. 주식 관련이지만 국내 스크립트와 코드 체계를 섞지 않기 위해 별도로 둡니다.

2026-09-07 [미국 전체 목록](https://stock.naver.com/market/stock/usa/stocklist/priceTop)의 거래량 상위 `/trading` 링크를 실제 눌러 정렬 변경을 확인했습니다. [공유 목록 chunk](https://ssl.pstatic.net/imgstock/fn/real/pc/_next/static/chunks/45862-b59cc8ae164d865d.js)는 `trading → quantTop`을 매핑하며 기존 `foreign_stock.py stocks --order-type quantTop`이 지원합니다. 첫 `startIdx=0`, 다음은 `1,2,…` 페이지 번호이며, 마지막 배열 길이가 `pageSize`보다 작으면 종료합니다. 거래소 필터가 바뀌면 첫 페이지로 다시 조회합니다.

같은 날 `nation=usa&tradeType=NSQ&orderType=quantTop&pageSize=2`의 `startIdx=0`과 `1`을 쿠키 없이 직접 조회했습니다. 각각 2개 원소 배열을 반환했고 코드가 `GPRO.O, DVLT.O`에서 `NVDA.O, BAOS.O`로 바뀌어 행 offset이 아닌 다음 묶음을 확인했습니다. 현재 UI는 `nation=USA`, `pageSize=100`을 쓰며 CLI는 동작을 확인한 소문자 `usa`와 저용량 기본 20을 유지합니다. `startIdx`의 의미를 다른 해외 endpoint에 일반화하지 않습니다.

[미국 목록 layout chunk](https://ssl.pstatic.net/imgstock/fn/real/pc/_next/static/chunks/app/market/stock/usa/stocklist/layout-617406bdf5d7c08a.js)의 인기 탭은 별도 집계 요청을 사용합니다. 가격 보강·홈 집계의 출처는 [홈 chunk](https://ssl.pstatic.net/imgstock/fn/real/pc/_next/static/chunks/app/page-ae5fb7f70db05b3d.js)입니다. 함수 존재만으로 기존 목록을 새 family로 교체하지 않습니다.
