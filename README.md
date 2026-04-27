# 네이버증권 API 스킬

`naverstock-web-api`는 공개 `stock.naver.com` 페이지에서 확인되는 비공식 읽기 전용 웹 엔드포인트를 점검하고 호출하기 위한 Codex 스킬이다. 국내 주식, 업종/테마/그룹사 구성 종목, ETF/ETN, 지수/시장지표, 가상자산, 뉴스, 리서치, 종목토론 데이터를 다룬다.

네이버증권은 별도 공개 API를 제공하지 않으므로, 이 저장소의 엔드포인트는 모두 미문서화 내부 웹 호출이다. 실제 사용 전에는 현재 페이지 기준으로 재검증해야 한다.

## 구성

- [SKILL.md](SKILL.md): 스킬 진입점과 작업 라우팅.
- [references/api-catalog.md](references/api-catalog.md): 관찰한 엔드포인트 카탈로그.
- [references/script-cookbook.md](references/script-cookbook.md): 자주 쓰는 스크립트 실행 예시.
- [references/safety-rules.md](references/safety-rules.md): 책임 범위, 허용/제외 기준, 캡처 처리 규칙.
- `scripts/*.py`: 네이버증권 읽기 전용 데이터를 호출하는 도우미 스크립트.
- [agents/openai.yaml](agents/openai.yaml): OpenAI/Codex UI용 표시 메타데이터.

## 주요 범위

- 국내 종목 상세, 현재가 폴링, 호가, 일별/체결 시세, 뉴스, 공시, IR, 투자자 통계.
- 업종, 테마, 그룹사 랭킹과 상세 구성 종목.
- 국내 주식 랭킹, 배당, IPO, ETF, ETN, 투자자 예탁금, 투자자 동향.
- KOSPI/KOSDAQ/KPI200, 원자재, 금리, 환율, 경제지표.
- 업비트/빗썸 가상자산 랭킹, 가격, 폴링, 캔들.
- 네이버증권 뉴스, 리서치, 읽기 전용 종목토론.

## 예시

```bash
python3 scripts/stock_summary.py --code 005930 --include-industry
python3 scripts/category_detail.py stocks theme --rank 1 --page-size 10
python3 scripts/domestic_etf.py list --listing-type priceTop --size 10
python3 scripts/marketindex.py majors
python3 scripts/crypto.py rank --market UPBIT --page-size 10
python3 scripts/news.py list --category mainnews --page-size 10
python3 scripts/research.py category --category COMPANY --page-size 10
```

## 제외 범위

- 주문, 계좌, 보유종목, 관심종목, 알림, 로그인, 인증, 프로필 수정.
- 댓글 작성, 반응 mutation, 이미지 업로드 등 쓰기 작업.
- 쿠키, 토큰, 세션, 계좌번호, 원본 HAR 저장.
- 대량 스크래핑, rate limit 우회, 접근제어 우회.
- `finance.naver.com` 레거시 HTML 스크래핑.

## 책임 고지

이 저장소는 네이버, 네이버페이, 네이버파이낸셜 또는 증권사가 보증하거나 지원하는 공식 API가 아니다. 결과는 정보 제공 목적이며 금융, 법률, 세무, 투자 조언이 아니다. 사용자와 연동 시스템은 데이터 정확성, 신선도, 약관, 라이선스, 제품 적합성을 직접 확인해야 한다.
