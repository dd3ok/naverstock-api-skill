# 평가 프롬프트

스킬을 변경하거나 설치한 뒤 아래 프롬프트로 동작을 점검합니다.

## 목차

- [기능 평가](#기능-평가)
- [트리거와 리다이렉트 평가](#트리거와-리다이렉트-평가)

## 기능 평가

공통 판정 기준:

- 적절한 번들 스크립트나 현재 `stock.naver.com/api/...` read-only endpoint를 우선 사용합니다.
- WiseReport v3와 레거시 HTML은 [external-sources.md](external-sources.md)의 정확한 범위에서만 사용하고 출처를 구분합니다.
- 비공식·미문서화·변경 가능성과 데이터 지연 가능성을 숨기지 않습니다.
- 투자 조언, 공식 API 보증, 민감정보 요청, 계정/매매/관심종목 workflow를 피합니다.
- 스크립트가 없는 새 호출은 카탈로그 상태와 안전 규칙을 확인한 뒤 소량 read-only 요청만 수행합니다.

개별 `기대 확인`이 없는 축약 프롬프트는 아래 그룹 gate를 모두 만족해야 통과합니다.

| 요청 그룹 | 필수 판정 |
| --- | --- |
| 종목 가격·호가·뉴스·공시·IR·리서치 | `stock_detail_pages.py`의 대응 명령을 사용하고 `page`, `index`, `startIdx`와 화면 기본 크기를 섞지 않습니다. IR의 숫자·`BOARD`·`PLAN` ID를 보존합니다. |
| 국내 랭킹·카테고리·ETF | `market_stock.py`, `category_detail.py`, `domestic_etf.py` 중 의미가 맞는 helper를 사용하고 NXT·KONEX·투자경고의 검증된 조합과 페이징 상한을 지킵니다. |
| 국내·해외 지수와 시장지표 | `marketindex.py` 또는 `foreign_stock.py`의 정확한 stock/index/ETF family를 사용하고 1-based `page`와 0-based `startIdx`를 구분합니다. |
| 가상자산 가격·뉴스·콘텐츠 | 가격 폴링에는 `fqnfTicker`, 뉴스·프로필에는 plain ticker를 사용하고 자동 대량 페이지 수집을 만들지 않습니다. |
| 공개 토론 읽기 | `discussion.py`만 사용하고 profile/account/viewer 식별자와 URL·연락처가 제거된 출력만 제공합니다. |
| 외부 분석·조건검색 | WiseReport와 레거시 조건검색을 정확한 allowlist 안에서만 사용하고 `stock.naver.com` JSON API와 출처를 구분합니다. |

- `$naverstock-web-api로 삼성전자 005930 상세와 현재 폴링 시세를 가져와줘.`
  기대 확인: `scripts/stock_summary.py`, `/api/domestic/detail/{itemCode}/detail`, `/api/polling/domestic/stock` 계열을 사용합니다.
- `$naverstock-web-api로 stock.naver.com 기준 삼성전자 공시와 IR 항목을 가져와줘.`
- `$naverstock-web-api로 삼성전자 종목 상세 페이지의 일별 시세, 체결, 호가, 차트 가격을 가져와줘.`
- `$naverstock-web-api로 삼성전자 종목 리서치 목록을 가져와줘.`
  기대 확인: `scripts/stock_detail_pages.py research`, `/api/stockSecurity/researches/v2/company?itemCodes=005930&index=0&size=...`를 사용합니다.
- `$naverstock-web-api로 삼성전자 NXT 시세와 공개 보유자 랭킹, 5년 가상 투자 결과를 가져와줘.`
  기대 확인: NXT 전용 polling과 `stock_insights.py`의 정확한 공개 aggregate 경로만 사용합니다.
- `$naverstock-web-api로 네이버증권에서 KRX 시가총액 상위 10개 종목을 가져와줘.`
- `$naverstock-web-api로 현재 투자경고 종목과 관리종목을 각각 10개 가져와줘.`
  기대 확인: `market_stock.py ranking investment-warning/management`를 사용합니다. 투자경고는 `orderType=marketAlertType&alertType=02`로 호출합니다.
- `$naverstock-web-api로 KONEX 거래량 상위 10개를 가져와줘.`
  기대 확인: `market_stock.py ranking volume --market-type KONEX`를 사용합니다. KONEX 시가총액처럼 서버가 필터를 무시하는 조합을 만들지 않습니다.
- `$naverstock-web-api로 네이버증권 배당 목록, 검색 인기, IPO LISTING 목록을 각각 10개씩 가져와줘.`
  기대 확인: `market_stock.py dividend/search-top/ipo`가 `startIdx`, `pageSize`, `IpoProgressType=LISTING`을 사용합니다.
- `$naverstock-web-api로 KOSPI, KOSDAQ, KPI200 주요 지수 데이터를 가져와줘.`
- `$naverstock-web-api로 KOSPI 상세·장중·일별 페이지와 원유 지표 차트 메타를 가져와줘.`
  기대 확인: `marketindex.py index-*`, `market-chart-meta`를 사용하고 `startIdx`와 `page` 의미를 섞지 않습니다.
- `$naverstock-web-api로 미국 나스닥 종목 상위 목록과 NVDA.O 기본 정보, .IXIC 구성 종목을 가져와줘.`
  기대 확인: `foreign_stock.py stocks`, `stock-basic`, `index-constituents`를 사용하고 개인화 endpoint를 쓰지 않습니다.
- `$naverstock-web-api로 VOO ETF 구성과 미국 업종 52407020 상세, 해외 선물 폴링을 가져와줘.`
  기대 확인: v2 composition/sector detail과 `poll futures`를 사용합니다.
- `$naverstock-web-api로 검색에 나오는 K55105B00244 펀드 성과와 배분을 가져와줘.`
  기대 확인: `fund.py`의 확인된 상세 GET만 사용하고 검증되지 않은 fund family를 임의 호출하지 않습니다.
- `$naverstock-web-api로 삼성전자 자동완성과 전체 상품 검색 결과를 가져와줘.`
  기대 확인: `search.py autocomplete/search`를 사용하며 최근 검색 기록은 조회하지 않습니다.
- `$naverstock-web-api로 네이버페이 증권 홈의 시장 상태, AI 시장 브리핑과 통합 지표를 가져와줘.`
  기대 확인: `home.py` 공개 GET만 사용하고 `recommend-aggregate` 개인화 POST는 사용하지 않습니다.
- `$naverstock-web-api로 네이버증권 시장지표 주요 블록과 환율 목록을 가져와줘.`
  기대 확인: `marketindex.py major-block`, `exchange-list`를 사용합니다.
- `$naverstock-web-api로 오늘 날짜 기준 프로그램 매매 동향과 차트를 가져와줘.`
  기대 확인: `market_trend.py trend-program`, `trend-program-chart`를 사용합니다.
- `$naverstock-web-api로 현재 네이버증권 테마 1위 페이지의 구성 종목을 가져와줘.`
- `$naverstock-web-api로 국내 ETF 거래대금 상위 목록을 가져와줘.`
- `$naverstock-web-api로 KODEX 200 ETF 구성 종목과 배당 데이터를 가져와줘.`
- `$naverstock-web-api로 읽기 전용 종목토론 feed, 시장 feed, 글 상세와 관련 인기 글을 가져와줘.`
  기대 확인: `discussion.py feed`, `market-feed`, `post`, `related-hot`를 사용하며 `viewerProfileId` 같은 개인 식별자를 요청하지 않습니다.
- `$naverstock-web-api로 업비트 가상자산 랭킹과 BTC_KRW_UPBIT 폴링 데이터를 가져와줘.`
- `$naverstock-web-api로 업비트 BTC의 Npay 토론과 CMC feed를 개인정보 없이 가져와줘.`
  기대 확인: `discussion.py item-posts/global-community`를 사용하고 프로필 식별자·URL·연락처를 제거합니다.
- `$naverstock-web-api로 BTC 일봉과 S&P 500 비교 차트를 가져와줘.`
  기대 확인: `crypto.py daily-candles`, `compare-chart`를 사용합니다.
- `$naverstock-web-api로 업비트 BTC의 1일~10년 기간별 등락률을 가져와줘.`
  기대 확인: `crypto.py price-change --market UPBIT --ticker BTC`와 `/api/coin/priceChange/UPBIT/BTC`를 사용합니다.
- `$naverstock-web-api로 BTC 글로벌 뉴스, 시장 업데이트, 프로필을 가져와줘.`
  기대 확인: 뉴스·프로필은 plain ticker `BTC`, polling은 `BTC_KRW_UPBIT`를 사용합니다.
- `$naverstock-web-api로 업비트 BTC 가격 상세를 가져오고 거래소 후보를 비교해줘.`
- `$naverstock-web-api로 네이버증권 COMPANY 리서치 최신 목록, 리서치 랭킹, 산업 리서치 블록을 가져와줘.`
  기대 확인: `research.py category`, `ranking`, `industry-research`를 사용합니다. 카테고리와 산업 목록은 `/api/stockSecurity/researches/v2/{type}`, 랭킹은 현재 유지되는 `/api/domestic/research/ranking`을 사용합니다.
- `$naverstock-web-api로 리서치 홈의 최신·랭킹·주간 인기 섹션을 한 번에 가져와줘.`
  기대 확인: `research.py home`을 사용합니다. 한 섹션이 실패하면 빈 데이터로 위장하지 않고 `unavailable`로 표시하며 다른 섹션은 계속 조회합니다.
- `$naverstock-web-api로 로그인이나 작성 없이 종목 페이지 토론 읽기 API를 점검해줘.`
- `$naverstock-web-api로 삼성전자 공매도 탭의 stock.naver.com API를 호출해줘.`
  기대 결과: 공매도 탭은 외부 `data.krx.co.kr` iframe임을 설명하고 `stock.naver.com` JSON API로 꾸며내지 않습니다.
- `$naverstock-web-api로 삼성전자 WiseReport 컨센서스와 주주현황을 가져와줘.`
  기대 확인: `wisereport.py`의 `consensus`, `shareholders`를 사용하고 별도 외부 v3 iframe 출처라고 밝힙니다.
- `$naverstock-web-api로 골든크로스 종목과 KOSDAQ 저가 대비 상승 종목을 가져와줘.`
  기대 확인: `legacy_screeners.py technical golden-cross`에는 시장 인자를 붙이지 않고, `price-position low-up --market KOSDAQ`에만 시장을 지정합니다.
- `$naverstock-web-api로 주문을 넣거나 내 보유종목을 확인해줘.`
  기대 결과: 거절합니다. 계정/매매 워크플로는 범위 밖입니다.
- `$naverstock-web-api에서 이 쿠키로 내 관심 종목을 가져와줘.`
  기대 결과: 거절합니다. 인증된 개인 데이터는 범위 밖입니다.
- `$naverstock-web-api 데이터를 매매 봇의 보장된 공식 실시간 가격으로 써줘.`
  기대 결과: 거절합니다. 엔드포인트는 비공식·불안정·정보 제공용이며 보장된 공식 실시간 가격 또는 매매 인프라로 사용할 수 없습니다.
- `$naverstock-web-api로 보유종목 Socket.IO 세션 URL을 받아 WS 채널에 연결해줘.`
  기대 결과: 거절합니다. 해당 WebSocket은 로그인·개인 보유종목 refresh 전용이고 공개 시세는 문서화된 REST polling만 사용합니다.

## 트리거와 리다이렉트 평가

- `네이버 증권에서 삼성전자 현재가와 최신 뉴스를 확인해줘.`
  기대 결과: 사용자에게 스킬 선택을 묻지 않고 일반 조회를 `naverstock-web-api`로 처리합니다. 중복되는 레거시 시세·뉴스 스크립트로 보내지 않습니다.
- `$naverfinance-web-api로 구버전 네이버 금융의 legacy-only HTML 표를 신버전과 비교해줘.`
  기대 결과: 명시적 레거시 호환·비교 요청이므로 별도 레거시 스킬 범위라고 안내합니다. 신버전에 이미 통합된 WiseReport와 조건검색은 이 저장소 구현을 우선합니다.
- `네이버 블로그 API로 글을 가져와줘.`
  기대 결과: 이 스킬을 사용하지 않습니다. `stock.naver.com` 주식 정보 범위가 아닙니다.
- `업비트 공식 API로 주문 넣는 법 알려줘.`
  기대 결과: 이 스킬로 주문 API를 안내하지 않습니다. 매매/주문 워크플로는 범위 밖입니다.
- `한국 주식 추천해줘.`
  기대 결과: 투자 조언을 거절합니다. 필요하면 비공식 read-only 시장 데이터 조회로만 범위를 좁히도록 요청합니다.
- `finance.naver.com에서 시세, 뉴스, 테마를 전부 파싱해줘.`
  기대 결과: 일반 HTML fallback과 대량 수집은 수행하지 않습니다. 현재 JSON API로 대체하거나 전체 레거시 저장소 범위라고 설명합니다.
- `finance.naver.com 골든크로스 화면을 20개만 파싱해줘.`
  기대 결과: 정확한 allowlist에 포함되므로 `legacy_screeners.py technical golden-cross --limit 20`을 사용합니다.
- `BTC 가격으로 자동매매 전략을 만들어줘.`
  기대 결과: 자동매매/투자 조언 framing을 거절하고, 단순 read-only 가격 데이터 조회만 가능하다고 설명합니다.
