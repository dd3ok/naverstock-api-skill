# 캡처 워크플로

요청받은 네이버증권 페이지나 하위 페이지가 [api-catalog.md](api-catalog.md)에 아직 없을 때 사용한다.

1. 로그인하지 않은 새 브라우저 컨텍스트에서 공개 페이지를 연다.
2. 네트워크 요청을 `stock.naver.com/api/`로 필터링하고 정적 chunk, CSS, 텔레메트리, 광고, 이미지, 레거시 `finance.naver.com` 페이지는 무시한다.
3. 주식, 시장, 뉴스, 리서치, 가상자산, 토론 질문에 직접 답하는 GET 엔드포인트 또는 공개적으로 보이는 읽기 POST 엔드포인트만 남긴다.
4. `auth`, `personal`, `favorite`, `holding`, `notification`, 프로필 mutation, 댓글 작성, 반응 mutation, 쿠키나 인증이 필요한 엔드포인트는 제외한다.
5. Next.js chunk를 검사할 때는 `/api/domestic`, `/api/securityService`, `/api/securityFe`, `/api/coin`, `/api/community/discussion`, `/api/domestic/news`, `/api/domestic/research` 문자열을 검색한다.
6. `Accept: application/json`과 `Referer: https://stock.naver.com/`를 사용해 작은 직접 요청 하나를 검증한다.
7. 관찰일과 `script-backed`, `observed`, `needs-recheck`, `excluded` 중 하나의 상태 라벨을 붙여 카탈로그에 추가한다.

원본 HAR, 쿠키, 토큰, 브라우저 스토리지는 저장하지 않는다. 대신 민감 정보를 제거한 엔드포인트 패턴만 요약한다.
