# 스크립트 쿡북

명령은 스킬 루트에서 실행합니다.

## 스크립트 개요

- `scripts/stock_summary.py`: 국내 종목 상세, 폴링 현재가, 시장 구분, 컨센서스, 선택적 업종 관련 종목 조회.
- `scripts/stock_detail_pages.py`: 종목 상세의 가격표, 호가, 차트 가격, 뉴스, 공시, IR 목록/상세, 리서치, 투자자 통계, finance v1 메뉴/ESG, ETF 상세 내부 데이터 조회.
- `scripts/market_stock.py`: 국내 종목 의미 기반 랭킹/목록, KONEX 거래량, 관리·정지·투자경고, 배당, 검색 인기, IPO, 업종/테마 랭킹 조회.
- `scripts/wisereport.py`: 현재 종목 페이지가 연결하는 WiseReport v3 기업분석 8종의 제한된 표 조회.
- `scripts/legacy_screeners.py`: 신버전에 없는 레거시 기술적 조건검색 5종과 가격 위치 2종 조회.
- `scripts/foreign_stock.py`: 해외 국가별 주식/업종, 재무·종목별 뉴스, 미국 ETF, 해외 주식·지수 상세/시세와 worldstock 폴링 조회.
- `scripts/category_detail.py`: 업종/테마/그룹사 랭킹 목록, 상세 정보, 구성 종목 조회.
- `scripts/domestic_etf.py`: 국내 ETF 목록, ETF 테마, ETF 레버리지 유형 메타데이터, ETN 목록 조회.
- `scripts/market_trend.py`: 투자자 예탁금 목록/차트, 시장 집계 투자자 동향, 외국인/기관/프로그램 동향 조회.
- `scripts/marketindex.py`: 주요 지수, 국내·해외 차트, 시장지표, 환율, 은행 환율 차트, KRX 금과 시장지표 폴링 조회.
- `scripts/crypto.py`: 업비트/빗썸 랭킹, 폴링 가격, 분봉·일봉, 비교 차트, 코인 콘텐츠, 카테고리, AI 브리핑 조회.
- `scripts/home.py`: 홈 시장 상태, 해외 거래시간, 시장 브리핑, 공개 콘텐츠, 통합 지표와 주목 ETF 조회.
- `scripts/search.py`: 공개 상품 자동완성과 전체 검색. 최근 검색과 개인 기록은 조회하지 않음.
- `scripts/news.py`: 시장 뉴스 목록, 뉴스포커스 하위 탭, 키워드 검색, 해외뉴스 목록/상세 조회.
- `scripts/notices.py`: stockSecurity v2 서비스 공지 목록/상세/배너 조회.
- `scripts/research.py`: stockSecurity v2 카테고리별 목록, 상세, 종목별 목록, 랭킹, 최신/주간 인기, 목표주가 변경, 증권사 목록, best-effort 홈 섹션과 명시적 v1 호환 조회.
- `scripts/discussion.py`: 읽기 전용 종목토론 feed, 시장 feed, 인기 목록, 글 상세, 이전/다음 글, 관련 인기 글, 종목 토론 랭킹/종목별 글/통계 조회.

## 국내 주식

```bash
python3 scripts/stock_summary.py --code 005930
python3 scripts/stock_summary.py --code 005930 --include-industry
python3 scripts/stock_summary.py --code 005930 --code-type NXT --include-industry
python3 scripts/stock_detail_pages.py price --code 005930
python3 scripts/stock_detail_pages.py hoga --code 005930
python3 scripts/stock_detail_pages.py chart-prices --code 005930 --period-type day
python3 scripts/stock_detail_pages.py sise-day --code 005930 --page-size 5
python3 scripts/stock_detail_pages.py sise-tick --code 005930 --page-size 5
python3 scripts/stock_detail_pages.py trend --code 005930 --trade-type KRX --page-size 5
python3 scripts/stock_detail_pages.py news --code 005930 --page-size 5
python3 scripts/stock_detail_pages.py notice --code 005930 --page-size 5
python3 scripts/stock_detail_pages.py ir --code 005930 --page-size 5
python3 scripts/stock_detail_pages.py research --code 005930 --size 10
python3 scripts/stock_detail_pages.py invest-poll --code 005930
python3 scripts/stock_detail_pages.py invest-resource --code 005930 invest-rate --size 10
python3 scripts/stock_detail_pages.py finance-menu --code 005930
python3 scripts/stock_detail_pages.py finance-esg --code 005930
python3 scripts/stock_detail_pages.py etf-detail --code 069500 base
python3 scripts/stock_detail_pages.py etf-detail --code 069500 component --page-size 10
python3 scripts/market_stock.py ranking market-cap --page-size 10
python3 scripts/market_stock.py ranking market-cap --market-type KOSPI --page-size 20
python3 scripts/market_stock.py ranking volume --market-type KONEX --page-size 20
python3 scripts/market_stock.py ranking management --page-size 10
python3 scripts/market_stock.py ranking investment-warning --page-size 10
# 저수준 호환/조사용. 일반 조회에는 위 ranking 명령을 우선 사용합니다.
python3 scripts/market_stock.py default --order-type marketSum --page-size 10
python3 scripts/market_stock.py search-top --page-size 10
python3 scripts/market_stock.py dividend --page-size 10
python3 scripts/market_stock.py ipo --ipo-progress-type LISTING --page-size 10
python3 scripts/market_stock.py upjong-theme --sort-type changeRate
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
TODAY="$(date +%Y%m%d)"
python3 scripts/market_trend.py trend-daily --bizdate "$TODAY" --page-size 10
python3 scripts/market_trend.py trend-time-chart --bizdate "$TODAY" --start-date "$TODAY" --end-date "$TODAY"
python3 scripts/market_trend.py trend-program --bizdate "$TODAY" --page-size 10
python3 scripts/market_trend.py trend-program-chart --bizdate "$TODAY" --start-date "$TODAY" --end-date "$TODAY"
```

## 외부 기업분석과 레거시 조건검색

현재 JSON API와 중복되는 시세·뉴스·리서치에는 아래 HTML 스크립트를 사용하지 않습니다. 출처와 허용 범위는 [external-sources.md](external-sources.md)를 먼저 확인합니다.

```bash
python3 scripts/wisereport.py --code 005930 --kind status --max-tables 10 --max-rows 30
python3 scripts/wisereport.py --code 005930 --kind consensus
python3 scripts/wisereport.py --code 005930 --kind shareholders
python3 scripts/legacy_screeners.py technical golden-cross --page 1 --limit 20
python3 scripts/legacy_screeners.py technical disparity-overheat --page 1 --limit 20
python3 scripts/legacy_screeners.py price-position low-up --market KOSDAQ --page 1 --limit 20
python3 scripts/legacy_screeners.py price-position high-down --market KOSPI --page 1 --limit 20
```

## 해외 주식과 미국 ETF

```bash
python3 scripts/foreign_stock.py stocks --nation usa --trade-type NSQ --page-size 10
python3 scripts/foreign_stock.py sectors --nation jpn
python3 scripts/foreign_stock.py sector-stocks --nation usa --industry-code 55501040 --page-size 10
python3 scripts/foreign_stock.py etfs --order-type marketValue --page-size 10
python3 scripts/foreign_stock.py stock-basic --code NVDA.O
python3 scripts/foreign_stock.py stock-prices --code NVDA.O --page 1 --page-size 10
python3 scripts/foreign_stock.py finance --code NVDA.O --section overview
python3 scripts/foreign_stock.py finance --code NVDA.O --section income --period quarter
python3 scripts/foreign_stock.py stock-world-news --code NVDA.O --page 1 --page-size 10
python3 scripts/foreign_stock.py stock-local-news --code NVDA.O --page 1 --page-size 10
python3 scripts/foreign_stock.py index-constituents --code .IXIC --page 1 --page-size 10
python3 scripts/foreign_stock.py poll stock --code NVDA.O --code TSLA.O
```

## 홈과 통합 검색

```bash
python3 scripts/home.py market-info --trade-type KRX
python3 scripts/home.py operating-time --exchange NASDAQ
python3 scripts/home.py market-briefing
python3 scripts/home.py market-briefing-list --date 2026-07-17 --size 10
python3 scripts/home.py indicators
python3 scripts/home.py notable-etf --nation foreign --page-size 10
python3 scripts/search.py autocomplete --query 삼성전자
python3 scripts/search.py search --query 나스닥 --target index --page 1 --size 30
```

## 시장 지수와 지표

```bash
python3 scripts/marketindex.py majors
python3 scripts/marketindex.py major-block --block-type exchange
python3 scripts/marketindex.py polling --codes KOSPI,KOSDAQ,KPI200
python3 scripts/marketindex.py chart --code KOSPI --period-type day
python3 scripts/marketindex.py foreign-chart --asset-type index --code .DJI --period-type day
python3 scripts/marketindex.py category --category energy
python3 scripts/marketindex.py category --category transport
python3 scripts/marketindex.py detail --category energy --code CLcv1
python3 scripts/marketindex.py prices --category energy --code CLcv1 --page-size 5
python3 scripts/marketindex.py economic-upcoming --limit 5
python3 scripts/marketindex.py economic-upcoming --limit 5 --nation-type USA --nation-type KOR
python3 scripts/marketindex.py exchange-rates --currencies USD,JPY
python3 scripts/marketindex.py exchange-list
python3 scripts/marketindex.py exchange-prices --currency USD --page-size 20
python3 scripts/marketindex.py bank-exchanges --bank-type HNB
python3 scripts/marketindex.py bank-round-chart --currency USD --bank-type hana
python3 scripts/marketindex.py krx-gold
python3 scripts/marketindex.py market-polling --category metals --codes M04020000
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
python3 scripts/crypto.py daily-candles --market UPBIT --ticker BTC --from-time 2026-06-17T09:00:00 --to-time 2026-07-17T09:00:00
python3 scripts/crypto.py compare-chart --nation foreign --asset-type index --code .INX --period day --start-date-time 20260617090000 --end-date-time 20260717090000
python3 scripts/crypto.py foreign-interval-chart --asset-type INDEX --exchange NASDAQ --code .IXIC --interval 5 --start-date-time 20260716130000 --end-date-time 20260716200000
python3 scripts/crypto.py global-news --ticker BTC --page-size 10
python3 scripts/crypto.py market-updates --ticker BTC --page-size 10
python3 scripts/crypto.py profile --ticker BTC
python3 scripts/crypto.py categories-ranking --exchange-type UPBIT --page-size 10
python3 scripts/crypto.py prices --fqnf-tickers BTC_KRW_UPBIT --fqnf-tickers ETH_KRW_UPBIT
python3 scripts/crypto.py global-market-trend
python3 scripts/crypto.py expert-contents --page-size 10
python3 scripts/crypto.py market-updates-overview --page-size 9
python3 scripts/crypto.py coinmacro-news --page 1 --page-size 10
python3 scripts/crypto.py coin-briefing --ticker BTC --exchange-type UPBIT
```

## 뉴스와 리서치

```bash
python3 scripts/news.py list --category mainnews --page-size 10
python3 scripts/news.py list --category mainnews --page-size 20
python3 scripts/news.py notice --page-size 10
python3 scripts/news.py notice --page-size 20
python3 scripts/news.py focus --focus global-market --page-size 10
python3 scripts/news.py world-news --page-size 10
python3 scripts/news.py world-news --page-size 10 --date "{YYYYMMDD}"
python3 scripts/news.py world-detail --article-id 2580641
python3 scripts/news.py aggregate --main-news-size 3 --notice-size 3
python3 scripts/news.py focus --focus market-outlook --page-size 20
python3 scripts/news.py focus --focus global-market --page-size 15 --date "{YYYYMMDD}" --enable-fallback
python3 scripts/news.py search --query 반도체 --page-size 10
python3 scripts/notices.py list --size 5
python3 scripts/notices.py banners --size 2 --banner-type PC_TOP
python3 scripts/notices.py detail --notice-id 147
python3 scripts/research.py category --category COMPANY --page-size 10
python3 scripts/research.py category --category COMPANY --item-code 005930 --page-size 10
python3 scripts/research.py home
python3 scripts/research.py weekly-hot --size 10  # startDate 생략 시 오늘 날짜 사용
python3 scripts/research.py ranking --ranking-type SEARCH_TOP --selected-rank 1
python3 scripts/research.py latest --size 3
python3 scripts/research.py industry-research --size 10
python3 scripts/research.py broker-list
python3 scripts/research.py by-items --item-code 005930 --item-code 000660 --size 3
python3 scripts/research.py goal-price-changed --direction up --size 10
python3 scripts/research.py analysis-focus
python3 scripts/research.py detail --category COMPANY --research-id "{RESEARCH_ID}"
python3 scripts/research.py v1-category --category company --size 10
python3 scripts/research.py v1-latest --size 5
python3 scripts/research.py v1-brokers
python3 scripts/research.py v1-by-items --item-codes 005930 --item-codes 000660 --size 5
python3 scripts/research.py v1-analysis-focus
python3 scripts/discussion.py hot-home --page-size 10
python3 scripts/discussion.py feed --page-size 10
python3 scripts/discussion.py market-feed --page-size 10
python3 scripts/discussion.py post --post-id 418462889
python3 scripts/discussion.py related-hot --item-code 005930 --page-size 5
python3 scripts/discussion.py item-posts --item-code 005930 --page-size 5
python3 scripts/discussion.py stats-by-items --start-date "{YYYY-MM-DD}" --domestic-codes 005930 --domestic-codes 000660
python3 scripts/discussion.py rankings --page-size 10
python3 scripts/discussion.py rankings --nation-type KOR --post-type HOT --page-size 10
```

기존 `recent-popular`, `category-latest`, `aggregate-static` 명령은 각각 `weekly-hot`, `latest`, `home`의 호환 alias로 유지됩니다. `home`의 `partial: true`와 `unavailable` 섹션은 API 실패를 뜻하며 빈 자료와 구분합니다.
