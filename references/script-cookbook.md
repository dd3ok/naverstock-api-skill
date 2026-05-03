# 스크립트 쿡북

명령은 스킬 루트에서 실행합니다.

## 스크립트 개요

- `scripts/stock_summary.py`: 국내 종목 상세, 폴링 현재가, 시장 구분, 컨센서스, 선택적 업종 관련 종목 조회.
- `scripts/stock_detail_pages.py`: 종목 상세의 가격표, 호가, 차트, 뉴스, 공시, IR 목록/상세, 투자자 통계, ETF 상세 내부 데이터 조회.
- `scripts/market_stock.py`: 국내 종목 랭킹/목록, 배당 랭킹, 검색 인기, IPO 진행, 업종/테마 랭킹 조회.
- `scripts/category_detail.py`: 업종/테마/그룹사 랭킹 목록, 상세 정보, 구성 종목 조회.
- `scripts/domestic_etf.py`: 국내 ETF 목록, ETF 테마, ETF 레버리지 유형 메타데이터, ETN 목록 조회.
- `scripts/market_trend.py`: 투자자 예탁금 목록/차트, 시장 집계 투자자 동향, 외국인/기관 투자자 동향 랭킹 조회.
- `scripts/marketindex.py`: 주요 지수 목록, 시장지표 카테고리, 지수 폴링, 지수 차트 조회.
- `scripts/crypto.py`: 업비트/빗썸 랭킹, 주요 코인, 폴링 가격, 분봉 캔들 조회.
- `scripts/news.py`: 시장 뉴스 목록, 포커스 카테고리, 키워드 검색 조회.
- `scripts/research.py`: 리서치 카테고리별 목록, 최근 인기 리서치, 증권사 목록, 리포트 상세, 리서치 홈 집계 블록 조회.
- `scripts/discussion.py`: 읽기 전용 종목토론 인기 목록, 글 상세, 이전/다음 글, 관련 인기 글, 종목 토론 랭킹 조회.

## 국내 주식

```bash
python3 scripts/stock_summary.py --code 005930
python3 scripts/stock_summary.py --code 005930 --include-industry
python3 scripts/stock_summary.py --code 005930 --code-type NXT --include-industry
python3 scripts/stock_detail_pages.py price --code 005930
python3 scripts/stock_detail_pages.py hoga --code 005930
python3 scripts/stock_detail_pages.py sise-day --code 005930 --page-size 5
python3 scripts/stock_detail_pages.py sise-tick --code 005930 --page-size 5
python3 scripts/stock_detail_pages.py trend --code 005930 --trade-type KRX --page-size 5
python3 scripts/stock_detail_pages.py news --code 005930 --page-size 5
python3 scripts/stock_detail_pages.py notice --code 005930 --page-size 5
python3 scripts/stock_detail_pages.py ir --code 005930 --page-size 5
python3 scripts/stock_detail_pages.py invest-poll --code 005930
python3 scripts/stock_detail_pages.py invest-resource --code 005930 invest-rate --size 10
python3 scripts/stock_detail_pages.py etf-detail --code 069500 base
python3 scripts/stock_detail_pages.py etf-detail --code 069500 component --page-size 10
python3 scripts/market_stock.py default --order-type marketSum --page-size 10
python3 scripts/market_stock.py default --order-type marketSum --market-type KOSPI --page-size 20
python3 scripts/market_stock.py default --order-type searchTop --page-size 10
python3 scripts/market_stock.py dividend --page-size 10
python3 scripts/market_stock.py ipo --page-size 10
python3 scripts/market_stock.py upjong-theme --ranking-type upjong --page-size 10
python3 scripts/category_detail.py rank industry --page-size 10
python3 scripts/category_detail.py detail theme --rank 1 --stock-page-size 10
python3 scripts/category_detail.py stocks theme --rank 1 --page-size 10
python3 scripts/category_detail.py stocks groups --no 19 --order-type marketSum --page-size 10
python3 scripts/domestic_etf.py list --listing-type priceTop --size 10
python3 scripts/domestic_etf.py themes
python3 scripts/domestic_etf.py etn-list --order-type priceTop --page-size 10
python3 scripts/market_trend.py deposit --page-size 10
python3 scripts/market_trend.py aggregate --market-type KOSPI --period-type TIME
python3 scripts/market_trend.py trend-foreign-org --market-type ALL --trade-type KRX --page-size 10
```

## 시장 지수와 지표

```bash
python3 scripts/marketindex.py majors
python3 scripts/marketindex.py polling --codes KOSPI,KOSDAQ,KPI200
python3 scripts/marketindex.py chart --code KOSPI --period-type day
python3 scripts/marketindex.py category --category energy
python3 scripts/marketindex.py category --category transport
python3 scripts/marketindex.py detail --category energy --code CLcv1
python3 scripts/marketindex.py prices --category energy --code CLcv1 --page-size 5
python3 scripts/marketindex.py economic-upcoming --limit 5
python3 scripts/marketindex.py exchange-rates --currencies USD,JPY
python3 scripts/marketindex.py category --category metals
python3 scripts/marketindex.py category --category domesticInterest
```

## 가상자산

```bash
python3 scripts/crypto.py rank --market UPBIT --sort-type marketValue --page-size 10
python3 scripts/crypto.py rank --market UPBIT --sort-type marketValue --page-size 20
python3 scripts/crypto.py majors --market UPBIT
python3 scripts/crypto.py price --market UPBIT --ticker BTC
python3 scripts/crypto.py price --ticker BTC --exclude-exchange BITHUMB
python3 scripts/crypto.py polling --fqnf-tickers BTC_KRW_UPBIT,ETH_KRW_UPBIT
python3 scripts/crypto.py candles --market UPBIT --ticker BTC --unit 1 --from-time 2026-04-27T09:00:00 --to-time 2026-04-27T09:40:00
```

## 뉴스와 리서치

```bash
python3 scripts/news.py list --category mainnews --page-size 10
python3 scripts/news.py list --category mainnews --page-size 20
python3 scripts/news.py notice --page-size 10
python3 scripts/news.py notice --page-size 20
python3 scripts/news.py world --page-size 10
python3 scripts/news.py aggregate --main-news-size 3 --notice-size 3
python3 scripts/news.py focus --focus market-outlook --page-size 20
python3 scripts/news.py search --query 반도체 --page-size 10
python3 scripts/research.py category --category COMPANY --page-size 10
python3 scripts/research.py aggregate-static
python3 scripts/research.py recent-popular
python3 scripts/research.py broker-list
python3 scripts/research.py detail --category COMPANY --research-id 91965
python3 scripts/discussion.py hot-home --page-size 10
python3 scripts/discussion.py post --post-id 418462889
python3 scripts/discussion.py related-hot --item-code 005930 --page-size 5
python3 scripts/discussion.py rankings --size 10
python3 scripts/discussion.py rankings --nation-type KOR --post-type HOT --size 10
```
