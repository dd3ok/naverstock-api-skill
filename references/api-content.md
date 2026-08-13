# 공지·뉴스·리서치·종목토론 API

상태 라벨, page route, 전송, 식별자와 제외 기준은 [공통 API 인덱스](api-catalog.md)를 따릅니다.

## 목차

- [서비스 공지 API](#서비스-공지-api)
- [뉴스 API](#뉴스-api)
- [리서치 API](#리서치-api)
- [종목토론 API](#종목토론-api)

## 서비스 공지 API

| 목적 | 상태 | Method | Path / params |
| --- | --- | ---: | --- |
| 서비스 공지 목록 | `script-backed` | GET | `/api/stockSecurity/notices/v2?size=10&cursor={cursor}`. `cursor`는 opaque 서버 값 |
| 서비스 공지 상세 | `script-backed` | GET | `/api/stockSecurity/notices/v2/{noticeId}` |
| 서비스 공지 배너 | `script-backed` | GET | `/api/stockSecurity/notices/v2/banners?size=2&type=PC_TOP` |
| 홈 공지 목록 legacy | `needs-recheck` | GET | `/api/domestic/home/noticeList?page=1&pageSize=5`. 2026-07-09 직접 확인에서 404를 반환했습니다. 서비스 공지는 `stockSecurity/notices/v2`를 우선 사용합니다. |
| 홈 공지 상세 legacy | `needs-recheck` | GET | `/api/domestic/home/notice/{noticeId}`. 새 경로는 `/api/stockSecurity/notices/v2/{noticeId}`입니다. |

## 뉴스 API

| 목적 | 상태 | Method | Path / params |
| --- | --- | ---: | --- |
| 뉴스 목록 | `script-backed` | GET | `/api/domestic/news/list?category=MAINNEWS&page=1&pageSize=15` |
| 포커스 뉴스 (`/news/section`) | `script-backed` | GET | `/api/domestic/news/focus?sid=401&page=1&pageSize=15` |
| 뉴스포커스 해외증시 (`/news/section`, `global-market`) | `script-backed` | GET | `/api/domestic/news/focus?sid=403&page=1&pageSize=15`. 2026-08-13에는 정상 데이터 확인 |
| 뉴스 검색 | `script-backed` | GET | `/api/domestic/news/search?query=반도체&page=1&pageSize=20`. 현재 연결된 독립 검색 page route는 확인되지 않아 helper의 기존 저용량 기본을 유지 |
| 시장 공시/공지 뉴스 | `script-backed` | GET | `/api/domestic/news/noticeList?page=1&pageSize=15&startDate={3개월전 yyyyMMdd}&endDate={오늘 yyyyMMdd}&keyword={keyword}&typeIdx={idx}` |
| 해외뉴스 목록 (`/news/worldnews`) | `script-backed` | GET | `/api/foreign/news/worldNews?page=1&pageSize=15&date={yyyyMMdd}`. Reuters/해외 시장 뉴스 목록입니다. |
| 해외뉴스 상세 (`/news/worldnews/{aid}`) | `script-backed` | GET | `/api/foreign/news/worldNews/{aid}` |
| 뉴스 홈 집계 | `script-backed` | GET | `/api/domestic/news/aggregate/home?flashNewsSize=4&mainNewsSize=6&rankingNewsSize=5&overseasNewsSize=5&focusSize=5&moneyStorySize=20&noticeSize=5` |

관찰된 목록 카테고리는 `MAINNEWS`, `FLASHNEWS`, `RANKNEWS`입니다. CLI는 기존 소문자 입력을 대문자로 정규화하되 현재 UI 값을 전송합니다. `stock`, `market`, `all` 같은 임의 값은 거절합니다.

2026-05-05 직접 확인에서 뉴스 상단 탭 route는 `/news/flashnews`, `/news/mainnews`, `/news/ranknews`, `/news/section`, `/news/worldnews`였습니다. `/news/worldnews`는 `page`가 1부터 증가하는 목록 API를 사용하고, 날짜 필터는 `date=yyyyMMdd`를 추가합니다. 각 목록 item의 `aid`로 `/news/worldnews/{aid}` 페이지와 `/api/foreign/news/worldNews/{aid}` 상세 API를 조회할 수 있습니다. 상세 응답은 `{ "article": ..., "latestList": [...] }` 형태이며 `article.subcontent`에 HTML 원문/고지 문구가 포함될 수 있습니다.

`/news/section`의 포커스 뉴스는 `/api/domestic/news/focus`를 사용하며, 하위 탭은 query `tab`으로 선택됩니다. 관찰된 탭/섹션 맵은 `market-outlook=401`(시황·전망), `company-analysis=402`(기업·종목분석), `global-market=403`(해외증시), `bond-futures=404`(채권·선물), `disclosure-memo=406`(공시·메모), `exchange-rate=429`(환율)입니다. 최신순 기본 호출은 현재 날짜 `date=yyyyMMdd`와 `enableFallback=true`를 함께 보내 과거 기사로 fallback할 수 있고, 직접 지정 시 `maxDays`는 1-7 범위만 허용됩니다. 날짜별 필터에서는 선택 날짜의 기사만 남기도록 클라이언트가 추가 필터링합니다. `sid=403`은 2026-05-06에는 빈 결과였지만 2026-08-13 재확인에서는 정상 데이터를 반환했습니다. 독립 해외뉴스 목록에는 `/api/foreign/news/worldNews`를 사용합니다.

## 리서치 API

| 목적 | 상태 | Method | Path / params |
| --- | --- | ---: | --- |
| 카테고리 목록 | `script-backed` | GET | `/api/stockSecurity/researches/v2/{market\|company\|industry\|invest\|economy\|debenture}?index=0&size=15`. 선택 query: `query`, `startDate`, `endDate`, 반복 `brokerCodes`, `industryTypes`, `itemCodes` |
| 카테고리 상세 | `script-backed` | GET | `/api/stockSecurity/researches/v2/{researchType}/{researchId}` |
| 종목 리포트 목록 | `script-backed` | GET | `/api/stockSecurity/researches/v2/company?itemCodes={itemCode}&index=0&size=16` |
| 여러 종목별 최근 리포트 | `script-backed` | GET | `/api/stockSecurity/researches/v2/company/by-items?itemCodes={code}&size=3`. `itemCodes`는 반복 query입니다. |
| 상세 페이지 인접 리포트 | `observed` | GET | `/api/stockSecurity/researches/v2/{researchType}/{researchId}/detail-page?itemCode={itemCode}&size=1` |
| 주간 인기 | `script-backed` | GET | `/api/stockSecurity/researches/v2/weekly-hot?startDate={yyyy-MM-dd}&size=10`. `startDate` 생략은 400이며 CLI 기본은 현재 UI처럼 7일 전 |
| 카테고리별 최신 | `script-backed` | GET | `/api/stockSecurity/researches/v2/latestResearch?size=3` |
| 목표주가 변경 | `script-backed` | GET | `/api/stockSecurity/researches/v2/company/goal-price-changed?direction={up\|down}&size=10` |
| 분석 포커스 | `script-backed` | GET | `/api/stockSecurity/researches/v2/analysis-focus` |
| 랭킹 | `script-backed` | GET | `/api/domestic/research/ranking?rankingType={type}&selectedRank={rank}` |
| 증권사 목록 | `script-backed` | GET | `/api/stockSecurity/researches/v2/brokers` |
| v1 리서치 카테고리 목록(명시적 호환) | `script-backed` | GET | `/api/stockSecurity/researches/v1/{company\|industry\|invest\|economy}?index=0&size=15` |
| v1 증권사 목록(명시적 호환) | `script-backed` | GET | `/api/stockSecurity/researches/v1/brokers` |
| v1 최신 리서치 블록(명시적 호환) | `script-backed` | GET | `/api/stockSecurity/researches/v1/latestResearch?size=5` |
| v1 종목별 회사 리서치(명시적 호환) | `script-backed` | GET | `/api/stockSecurity/researches/v1/company/by-items?itemCodes=005930&itemCodes=000660&size=5` |
| v1 분석 포커스(명시적 호환) | `script-backed` | GET | `/api/stockSecurity/researches/v1/analysis-focus` |

CLI 카테고리 enum은 `INVEST`, `MARKET`, `INDUSTRY`, `COMPANY`, `ECONOMY`, `DEBENTURE`이며 API path에서는 소문자 research type으로 변환합니다. 목록 응답은 `{ "hasNext": ..., "totalCount": ..., "items": [...] }` 형태입니다. `index`는 0-based 페이지 번호이므로 다음 15개는 `index=1&size=15`입니다. 발행사 페이지는 `MARKET`과 하나 이상의 반복 `brokerCodes`를 사용합니다.

2026-07-20 확인에서 기존 `/api/domestic/research/category`, 종목별 `/api/domestic/research/{itemCode}/research`, `recent-popular`, `category-lastest`, `industry-research`, `broker-list`, `/api/domestic/home/researchaggregate/static`은 route 자체가 404였습니다. 이 404는 자료 없음이 아니라 제거된 route이므로 빈 목록으로 해석하지 않습니다. 랭킹 `/api/domestic/research/ranking`은 같은 날 200을 반환해 유지했습니다.

## 종목토론 API

| 목적 | 상태 | Method | Path / params |
| --- | --- | ---: | --- |
| 인기 feed | `script-backed` | GET | `/api/community/discussion/posts/hot?pageSize=50&page=1` |
| 홈 인기 feed | `script-backed` | GET | `/api/community/discussion/posts/hot/home?pageSize=20&page=1` |
| 글 상세 | `script-backed` | GET | `/api/community/discussion/posts/{postId}` |
| 이전/다음 글 이동 | `script-backed` | GET | `/api/community/discussion/posts/{postId}/adjacent`에 선택적으로 `isHolderOnly`, `excludesItemNews`, `isItemNewsOnly`, `excludesBlockPost`, `discussionGroupType` |
| 관련 인기 글 | `script-backed` | GET | `/api/community/discussion/posts/related/hot?itemCode={itemCode}&pageSize=20&discussionType=domesticStock` |
| 인기 글 | `script-backed` | GET | `/api/community/discussion/posts/popular/hot` |
| 일반 feed | `script-backed` | GET | `/api/community/discussion/posts?pageSize=50&offset={lastOrderNo}` |
| 시장 feed | `script-backed` | GET | `/api/community/discussion/posts/market?pageSize=60&offset={lastOrderNo}&discussionGroupType={exchange\|bondInterest\|energy\|metals\|agricultural}&filterType=marketIndex` |
| 종목 글 | `observed` | GET | `/api/community/discussion/posts?itemCode={itemCode}&pageSize=20` |
| 국내 종목별 글 | `script-backed` | GET | `/api/community/discussion/posts/by-item?itemCode={itemCode}&discussionType=domesticStock&pageSize=30&isHolderOnly=false&excludesItemNews=false&isItemNewsOnly=false&offset={lastOrderNo}` |
| 코인별 Npay 글 | `script-backed` | GET | `/api/community/discussion/posts/by-item?itemCode={ticker}&discussionType={cryptoUpbit\|cryptoBithumb}&pageSize=30&isHolderOnly=false&excludesItemNews=false&isItemNewsOnly=false&isCleanbotPassedOnly=false&offset={lastOrderNo}` |
| 여러 종목 글 | `observed` | GET | `/api/community/discussion/posts/by-item-codes?filterType=itemCodes&pageSize=20&offset={offset}&domesticCodes={codes}` |
| 최신 종목 글 | `observed` | GET | `/api/community/discussion/items/posts/latest?domesticCodes={codes}&limit=10` |
| 댓글 수 | `observed` | GET | `/api/community/discussion/posts/comment-counts?postIds={ids}` |
| 반응 조회 | `observed` | GET | `/api/community/discussion/posts/reactions?postIds={ids}` |
| 랭킹 | `script-backed` | GET | `/api/community/discussion/rankings?nationType={KOR\|USA}&page=1&size=20&postType=HOT` |
| 종목 통계 | `script-backed` | GET | `/api/community/discussion/stats/by-items?startDate={yyyy-MM-dd}&domesticCodes={codes}&foreignCodes={codes}`. 2026-07-09 기준 `startDate`가 필요하고, legacy `itemCodes`만 보내는 호출은 400을 반환했습니다. |

작성, 프로필 편집, 이미지 업로드, 닉네임 검증/추천, 반응 mutation, 인증된 커뮤니티 프로필 워크플로는 피합니다.
