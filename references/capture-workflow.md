# 캡처 워크플로

요청받은 네이버증권 페이지나 하위 페이지가 [api-catalog.md](api-catalog.md)에서 연결하는 도메인 카탈로그에 없거나, 기존 엔드포인트가 실패·변경된 것으로 보일 때 사용합니다.

## 실패/변경 재확인

조회 실패, 404, 빈 응답, 응답 구조 변경, route 변경 의심이 있으면 카탈로그를 믿고 진행하지 않습니다. 현재 공개 웹앱을 다시 확인합니다.

route 자체가 404인 경우 이를 해당 종목이나 카테고리의 "자료 없음"으로 해석하지 않습니다. 빈 결과는 정상 2xx payload의 빈 `items`, `content`, `articles` 등으로만 판단합니다.

우선순위:

1. 사용자가 준 URL/path 또는 현재 공개 페이지의 실제 route.
2. 브라우저 네트워크의 `https://stock.naver.com/api/...` 요청.
3. 페이지가 로드한 Next.js 정적 chunk의 API 문자열과 enum.
4. 쿠키/인증 없이 1-2회 read-only 직접 요청.

403, 429, 차단/챌린지 페이지, 로그인 리다이렉트, 인증 쿠키 필요, 개인화 응답이면 중단합니다. 부족한 데이터를 임의의 `finance.naver.com` HTML로 메우지 않습니다. 기존 외부 소스 경계는 [external-sources.md](external-sources.md)를 따릅니다.

## 새 엔드포인트 캡처

1. 로그인하지 않은 새 브라우저 컨텍스트에서 공개 페이지를 엽니다.
2. 상단·하위 메뉴, radio/tab, 필터, 숫자 페이지, 다음/더보기 버튼을 화면에 보이는 순서대로 확인합니다. 클릭 후 URL, 선택 상태, 새 요청을 함께 기록하고, route에 `?page=`를 직접 붙인 결과를 실제 pagination 클릭과 같은 것으로 간주하지 않습니다.
3. 네트워크 요청을 `stock.naver.com/api/`로 필터링하고 정적 chunk, CSS, 텔레메트리, 광고, 이미지, 레거시 `finance.naver.com` 페이지는 데이터 API 목록에서 제외합니다. 정적 chunk는 숨은 후보와 transport 판별에만 별도로 사용합니다. 이 절차로 외부 HTML allowlist를 확장하지 않습니다.
4. 주식, 시장, 뉴스, 리서치, 가상자산, 토론 질문에 직접 답하는 GET 엔드포인트 또는 Method가 POST이지만 설명에 read-only POST라고 명시할 수 있는 공개 조회 엔드포인트만 남깁니다.
5. 읽기 POST는 로그인/쿠키/세션/개인 식별자 없이 동작하고, 같은 body를 반복 호출해도 주문·관심종목·댓글·반응·프로필·알림·계정 상태를 바꾸지 않는 조회형 호출이어야 합니다. 요청 body에 계좌, 보유종목, 토큰, 개인 데이터가 들어가면 제외합니다.
6. `auth`, `personal`, `favorite`, `holding`, `notification`, 프로필 mutation, 댓글 작성, 반응 mutation, 쿠키나 인증이 필요한 엔드포인트는 제외합니다.
7. Next.js chunk를 검사할 때는 `/api/domestic`, `/api/securityService`, `/api/securityFe`, `/api/stockSecurity`, `/api/stockDomestic`, `/api/coin`, `/api/community/discussion`, `/api/foreign/news` 문자열을 검색합니다. 리서치는 `/api/stockSecurity/researches/v2`, ETF는 `/api/stockSecurity/etfs/v2`를 우선 확인합니다.
8. 같은 chunk에서 `WebSocket`, `socket.io`, `ws://`, `wss://`, `EventSource`, `text/event-stream`도 검색합니다. 실제 네트워크 URL과 연결 조건을 확인해 공개 데이터 transport인지 구분합니다. 세션 API가 URL을 내려주거나 user/channel/holding 식별자가 필요하면 연결하지 않고 `excluded`로 기록합니다. 공통 라이브러리에 transport 구현만 존재하면 구체 endpoint로 승격하지 않습니다.
9. 공개 라이브 데이터가 `/api/polling/*`를 사용하면 WebSocket 주소를 추정하지 않습니다. 폴링 응답의 `pollingInterval` 이상을 다음 호출 전 최소 대기 간격으로 사용하고, 기존 호출 횟수 상한도 지킵니다.
10. `Accept: application/json`과 `Referer: https://stock.naver.com/`를 사용해 1-2회 소량 직접 요청만 검증합니다.
11. 관찰일과 `script-backed`, `observed`, `needs-recheck`, `excluded` 중 하나의 상태 라벨을 붙여 카탈로그에 추가합니다. `page`, `index`, `startIdx`, cursor는 이름만 보고 의미를 통일하지 말고 화면의 1·2페이지 요청 차이로 기록합니다.

원본 HAR, 쿠키, 토큰, 브라우저 스토리지는 저장하지 않습니다. 대신 민감 정보를 제거한 엔드포인트 패턴만 요약합니다.

## 완료 기준

다음을 모두 충족했을 때만 페이지 감사를 완료합니다.

- 범위에 포함된 모든 공개 링크, 탭, radio, 필터, 숫자 페이지, 다음·더보기에 정상 화면, redirect, 404, 제외 중 하나의 결과가 기록되어 있습니다.
- 모든 API 후보에 관찰 출처, 관찰일, 상태 라벨이 있고, 화면이나 chunk 근거가 없는 추정 경로는 남아 있지 않습니다.
- 각 페이징 계열은 첫 요청과 다음 요청의 차이가 기록되어 있거나, 화면에 다음 동작이 없거나 검증하지 못했다는 사실이 명시되어 있습니다.
- 변경된 route, query, enum, 기본값, 안전 경계가 해당 도메인 카탈로그와 스크립트·집중 테스트에 함께 반영되어 있습니다.
- 원본 HAR, 쿠키, 토큰, 세션·브라우저 스토리지, 개인 식별 응답을 저장하지 않았고 감사에 사용한 브라우저 탭을 정리했습니다.
