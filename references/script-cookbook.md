# 스크립트 쿡북

명령은 스킬 루트에서 실행합니다.

## 목차

- [국내 주식](#국내-주식)
- [외부 기업분석과 레거시 조건검색](#외부-기업분석과-레거시-조건검색)
- [해외 주식과 미국 ETF](#해외-주식과-미국-etf)
- [홈과 통합 검색](#홈과-통합-검색)
- [시장 지수와 지표](#시장-지수와-지표)
- [가상자산](#가상자산)
- [뉴스와 리서치](#뉴스와-리서치)
- [리서치 소량 검증](#리서치-소량-검증)

## 국내 주식

```bash
python3 scripts/stock_summary.py --code 005930
python3 scripts/stock_summary.py --code 005930 --include-industry
python3 scripts/stock_summary.py --code 005930 --code-type NXT --include-polling
python3 scripts/stock_detail_pages.py price --code 005930
python3 scripts/stock_detail_pages.py price --code 0193W0
python3 scripts/stock_detail_pages.py hoga --code 005930
python3 scripts/stock_detail_pages.py chart-prices --code 005930 --period-type day
python3 scripts/stock_detail_pages.py sise-day --code 005930 --page-size 5
python3 scripts/stock_detail_pages.py sise-tick --code 005930 --page-size 5
python3 scripts/stock_detail_pages.py trend --code 005930 --trade-type KRX --page-size 5
python3 scripts/stock_detail_pages.py news --code 005930 --page-size 5
python3 scripts/stock_detail_pages.py notice --code 005930 --page-size 5
python3 scripts/stock_detail_pages.py ir --code 005930 --page-size 5
python3 scripts/stock_detail_pages.py ir-detail --code 005930 --article-id BOARD75384
python3 scripts/stock_detail_pages.py research --code 005930 --size 10
python3 scripts/stock_detail_pages.py invest-poll --code 005930
python3 scripts/stock_detail_pages.py invest-resource --code 005930 invest-rate --size 10
python3 scripts/stock_insights.py holder-ranking --asset-type domestic --code 005930
python3 scripts/stock_insights.py what-if --asset-type worldstock --code NVDA.O
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
python3 scripts/market_stock.py ipo-current
python3 scripts/market_stock.py ipo-recent
python3 scripts/market_stock.py upjong-theme --sort-type changeRate
python3 scripts/market_stock.py category-ranking --category themes --size 100
python3 scripts/market_stock.py category-ranking --category groups --cursor OA --size 100
python3 scripts/market_stock.py category-total-market-cap --category industries
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
python3 scripts/foreign_stock.py sector-detail --nation usa --industry-code 52407020
python3 scripts/foreign_stock.py etfs --order-type marketValue --page-size 10
python3 scripts/foreign_stock.py stock-basic --code NVDA.O
python3 scripts/foreign_stock.py stock-prices --code NVDA.O --page 1 --page-size 10
python3 scripts/foreign_stock.py finance --code NVDA.O --section overview
python3 scripts/foreign_stock.py finance --code NVDA.O --section income --period quarter
python3 scripts/foreign_stock.py stock-world-news --code NVDA.O --page 1 --page-size 10
python3 scripts/foreign_stock.py stock-local-news --code NVDA.O --page 1 --page-size 10
python3 scripts/foreign_stock.py index-constituents --code .IXIC --page 1 --page-size 10
python3 scripts/foreign_stock.py etf-composition --code VOO
python3 scripts/foreign_stock.py chart-meta --asset-type index --code .IXIC
python3 scripts/foreign_stock.py poll stock --code NVDA.O --code TSLA.O
python3 scripts/foreign_stock.py poll futures --code EScv1 --code NQcv1
python3 scripts/fund.py left-panel --code K55105B00244
python3 scripts/fund.py base-price-chart --code K55105B00244 --term 3m
python3 scripts/fund.py daily-prices --code K55105B00244 --date 2026-08-13 --size 10
```

## 홈과 통합 검색

```bash
python3 scripts/home.py market-info --trade-type KRX
python3 scripts/home.py operating-time --exchange NASDAQ
python3 scripts/home.py market-briefing
python3 scripts/home.py market-briefing-list --api-version v2 --date 2026-09-04 --size 10
python3 scripts/home.py indicators
python3 scripts/home.py notable-etf --nation foreign --page-size 10
python3 scripts/home.py notable-etf --nation foreign --order-type return1Month --middle-code 0101 --page-size 2
python3 scripts/search.py autocomplete --query 삼성전자
python3 scripts/search.py search --query 나스닥 --target index --page 1 --size 30
```

브리핑 목록의 날짜는 조회할 한국 날짜로 바꿉니다. 다음 페이지는 `hasMore`와 `nextPageToken`을 확인한 뒤 같은 명령에 `--page-token`으로 서버 값을 그대로 전달합니다. 상세는 목록에서 받은 ID로 `home.py market-briefing-detail --api-version v2 --briefing-id ID`를 사용합니다. 버전 옵션을 생략하면 호환용 기존 unversioned 경로를 유지하며, 현재 화면 계약은 v2입니다.

## 시장 지수와 지표

```bash
python3 scripts/marketindex.py majors
python3 scripts/marketindex.py major-block --block-type exchange
python3 scripts/marketindex.py polling --codes KOSPI,KOSDAQ,KPI200
python3 scripts/marketindex.py index-basic --code KOSPI
python3 scripts/marketindex.py index-integration --code KOSPI
python3 scripts/marketindex.py index-chart-meta --code KOSPI
python3 scripts/marketindex.py index-time --code KOSPI --date 2026-08-13 --start-idx 0
python3 scripts/marketindex.py index-prices --code KOSPI --page 1
python3 scripts/marketindex.py chart --code KOSPI --period-type day
python3 scripts/marketindex.py foreign-chart --asset-type index --code .DJI --period-type day
python3 scripts/marketindex.py category --category energy
python3 scripts/marketindex.py category --category transport
python3 scripts/marketindex.py detail --category energy --code CLcv1
python3 scripts/marketindex.py prices --category energy --code CLcv1 --page-size 5
python3 scripts/marketindex.py market-chart-meta --category energy --code CLcv1
python3 scripts/marketindex.py category --category exchangeWorld
python3 scripts/marketindex.py economic-upcoming --limit 5
python3 scripts/marketindex.py economic-upcoming --limit 5 --nation-type USA --nation-type KOR
python3 scripts/marketindex.py exchange-rates --currencies USD,JPY
python3 scripts/marketindex.py exchange-list
python3 scripts/marketindex.py exchange-prices --currency USD --page-size 20
python3 scripts/marketindex.py bank-exchanges --bank-type HNB
python3 scripts/marketindex.py bank-round-chart --currency USD --bank-type hana
python3 scripts/marketindex.py krx-gold
python3 scripts/marketindex.py market-polling --category metals --codes M04020000
python3 scripts/marketindex.py market-polling --category exchange --codes .DXY
python3 scripts/marketindex.py category --category metals
python3 scripts/marketindex.py category --category domesticInterest
```

## 가상자산

```bash
python3 scripts/crypto.py rank --market UPBIT --sort-type top --page-size 100
python3 scripts/crypto.py rank --market UPBIT --sort-type down --page 2 --page-size 100
python3 scripts/crypto.py majors --market UPBIT
python3 scripts/crypto.py price --market UPBIT --ticker BTC
python3 scripts/crypto.py price-change --market UPBIT --ticker BTC
python3 scripts/crypto.py price --ticker BTC --exclude-exchange BITHUMB
python3 scripts/crypto.py polling --fqnf-tickers BTC_KRW_UPBIT,ETH_KRW_UPBIT
python3 scripts/crypto.py candles --market UPBIT --ticker BTC --unit 1 --from-time 2026-04-27T09:00:00 --to-time 2026-04-27T09:40:00
python3 scripts/crypto.py daily-candles --market UPBIT --ticker BTC --from-time 2026-06-17T09:00:00 --to-time 2026-07-17T09:00:00
python3 scripts/crypto.py compare-chart --nation foreign --asset-type index --code .INX --period day --start-date-time 20260617090000 --end-date-time 20260717090000
python3 scripts/crypto.py foreign-interval-chart --asset-type INDEX --exchange NASDAQ --code .IXIC --interval 5 --start-date-time 20260716130000 --end-date-time 20260716200000
python3 scripts/crypto.py global-news --ticker BTC --page-size 10
python3 scripts/crypto.py market-updates --ticker BTC --page-size 10
python3 scripts/crypto.py profile --ticker BTC
python3 scripts/crypto.py categories-ranking --exchange-type UPBIT --page-size 50
python3 scripts/crypto.py prices --fqnf-tickers BTC_KRW_UPBIT --fqnf-tickers ETH_KRW_UPBIT
python3 scripts/crypto.py global-market-trend
python3 scripts/crypto.py expert-contents --page-size 10
python3 scripts/crypto.py market-updates-overview --page-size 9
python3 scripts/crypto.py coinmacro-news --page 1 --page-size 10
python3 scripts/crypto.py coin-briefing --ticker BTC --exchange-type UPBIT
```

## 뉴스와 리서치

```bash
python3 scripts/news.py list --category MAINNEWS
python3 scripts/news.py notice  # 날짜 생략 시 최근 3개월
python3 scripts/news.py world-news --page-size 10
python3 scripts/news.py world-news --page-size 10 --date "{YYYYMMDD}"
python3 scripts/news.py world-detail --article-id 2580641
python3 scripts/news.py aggregate --main-news-size 3 --notice-size 3
python3 scripts/news.py focus --focus global-market --page-size 15 --date "{YYYYMMDD}" --enable-fallback
python3 scripts/news.py search --query 반도체 --page-size 10
python3 scripts/notices.py list --size 5
python3 scripts/notices.py banners --size 2 --banner-type PC_TOP
python3 scripts/notices.py detail --notice-id 147
python3 scripts/research.py category --category COMPANY --page-size 10
python3 scripts/research.py category --category COMPANY --item-code 005930 --page-size 10
python3 scripts/research.py home
python3 scripts/research.py weekly-hot --size 10  # startDate 생략 시 7일 전 날짜 사용
python3 scripts/research.py ranking --ranking-type SEARCH_TOP --selected-rank 1
python3 scripts/research.py latest --size 3
python3 scripts/research.py industry-research --size 10
python3 scripts/research.py broker-list
python3 scripts/research.py by-items --item-code 005930 --item-code 000660 --size 3
python3 scripts/research.py goal-price-changed --direction up --size 10
python3 scripts/research.py analysis-focus
python3 scripts/research.py detail --category COMPANY --research-id "{RESEARCH_ID}"
# 아래 v1 호환 명령 5종(카테고리 4개 포함 8경로)은 2026-09-07 HTTP 404 확인.
# 현재 자료 조회에는 위 v2 명령을 사용하며, 실패를 빈 목록으로 해석하지 않습니다.
python3 scripts/research.py v1-category --category company --size 10
python3 scripts/research.py v1-latest --size 5
python3 scripts/research.py v1-brokers
python3 scripts/research.py v1-by-items --item-codes 005930 --item-codes 000660 --size 5
python3 scripts/research.py v1-analysis-focus
python3 scripts/discussion.py hot-home --page-size 10
python3 scripts/discussion.py hot --page-size 50
python3 scripts/discussion.py feed --page-size 50
python3 scripts/discussion.py market-feed --discussion-group-type exchange --page-size 60
python3 scripts/discussion.py post --post-id 418462889
python3 scripts/discussion.py related-hot --item-code 005930 --page-size 5
python3 scripts/discussion.py item-posts --item-code 005930 --page-size 5
python3 scripts/discussion.py item-posts --discussion-type cryptoUpbit --item-code BTC --page-size 30
python3 scripts/discussion.py global-community --ticker BTC --page-size 30
python3 scripts/discussion.py stats-by-items --start-date "{YYYY-MM-DD}" --domestic-codes 005930 --domestic-codes 000660
python3 scripts/discussion.py rankings --page-size 10
python3 scripts/discussion.py rankings --nation-type KOR --post-type HOT --page-size 10
```

기존 `recent-popular`, `category-latest`, `aggregate-static` 명령은 각각 `weekly-hot`, `latest`, `home`의 호환 alias로 유지됩니다. `home`의 `partial: true`와 `unavailable` 섹션은 API 실패를 뜻하며 빈 자료와 구분합니다.

`research.py`의 v2 `category`, `industry-research`는 1-based 페이지를 요구합니다. 예전에 첫 페이지로 보정하던 0·음수는 이제 요청 전에 오류로 거부합니다. 날짜는 실제 달력에 존재하는 `YYYY-MM-DD` 또는 `YYYYMMDD`만 허용하고 시작일이 종료일보다 늦으면 거부합니다. v1의 0-based `--index`는 유지합니다. `home`은 선택한 섹션의 요청 조건을 먼저 검증하며, 실행 중 403·429·3xx·비정상 JSON이면 이후 섹션을 `not_run`으로 남깁니다. 일반 404·500은 기존처럼 해당 섹션만 실패 처리합니다.

`stock_summary.py --include-industry`의 페이지(1~10000)·페이지 크기(1~500)는 첫 API 요청 전에 검증합니다. 업종 조회를 선택하지 않으면 사용하지 않는 업종 옵션은 검증하지 않습니다.

`discussion.py feed`는 전체 피드입니다. 종목별 조회에는 위 `item-posts`를 사용하고, 직접 `/posts?itemCode=...`를 호출하면 필터 무시 방지를 위해 요청 전에 거부됩니다. 알려진 404·500의 대안과 검증된 조건은 [제한 문서](known-limitations.md)를 확인하세요.

## 리서치 소량 검증

```bash
python3 scripts/research_check.py --category COMPANY
python3 scripts/research_check.py --category COMPANY --live --output research-check.json
```

기본 실행은 네트워크 없이 요청 계획만 출력합니다. `--live`는 선택한 v2 카테고리 한 곳에서 `size=2`로 첫·다음 페이지를 최대 2회 GET하며, 첫 응답 처리 후 1초 이상 기다립니다. 첫 페이지의 `hasNext=false`이면 다음 요청을 건너뛰고, 요청 실패·구조 불일치에는 중단합니다. 기존 `research.py category`와 요청 경로 생성 함수를 공유합니다.

검사는 `items` 배열, boolean `hasNext`, 공개 리포트 `nid`, 요청 크기, 페이지 내·간 ID 중복에 한정합니다. 추가 필드는 허용하고 정상 빈 목록은 `empty`로 표시합니다. JSON 요약에는 요청 경로·조건·확인 시각·개수·판정만 남기며 원본 본문과 리포트 내용은 저장하지 않습니다. 요청 오류에는 확인 가능한 HTTP 상태와 로컬 오류 종류 `errorKind`를 남깁니다. 종류는 `http`, `timeout`, `network`, `transport`, `encoding`, `invalid_json`, `response_too_large`, `api`, `unknown`입니다. 실패 전 결과와 아직 실행하지 않은 `not_run` 항목도 출력하며, 파일 저장은 `--output`을 지정할 때만 수행합니다. 자동 재시도나 저장된 상태에서 재개하는 기능은 없습니다.

`status=planned`는 미실행, `passed`는 실행한 표본의 검사 통과, `failed`는 요청·계약·중복 검사 실패입니다. 종료 코드는 계획/통과 0, 실패 1, 잘못된 CLI 인자 2입니다. `pagination=disjoint`만 두 비어 있지 않은 페이지의 ID 비중복을 뜻합니다. `terminal`은 첫 페이지에서 종료, `empty_next_page`는 다음 요청이 정상 빈 목록인 경우이며 비어 있지 않은 다음 페이지의 진행을 검증한 것은 아닙니다. 조회 사이 새 글이 추가되면 중복이 생길 수 있으므로 `overlap`만으로 API 결함이나 삭제를 단정하지 않습니다.

결과는 해당 조건·시점의 표본입니다. 모든 필터·끝 페이지·금융 수치 정확성을 보증하지 않으며, 전체 페이지 감사에는 [캡처 워크플로](capture-workflow.md)를 사용합니다. 기본 CI는 실 API를 호출하지 않습니다.
