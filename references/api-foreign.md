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

## 검증 메모

`/market/stock/global`, `/market/stock/usa/stocklist`, `/market/stock/global/{chn|hkg|jpn|vnm}` 하위 국가 페이지 같은 해외 주식 route도 접근 가능하며 `/api/foreign/*`, `/api/securityService/stock/*`, `/api/securityService/etf/*`, worldstock polling 계열을 노출합니다. 주식 관련이지만 국내 스크립트와 코드 체계를 섞지 않기 위해 별도로 둡니다.
