# 공지·뉴스·리서치·종목토론 API

상태 라벨, page route, 전송, 식별자와 제외 기준은 [공통 API 인덱스](api-catalog.md)를 따릅니다.

`script-backed`는 CLI 래퍼가 있다는 뜻이며 현재 HTTP 성공을 보장하지 않습니다. 특히 아래 v1 리서치의 최신 404 기록과 현재 v2 대안을 함께 확인합니다.

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

2026-09-07 무인증 `size=2` 목록은 `hasNext`, `items`, `cursor` 객체를 반환했습니다. 받은 opaque cursor를 그대로 전달한 다음 목록은 다른 공지 ID 2개를 반환했고, 목록에서 얻은 ID의 상세와 `PC_TOP` 배너도 200이었습니다. 배너 응답은 최상위 배열입니다. 두 목록의 `hasNext`가 모두 true였으므로 마지막 페이지 종료까지 확인한 것은 아닙니다.

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

2026-09-07에는 목록 3개 카테고리, 포커스 6개 sid, 검색·공시 뉴스·해외뉴스 목록·집계를 낮은 요청 크기로 조회해 200을 확인했습니다. 해외뉴스는 최상위 배열의 `aid`로 상세를 조회했고, 상세의 `article.aid`가 요청 ID와 일치했습니다. 국내 목록은 `articles`, 검색은 `status`와 `items`, 공시 뉴스는 `content`를 사용하므로 공통 `items` 키 하나로 모든 목록을 해석하지 않습니다. 검색의 `status.code=0`을 관찰했지만 HTTP 200만으로 향후 응답의 애플리케이션 성공 상태까지 가정하지 않습니다.

해외뉴스의 후속 `page=1/2&pageSize=2` 응답은 aid `2732728,2732727` / `2732726,2732725`로 비중복을 확인했습니다. 삼성전자 검색에서 `startDate=endDate=2026-09-04`와 `2026-09-03`도 각각 해당 날짜 기사 2개를 반환했습니다. 검색 `datetime`은 `YYYYMMDDHHmm`이며, 같은 날짜를 양 끝에 지정한 포함 표본까지 확인한 것입니다. 자정·시간대 경계나 모든 검색 조건까지 보장하지 않습니다. 뉴스 집계의 `focusSize=1`은 포커스 카테고리 6개 각각의 뉴스 수에 적용됐으며, 최상위 `newsFocus` 길이를 1로 제한하지 않았습니다.

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
| v1 리서치 카테고리 목록(명시적 호환) | `script-backed` | GET | `/api/stockSecurity/researches/v1/{company\|industry\|invest\|economy}?index=0&size=15`. 2026-09-07 4개 경로 모두 HTTP 404 |
| v1 증권사 목록(명시적 호환) | `script-backed` | GET | `/api/stockSecurity/researches/v1/brokers`. 2026-09-07 HTTP 404 |
| v1 최신 리서치 블록(명시적 호환) | `script-backed` | GET | `/api/stockSecurity/researches/v1/latestResearch?size=5`. 2026-09-07 HTTP 404 |
| v1 종목별 회사 리서치(명시적 호환) | `script-backed` | GET | `/api/stockSecurity/researches/v1/company/by-items?itemCodes=005930&itemCodes=000660&size=5`. 2026-09-07 HTTP 404 |
| v1 분석 포커스(명시적 호환) | `script-backed` | GET | `/api/stockSecurity/researches/v1/analysis-focus`. 2026-09-07 HTTP 404 |

CLI 카테고리 enum은 `INVEST`, `MARKET`, `INDUSTRY`, `COMPANY`, `ECONOMY`, `DEBENTURE`이며 API path에서는 소문자 research type으로 변환합니다. 목록 응답은 `{ "hasNext": ..., "totalCount": ..., "items": [...] }` 형태입니다. `index`는 0-based 페이지 번호이므로 다음 15개는 `index=1&size=15`입니다. 발행사 페이지는 `MARKET`과 하나 이상의 반복 `brokerCodes`를 사용합니다.

2026-09-07에는 v2 6개 카테고리의 `index=0`과 `1`, `size=2` 응답 및 각 카테고리에서 얻은 ID의 상세가 모두 200이었습니다. 후속 감사에서는 첫·다음 nid를 함께 기록해 6개 모두 비중복을 확인했고, 응답 totalCount로 계산한 마지막 index도 1~2행과 `hasNext=false`를 반환했습니다. 목록의 공개 리포트 ID 필드는 `nid`이고, 랭킹의 `latestResearch`는 `researchId`를 사용합니다. API type `market`은 화면의 `/research/daily`에 대응합니다. totalCount는 조회 사이 변할 수 있으며 표본 경계 검증을 중간 모든 페이지의 무누락 보증으로 확대하지 않습니다.

`industryTypes=it&index=0&size=2`는 공개 목록에서 관찰한 산업 코드로 확인했으며, 200 응답의 두 항목 모두 `industry=it`였습니다. 현재 화면에서 IT 필터를 적용한 `/research/industry?industryType=IT`의 첫 리포트 ID도 API 표본과 일치했습니다. 화면 query의 대문자 `IT`와 API의 소문자 `it`를 구분합니다. `brokerCodes=60&brokerCodes=55`를 보낸 MARKET 목록은 유효한 증권사 코드였지만 `items=[]`, `totalCount=0`, `hasNext=false`였습니다. 목표주가 `direction=down`도 200과 빈 `researchSets`를 반환했습니다. 이런 빈 결과는 아래 v1의 경로 404와 구분하며, 다른 필터값·기간에서의 비어 있지 않은 결과까지 보장하지 않습니다.

v1 8개 경로는 CLI 명령이 남아 있어 `script-backed`로 표시하지만 현재 표본 요청은 조회 불가(404)였습니다. 크기 인자가 있는 요청은 `size=2`, 카테고리는 `index=0`으로 확인했습니다. `v1-category` 대신 명시적으로 `category`, `v1-brokers` 대신 `broker-list`, `v1-latest` 대신 `latest`, `v1-by-items` 대신 `by-items`, `v1-analysis-focus` 대신 `analysis-focus`를 선택하면 위 v2 계열을 사용합니다. 명령별 옵션은 cookbook을 따릅니다. 실패한 v1을 자동으로 v2나 레거시 응답으로 바꾸지 않으며, 404를 빈 데이터로 숨기지 않습니다.

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
| 일반 글 feed의 과거 종목 query | `observed` | GET | `/api/community/discussion/posts?itemCode={itemCode}&pageSize=20`. 2026-09-07 다른 종목 반환을 재현하여 공통 helper가 이 query를 요청 전에 거부. 종목 조회는 `/posts/by-item` 사용 |
| 국내 종목별 글 | `script-backed` | GET | `/api/community/discussion/posts/by-item?itemCode={itemCode}&discussionType=domesticStock&pageSize=30&isHolderOnly=false&excludesItemNews=false&isItemNewsOnly=false&offset={lastOrderNo}` |
| 코인별 Npay 글 | `script-backed` | GET | `/api/community/discussion/posts/by-item?itemCode={ticker}&discussionType={cryptoUpbit\|cryptoBithumb}&pageSize=30&isHolderOnly=false&excludesItemNews=false&isItemNewsOnly=false&isCleanbotPassedOnly=false&offset={lastOrderNo}` |
| 여러 종목 글 | `observed` | GET | `/api/community/discussion/posts/by-item-codes?filterType=itemCodes&pageSize=20&offset={offset}&domesticCodes={codes}` |
| 최신 종목 글 | `observed` | GET | `/api/community/discussion/items/posts/latest?domesticCodes={codes}&limit=10` |
| 댓글 수 | `observed` | GET | `/api/community/discussion/posts/comment-counts?postIds={ids}` |
| 반응 조회 | `observed` | GET | `/api/community/discussion/posts/reactions?postIds={ids}` |
| 랭킹 | `script-backed` | GET | `/api/community/discussion/rankings?nationType={KOR\|USA}&page=1&size=20&postType=HOT` |
| 종목 통계 | `script-backed` | GET | `/api/community/discussion/stats/by-items?startDate={yyyy-MM-dd}&domesticCodes={codes}&foreignCodes={codes}`. 2026-07-09 기준 `startDate`가 필요하고, legacy `itemCodes`만 보내는 호출은 400을 반환했습니다. |

작성, 프로필 편집, 이미지 업로드, 닉네임 검증/추천, 반응 mutation, 인증된 커뮤니티 프로필 워크플로는 피합니다.

2026-09-07 미구현 관찰 경로도 구분해 호출했습니다. 리서치 `company/96027/detail-page?itemCode=005930&size=1`은 200이며 `researchContent.nid=96027`, `itemCode=005930`과 인접 `researchSummaries`를 반환했습니다. 토론 `/posts?itemCode=005930`는 200이어도 다른 종목 `386380`, `066980`의 글을 반환해 종목 필터가 적용됐다고 볼 수 없었습니다. 반면 `/posts/by-item-codes?filterType=itemCodes&domesticCodes=005930&pageSize=2`와 `/items/posts/latest?domesticCodes=005930&limit=2`는 요청한 종목 글을 반환했습니다. 댓글 수와 반응 GET의 공개 postId도 요청값과 일치했습니다. 이들은 CLI 미구현이므로 `observed`를 유지하며 반응 작성·인증된 이용자 상태는 조회하지 않습니다.

2026-09-07 공개 feed·종목별 글·시장 5개 그룹·상세·인접 글·관련 인기 글·랭킹을 무인증으로 조회해 200을 확인했습니다. 일반 feed의 공개 글 ID는 `posts[].id`, 랭킹 안의 글과 [CMC feed](api-crypto.md)는 `postId`를 사용합니다. `discussion.py` 출력은 개인정보 제거 helper를 통과하며 작성자·프로필·회원 식별자를 상세나 페이징 ID로 사용하지 않습니다.

랭킹 응답은 `contents`에 표본 2개가 있고 `items=[]`도 함께 있어, 빈 items만 보고 랭킹 전체를 빈 결과로 해석하면 안 됩니다. 표본 통계 요청의 `domestic=[]`, `foreign=[]`와 뉴스 전용 필터를 적용한 인접 글의 `nextPost=null`, `prevPost=null`은 모두 HTTP 200의 빈 결과였습니다. 이는 경로 실패가 아니며, 통계 수치나 모든 필터 조합의 의미를 검증한 것도 아닙니다.

같은 날 일반 feed, `filterType=marketIndex` 시장 feed, BTC `cryptoUpbit` feed에서 `pageSize=2` 응답의 마지막 `posts[].orderNo`를 계산 없이 그대로 `offset`으로 전달했습니다. 각각의 다음 요청은 200이었고 첫 응답과 겹치지 않는 글 ID 2개를 반환했습니다. CMC BTC feed도 마지막 `items[].postTime`을 그대로 `offsetPostTime`으로 전달해 다른 postId 2개와 더 이전 postTime을 확인했습니다. CMC의 다음 응답은 여전히 `hasNext=true`였습니다. 이는 표본별 다음 묶음 진행의 검증이며 끝 페이지, 모든 시장 그룹, `cryptoBithumb`까지 같은 방식으로 확인한 것은 아닙니다.
