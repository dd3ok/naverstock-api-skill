# 캡처 워크플로

요청받은 네이버증권 페이지나 하위 페이지가 [api-catalog.md](api-catalog.md)에 없거나, 기존 엔드포인트가 실패/변경된 것으로 보일 때 사용합니다.

## 실패/변경 재확인

조회 실패, 404, 빈 응답, 응답 구조 변경, route 변경 의심이 있으면 카탈로그를 믿고 진행하지 않습니다. 현재 공개 웹앱을 다시 확인합니다.

우선순위:

1. 사용자가 준 URL/path 또는 현재 공개 페이지의 실제 route.
2. 브라우저 네트워크의 `https://stock.naver.com/api/...` 요청.
3. 페이지가 로드한 Next.js 정적 chunk의 API 문자열과 enum.
4. 쿠키/인증 없이 1-2회 read-only 직접 요청.

403, 429, 차단/챌린지 페이지, 로그인 리다이렉트, 인증 쿠키 필요, 개인화 응답이면 중단합니다. 부족한 데이터는 `finance.naver.com` HTML로 메우지 않습니다. 구버전 네이버증권은 [dd3ok/naverfinance-api-skills](https://github.com/dd3ok/naverfinance-api-skills)로 안내합니다.

## 새 엔드포인트 캡처

1. 로그인하지 않은 새 브라우저 컨텍스트에서 공개 페이지를 엽니다.
2. 네트워크 요청을 `stock.naver.com/api/`로 필터링하고 정적 chunk, CSS, 텔레메트리, 광고, 이미지, 레거시 `finance.naver.com` 페이지는 무시합니다. 구버전 네이버 증권 페이지가 필요하면 [dd3ok/naverfinance-api-skills](https://github.com/dd3ok/naverfinance-api-skills)를 참고합니다.
3. 주식, 시장, 뉴스, 리서치, 가상자산, 토론 질문에 직접 답하는 GET 엔드포인트 또는 카탈로그에 `read-post`로 설명할 수 있는 공개 읽기 POST 엔드포인트만 남깁니다.
4. 읽기 POST는 로그인/쿠키/세션/개인 식별자 없이 동작하고, 같은 body를 반복 호출해도 주문·관심종목·댓글·반응·프로필·알림·계정 상태를 바꾸지 않는 조회형 호출이어야 합니다. 요청 body에 계좌, 보유종목, 토큰, 개인 데이터가 들어가면 제외합니다.
5. `auth`, `personal`, `favorite`, `holding`, `notification`, 프로필 mutation, 댓글 작성, 반응 mutation, 쿠키나 인증이 필요한 엔드포인트는 제외합니다.
6. Next.js chunk를 검사할 때는 `/api/domestic`, `/api/securityService`, `/api/securityFe`, `/api/coin`, `/api/community/discussion`, `/api/domestic/news`, `/api/domestic/research` 문자열을 검색합니다.
7. `Accept: application/json`과 `Referer: https://stock.naver.com/`를 사용해 1-2회 소량 직접 요청만 검증합니다.
8. 관찰일과 `script-backed`, `observed`, `needs-recheck`, `excluded` 중 하나의 상태 라벨을 붙여 카탈로그에 추가합니다.

원본 HAR, 쿠키, 토큰, 브라우저 스토리지는 저장하지 않습니다. 대신 민감 정보를 제거한 엔드포인트 패턴만 요약합니다.
