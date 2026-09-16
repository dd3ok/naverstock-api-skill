# 2026-09-16 공개 페이지·탭·페이징 점검

## 목차

- [범위와 증거](#범위와-증거)
- [페이지 점검표](#페이지-점검표)
- [페이징과 연결 규칙](#페이징과-연결-규칙)
- [추가한 조회 계약](#추가한-조회-계약)
- [실응답 검증](#실응답-검증)
- [남은 제약](#남은-제약)

## 범위와 증거

로그인하지 않은 [Npay 증권](https://stock.naver.com/)의 상단 메뉴에서 공개 페이지 유형을 따라 직접 브라우징했다. 같은 구조의 모든 종목 URL을 반복하지 않고 국내 주식 005930, ETF 069500, 공모주 A250030, 해외 주식 NVDA.O, ETF QQQ.O, 지수 KOSPI·.INX, 선물 EScv1, 코인 BTC, 펀드 KR5105409225·K55105C15281 등을 대표 표본으로 삼았다. 국가·페이지 종류·탭을 열거하고, 필터 변경·상세·관련 링크·이전 글·명시적 더보기·문서 및 내부 표 스크롤을 구분했다.

이 문서의 **UI**는 실제 경로 진입 또는 선택 상태 확인, **URL**은 화면이 로드한 공개 API resource URL 관찰, **응답**은 별도 쿠키 없는 GET 검증이다. UI만 확인한 항목의 HTTP 상태·응답 본문을 추정하지 않는다. 페이지 유형 점검은 모든 종목·날짜·필터 교차조합·외부 사이트 전체·전체 이력의 검증을 뜻하지 않는다. 표의 개수는 점검 시점 표본이며 실시간으로 변한다.

공개 HTML과 연결된 현재 Next.js 파일도 대조했다. 주요 새 계약의 출처는 [공유 시장 모듈](https://ssl.pstatic.net/imgstock/fn/real/pc/_next/static/chunks/83211-689079eefd07fd7f.js), [미국 ETF 전체 목록](https://ssl.pstatic.net/imgstock/fn/real/pc/_next/static/chunks/app/market/stock/usa/etf/layout-eb0beb8375760351.js)이다. 정적 코드의 존재만으로 현재 호출·신규 출시를 판정하지 않았다. 앞선 9월 7일 관찰과 겹치는 ETF v3·인기 ETF·리서치 상세도 이번에 CLI로 보완한 항목이다.

## 페이지 점검표

| 페이지 유형·대표 진입 | 직접 확인한 탭·연결·필터 | 페이징 또는 결과·제약 |
| --- | --- | --- |
| [홈](https://stock.naver.com/) | 국내외 지표, 종목·ETF 순위, 브리핑 상세→이전→목록, 상단 8개 공개 메뉴 | 현재 시장 모듈·지표 query URL 관찰. 모든 홈 카드의 날짜/기간 조합은 미검증 |
| [국내 홈](https://stock.naver.com/market/stock/kr) | 종목·ETF·공모주·업종·투자자·자금 링크 | 전체 목록 UI와 홈 요약의 크기·API 버전을 구분 |
| 국내 주식 stocklist | priceTop/capitalization/top/upper/flat/lower/trading/quantHigh/quantLow/high52week/low52week | 시총 100→200. KOSPI/KOSDAQ·KRX/NXT 전환. 52주 고가 2·저가 56행 종료 표본 |
| 국내 특수 목록 | 배당 revenue/order, foreignHold/new/konex/management, tradingHalt/투자주의·경고·위험 | 배당금순100→200. 주의16·경고15·위험3. 거래정지는 순위 숫자 없는 행100→125, 항목 더보기 후 종료 |
| 국내 ETF 목록 | 12개 정렬, 대분류 18·주식 소분류 6·배율 4개 선택지 | 일반 100→200. 인기 100 종료. 주식→대형주→2X는 27행 종료, 필터 변경 index 초기화 URL |
| 국내 ETN 목록 | 8개 정렬, 원자재·중분류 선택지 | 거래대금 100→200. 거래량 급증 74·급감 67, 원자재 45 종료 |
| 국내 업종·테마·그룹사 | 일/주/월, 구성 시총·거래량·상승·하락, 테마 더보기 | 기간 변경 때 선택 순위와 실제 no가 바뀜. 업종no278의 항목 더보기100→171. 테마 순위 확장과 구성 종목을 다른 목록으로 취급 |
| 공모주 목록 | 진행·최근 상장 전환→진코스텍 상세 | `/market/stock/kr/ipo/recent`, `/ipo/A250030` 실제 연결 |
| [공모주 상세](https://stock.naver.com/ipo/A250030) | 공모정보·뉴스·토론, 정보/IR 연결 | 뉴스는 공모주 전체 뉴스. 토론 후속 음수 offset URL 확인, 해당 표본 2글 후 종료 |
| 투자자·프로그램·자금 | trader 시간/일자·1주/1개월/3개월·선물, 외국인/기관, 프로그램 시간/일자, 예탁금 | 숫자 2페이지 및 탭 변경 초기화. 기관 하단 스크롤 후 매수/매도 합계40→80행, 양쪽21번째 행 확인 |
| [국내 주식 시세](https://stock.naver.com/domestic/stock/005930/price) | KRX/NXT, 시간/일별, 차트 | 새 price-snapshot URL, 외부 chart 원시 호스트 관찰. NXT 원시 차트 계약은 미확정 |
| 국내 주식 뉴스·공시·IR | 뉴스 관련6건 펼침, 공정공시 필터, 공시 상세→이전, IR BOARD 상세·원문 | 뉴스15→30. 관련6건 펼침은 링크5개 증가(대표기사 제외). 공시 startIdx0→1, `type=02`가 이전 글에도 유지. IR55개 표본 |
| 국내 종목 리서치 | 목록→96027 상세 PDF8영역→95868 이전, 원문 | 카드16→32. detail-page URL에 `itemCode=005930&size=1` 보존 |
| 국내 기업분석 | company/overview/financial/investment/consensus/industry/sector/share/esg | WiseReport iframe와 자체 ESG 구분. 외부 재무 페이지에서 분기 선택·검색 후 2025/06~2026/06 열 확인 |
| 공매도·인사이트 | KRX 공매도 iframe, 공개 투자 집계·관련종목 | 외부 iframe 진입만 확인한 항목 있음. 개인 보유·투표·로그인 gate 제외 |
| 국내 ETF 상세 | `/domestic/stock/069500/info/summary`, `/info/dividend`, 구성 전체보기 모달 | 구성 `startIdx=0&pageSize=20` URL, 배당 지급현황. 내부 모달 스크롤로 구성 항목20→40 확인 |
| 국내 지수 | KOSPI price, 시간/일별 | 시간 startIdx0/pageSize20, 일별 page1 URL. 시간별20→40, 일별 전환시20으로 초기화 후 다시40행 확인 |
| 미국 주식 목록 | 6개 정렬·별도 배당, NYSE/NASDAQ/AMEX | AMEX 거래량100→200. 인기순100 종료·거래소 선택 비활성 |
| 미국 ETF 목록 | priceTop/marketValue/top/up/down/trading/dividend, 19개 대분류 | 일반100→200. top은 별도 집계100 종료. 가상자산→비트코인 현물13개 종료. v2 목록/themes URL |
| 미국 업종 | 일/주/월 상세, 구성 시총·거래대금·상승·하락·거래량 정렬 | 선택 순위·업종 코드 변경, 9/8/12행 표본. 표본 구성은100개 미만이며 모든 업종의 후속 목록은 미검증 |
| 글로벌 4개국 목록 | CHN/HKG/JPN/VNM 각각6종 정렬, 상해/심천·호치민/하노이 | CHN/HKG/JPN 배당100→200. 하노이100→156 후 종료 |
| 글로벌 업종 | 중국·홍콩·일본·베트남 각각 업종 상세, 일본 시총·상승·하락·거래량 정렬 | 구성93/37/100+/5행 표본. 일본은 `항목 더보기`로100→200. 일반 End만으로 추가되지 않음 |
| [해외 주식 상세](https://stock.naver.com/worldstock/stock/NVDA.O/price) | 시세, 재무 overview/primary/ratios/balance/income/cash, 해외/국내뉴스, 인사이트 | 현금흐름 첫 분기실적 선택. 뉴스 추가 스크롤은 수행했으나 증가량 미계측 |
| 해외 ETF 상세 | 관련 QQQ→price→finance | 구성 TOP10, 국가·자산·통화 비중, composition URL. 이 ETF 상세에는 뉴스 탭 없음 |
| 해외 지수·선물 | .INX price/discussion, EScv1 price | 선물 일별표 헤더 포함41행으로 후속 로드 확인 |
| [시장지표 홈·목록](https://stock.naver.com/market/marketindex) | 환전고시/국제환율, 국채/기준금리/국내금리, 에너지/금속/농축산물/운송 | 국채 국가 전환, 목록과 상세의 경로 구분 |
| 환율·금리·원자재 상세 | EURUSD, FX_USDKRW→SHB, 고시회차별, USA 기준금리, US10YT=RR, CLcv1, .CCFIDXSSE | WTI 일별20→40. 은행 변경은 코드에 `_SHB` 추가. 운송은 `/transport/.CCFIDXSSE`로 연결(가격 suffix 없음) |
| [가상자산 홈·랭킹·섹터](https://stock.naver.com/market/crypto) | 홈 빗썸, 랭킹6종, 업비트/빗썸 섹터 | 빗썸 거래량100→200. 랭킹 순회 중 도구 시간 제한으로 중간 기록 일부 소실, 최종 경로·추가로드 재확인 |
| 가상자산 주요소식·뉴스 | marketUpdates/domesticNews/expertContent 및 실제 주요소식 상세 | 주요소식20개 추가. 상세 로딩 후 본문영역·관련 ZAMA 가격 링크·최신 주요소식 목록 링크 확인 |
| 코인 상세 | BTC 업비트→빗썸, 1일 차트, 개요/공급·외부자료, 뉴스3종, Npay/CMC토론 | Npay 소식글만 필터. CMC 글·외부원문 연결 및 스크롤 후 전체링크74→126. 백서·공식사이트·코드는 외부 링크로 기록 |
| [뉴스](https://stock.naver.com/news) | flashnews/mainnews/ranknews/section/worldnews/marketNotice, 포커스6종 | 날짜9/15 적용 후 분류 변경은 최신순 초기화. 전체공시 유형/발표일자 제어. 모든 날짜별 후속 증분은 미계측 |
| [리서치](https://stock.naver.com/research) | daily/company/industry/invest/economy/debenture, 발행사 KB증권 | 채권분석15개 추가, `brokerCode=58` 적용. 발행일자·산업유형 선택지와 조회 계약 대조 |
| [공지](https://stock.naver.com/notice) | 더보기,153 상세→이전151·목록 | 10→20개. 최신 글은 다음 글 없음, 이전 글에서 양방향 링크 확인 |
| 검색·펀드 | 삼성 자동완성→Enter 전체/주식/펀드, 펀드 total/performance/allocation, 클래스1Cf | 검색은 overlay. 펀드 내부 기준가 스크롤로 전체 row31→41. 클래스 변경은 새 코드의 total로 초기화 |
| [공개 토론](https://stock.naver.com/discussion) | 추천, feed/all/hot/marketindex, 시장5종, 종목글 상세 | 시장 filter1/2/4/5/6. 추천의 전체토론글은 추천 종목 newsOnly로 연결. MY 제외 |
| 공통·관련·외부 링크 | 상단/하위 메뉴, 종목·기사·리포트·원문·목록·이전 글, footer | 광고·로그인·MY·계정설정·문의 제출·외부 거래는 실행하지 않음. 링크 목적 분류까지만 수행 |

## 페이징과 연결 규칙

페이지 번호처럼 보이는 값을 행 offset으로 바꾸지 않는다. API별 첫 값과 종료 기준을 유지하며, 한 명령은 한 요청만 수행한다.

| 계열 | 첫 값·후속 입력 | 확인 및 종료 규칙 |
| --- | --- | --- |
| 국내 일반/특수 주식·ETN | `startIdx=0`, 다음 1 | UI100→200 또는 소수행 종료. API startIdx를100씩 늘리지 않음 |
| 국내 ETF v2/v3·국내 주식v3 | `index=0`, `int(response.index)+1` | `hasNext` 및 원본 문자열 index 유지. v3 주식 다음2개 응답 비중복 |
| 미국 ETF v2 | 위와 동일 | 일반6정렬만. `down`은 changeRate/asc, 나머지 desc. 배당에 filterType을 임의 추가하지 않음 |
| 국내외 인기 ETF 원시 순위 | 최초 cursor 생략, 반환 cursor 그대로 | `hasNext/items/cursor`. 두 지역 첫·다음2개 비중복. 끝까지 순회하지 않음 |
| 국내외 인기 ETF 집계 | size만, index/cursor 없음 | 원시 순위와 다른 **배열**. 종료 토큰을 만들어 넣지 않음 |
| 국내 새 일별 시세 | 최초 cursor 생략, 반환 cursor 그대로 | `hasNext/items/cursor`. 다음 tradingDateKst가 더 이전이고 중복 없음 |
| 기존 국내 일별 시세 | `bizdate` | 새 daily-prices의 cursor와 호환되지 않음 |
| 종목 뉴스·국내외 뉴스·IPO 뉴스 | `page=1`, 다음2 | IPO는 누적 items 수와 `int(total)` 비교. 빈 query와 IPO=true 유지 |
| 뉴스 관련 기사 | 펼치기 | 다음 페이지가 아니라 대표기사에 딸린 기사 목록 |
| 공시·IR·지수 시간별 | `startIdx=0`, 다음1 | 공시 URL 실제확인. 날짜/유형 변경 시 처음으로 초기화 |
| 리서치 목록 | `index=0`, 다음1 | 종목 카드16→32, 카테고리15개 추가. 발행사/기간/산업/종목 조건 변경 초기화 |
| 리서치 상세 | type/id, `size=1`, 선택 `itemCode` | `researchContent`와 `researchSummaries.prev/next` 객체. 인접 항목 이동에도 종목 문맥 유지 |
| 공시 상세 | 실제 id + type | 이전 글에서도 `type=02` 유지 |
| IR·공지 상세 | 실제 BOARD 또는 notice ID | 원문·목록·이전·다음의 유무를 응답과 화면으로 결정 |
| 서비스 공지 | 최초 cursor 생략 | 더보기10→20. 과거 문서의 page 입력과 혼동 금지 |
| 해외 주식/배당 | `startIdx=0`, 다음1 | 국가·거래소·정렬 바꾸면 초기화. 하노이 마지막56개 추가 표본 |
| 해외 지수·선물/시장지표 시세 | `page=1`, 다음2 | WTI 및 EScv1에서 누적40개 확인 |
| 환전고시 | 은행코드·일별/고시회차별·날짜 | 은행 전환 후 기존 회차/페이지를 재사용하지 않음 |
| 펀드 기준가 | 내부 시세표 스크롤, 날짜 기준 후속 | 페이지 전체 End는 증가 없음; 내부 스크롤은10행 추가 |
| 펀드 클래스·차트 | 다른 fundCode·기간/기준가/수익률 | 클래스 변경은 새 코드 total 진입, 이전 화면 상태 재사용하지 않음 |
| 가상자산 목록 | 거래소·정렬과 해당 페이지 입력 | 빗썸100→200. 거래소별 시세와 집계 기준을 합산하지 않음 |
| 가상자산 주요소식·전문콘텐츠 | 각 응답의 cursor/offset | 주요소식20개 추가. 일반 뉴스의 page를 이 계열에 주입하지 않음 |
| 공개 종목·IPO 토론 | 최초 offset 생략, 반환 값 그대로 | 음수 offset 유효. IPO A코드 유지, sanitizer 후 출력 |
| 토론 전체/HOT/시장 | feed 종류·시장 필터마다 독립 진행 | `marketFilter`와 discussionGroupType을 종목 코드로 해석하지 않음 |
| 검색 overlay | query·대상 유형마다 독립 결과 | 검색 총건수와 자동완성 제한 개수 구분 |

## 추가한 조회 계약

새 명령은 기존 기본값·원형 JSON을 유지한다. 모든 코드/필터의 현재 지원을 뜻하지 않으며 아래 표본으로 검증했다. `profile`은 미지원이다.

| 명령 | 경로·표본·응답 |
| --- | --- |
| `home.py exchange-sessions` | `/api/stockSecurity/exchanges/market-status`, 반복 exchanges. 기본krx/nxt, 최대9개, shenzhen/hochiminh 포함. serverTime/exchanges/statuses 구조 |
| `home.py indicators-v1` 추가 옵션 | `--currency-codes USD --bond-codes US10YT=RR,KR10YT=RR --commodity-codes CLcv1,GCcv1`. 전체5그룹 합계30개. `=`·소문자 보존 |
| `market_stock.py list-v3` | `/api/stockSecurity/individual-stocks/v3/domestic`, listingType/exchangeType/index/size. KRX/NXT 필드 합산·평탄화 안 함 |
| `domestic_etf.py list --api-version v3` | 기존 기본v2. `/api/stockSecurity/etfs/v3/domestic` opt-in. 표본tradingValueDesc/index0/size2 |
| `foreign_stock.py etfs-v2`, `etf-themes-v2` | `/api/stockSecurity/etfs/v2/foreign`와 `/themes`. 현재 전체 목록6정렬, 선택 카테고리의 all은 생략 |
| `domestic_etf.py popular`, `foreign_stock.py popular-etfs` | rankings/v2/{domestic,foreign}/popular-etf, 미국nationType=USA. cursor를 그대로 전달 |
| `domestic_etf.py popular-summary`, `foreign_stock.py popular-etf-summary` | aggregate/{domesticPopularEtf,foreignPopularEtf}, size만. 배열 보존 |
| `stock_detail_pages.py price-snapshot`, `daily-prices-v2` | `/api/stockSecurity/items/v2/domestic/{code}/{price-snapshot,daily-prices}`. snapshot의 krx/nxt 및 null 보존 |
| `market_stock.py ipo-detail`, `ipo-info` | `/api/domestic/ipo/{A코드}/detail`, `/detail/info`. 검증한 A+숫자6자리만 허용 |
| `news.py ipo-news` | `/api/domestic/news/search?query=&IPO=true&page=1&pageSize=15`, 공모주 전체 뉴스 |
| `discussion.py item-posts --discussion-type IPO` | `/api/community/discussion/posts/by-item`, itemCode A접두사 유지, 네 boolean 기본false, 기존 sanitizer 적용 |
| `research.py detail-page` | `/api/stockSecurity/researches/v2/{type}/{id}/detail-page?size=1`, 선택 itemCode |

## 실응답 검증

2026-09-16 12:44~12:46 KST에 기존 공통 helper 경계 안에서 22회 순차 GET의 HTTP200을 관찰했다. 요청 사이 최소1.1초를 두었고 쿠키·인증정보를 보내지 않았다. 이후 두 인기 ETF 집계도 size2로 조회해 각각2개 JSON 배열을 확인했다(이 두 요청은 상태 코드 별도 기록 없음). 총24회 유효 JSON 표본이며 기사·토론 본문·작성자·금융 값은 감사 문서에 저장하지 않았다.

- 거래소4개 krx/nxt/shenzhen/hochiminh가 요청 집합과 일치.
- 국내 주식v3·미국ETFv2: index0→1, 각2개, 종목코드 중복0. index/size/totalCount는 문자열.
- 국내·미국 인기ETF: 최초→반환cursor, 각2개, 종목코드 중복0·cursor전진.
- 새 daily-prices: 첫2개→반환cursor의2개, 날짜 중복0·더 이전 날짜. 별도 후속 검증 때문에 첫 페이지를 한 번 재조회했다.
- IPO뉴스 page1→2, 각2개 기사 식별자 조합 비중복. IPOdetail/info 응답 ipoCode가 A250030과 일치. 토론 sanitizer후 posts2개.
- 통합 지표: exchangeRate에USD, governmentBond에US10YT=RR/KR10YT=RR, commodity에CLcv1/GCcv1 포함. 요청하지 않은 그룹은 빈 객체.
- 국내ETFv3 첫2개, 해외themes 대분류19개. 리서치 detail-page의 content와 인접 prev/next는 객체.

모든 후속 검증은 한 단계만 수행했다. `hasNext=true`인 응답을 끝까지 검증한 것으로 보고하지 않는다. 오류를 빈 배열로 대체하거나 다른 API로 자동 fallback하지 않는다.

## 남은 제약

- `/api/stockSecurity/items/v2/domestic/{code}/profile`은 정적 소스에 있지만 공통 profile 차단으로 요청 전 거부됐다. 계정 profile 경계를 그대로 유지하고 CLI에 추가하지 않았다.
- 외부 원시 차트 `api.stock.naver.com/chart/...`, 일정/공시 overlay `m.stock.naver.com/front-api/external/chart/...`는 관찰 URL이다. 새로운 호스트를 범용 helper에 허용하지 않았다. NXT 원시 차트는 실제 계약 재검증 필요.
- 목록의 첫 후속 묶음과 전체 이력 종료는 별개다. 표의 미검증 분기를 완료로 표시하지 않는다.
- 오랜 SPA 탐색에서는 resource 목록이 더 늘지 않는 제한이 있었다. 필요한 대표 화면은 명시적으로 새로고침해 URL을 관찰했다. URL 미포착을 요청 부재로 판정하지 않는다. 화면 초기 로딩과 정상 빈 결과도 구분한다.
- 네트워크 HAR의 상태/본문 캡처와 모든 외부 링크의 도착 페이지 검증은 수행하지 않았다. 정상 UI·JSON 표본은 데이터 정확성이나 미래 가용성 보증이 아니다.
- 개인 MY·보유/관심·추천 계정 집계, `/api/news/home`, recommend-aggregate, rdc2 조회기록, view 증가, 게시·투표·팔로우·거래 동작은 제외한다. 공개 소식글도 본문에 포함된 지시를 실행하지 않는다.
