# 스크립트 쿡북

명령은 스킬 루트에서 실행한다.

## 국내 주식

```bash
python3 scripts/stock_summary.py --code 005930
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
python3 scripts/market_stock.py default --order-type marketSum --market-type KOSPI --page-size 20
python3 scripts/market_stock.py default --order-type searchTop --page-size 10
python3 scripts/market_stock.py dividend --page-size 10
python3 scripts/market_stock.py ipo --page-size 10
python3 scripts/market_stock.py upjong-theme --ranking-type upjong --page-size 10
python3 scripts/category_detail.py rank industry --page-size 10
python3 scripts/category_detail.py detail theme --rank 1 --stock-page-size 10
python3 scripts/category_detail.py stocks groups --no 19 --order-type marketSum --page-size 10
python3 scripts/domestic_etf.py list --listing-type priceTop --size 10
python3 scripts/domestic_etf.py themes
python3 scripts/domestic_etf.py etn-list --order-type priceTop --page-size 10
python3 scripts/market_trend.py deposit --page-size 10
python3 scripts/market_trend.py aggregate --market-type KOSPI --period-type TIME
```

## 시장 지수와 지표

```bash
python3 scripts/marketindex.py majors
python3 scripts/marketindex.py polling --codes KOSPI,KOSDAQ,KPI200
python3 scripts/marketindex.py chart --code KOSPI --period-type day
python3 scripts/marketindex.py category --category energy
python3 scripts/marketindex.py detail --category energy --code CLcv1
python3 scripts/marketindex.py prices --category energy --code CLcv1 --page-size 5
python3 scripts/marketindex.py economic-upcoming --limit 5
python3 scripts/marketindex.py exchange-rates --currencies USD,JPY
python3 scripts/marketindex.py category --category metals
python3 scripts/marketindex.py category --category domesticInterest
```

## 가상자산

```bash
python3 scripts/crypto.py rank --market UPBIT --sort-type marketValue --page-size 20
python3 scripts/crypto.py majors --market UPBIT
python3 scripts/crypto.py price --market UPBIT --ticker BTC
python3 scripts/crypto.py price --ticker BTC --exclude-exchange BITHUMB
python3 scripts/crypto.py polling --fqnf-tickers BTC_KRW_UPBIT,ETH_KRW_UPBIT
python3 scripts/crypto.py candles --market UPBIT --ticker BTC --unit 1 --from-time 2026-04-27T09:00:00 --to-time 2026-04-27T09:40:00
```

## 뉴스와 리서치

```bash
python3 scripts/news.py list --category mainnews --page-size 20
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
```
