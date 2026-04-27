# 네이버증권 API 스킬 - Naver Stock Web API Skill

`naverstock-web-api`는 네이버증권(`stock.naver.com`)에서 확인되는 비공식 읽기 전용 웹 API, 내부 API, 네트워크 호출을 점검하고 사용하는 Codex 스킬이다. 네이버증권 API, 네이버 주식 API, Naver Stock API, 국내 주식 시세 API, ETF/ETN, 업종/테마/그룹사 구성 종목, 시장지표, 가상자산, 뉴스, 리서치, 종목토론 데이터를 다룬다.

네이버증권은 별도 공개 API를 제공하지 않는다. 이 저장소의 엔드포인트는 모두 공개 페이지에서 관찰한 미문서화 내부 웹 호출이며, 실제 사용 전에는 현재 `stock.naver.com` 페이지 기준으로 재검증해야 한다.

## 목차

- [주요 기능](#주요-기능)
- [설치 방법](#설치-방법)
- [사용 방법](#사용-방법)
- [스크립트 예시](#스크립트-예시)
- [문서 구성](#문서-구성)
- [검색 키워드](#검색-키워드)
- [제외 범위](#제외-범위)
- [책임 고지](#책임-고지)

## 주요 기능

- 국내 종목 상세, 현재가 폴링, 호가, 일별 시세, 체결 시세, 뉴스, 공시, IR, 투자자 통계.
- 네이버증권 업종, 테마, 그룹사 랭킹과 상세 구성 종목.
- 국내 주식 랭킹, 시가총액, 배당, IPO, ETF, ETN, 투자자 예탁금, 투자자 동향.
- KOSPI, KOSDAQ, KPI200, 원자재, 금리, 환율, 경제지표.
- 업비트/빗썸 가상자산 랭킹, 가격, 폴링, 분봉 캔들.
- 네이버증권 뉴스, 리서치 리포트, 읽기 전용 종목토론.
- 공개 `stock.naver.com/api/...` 호출 카탈로그와 캡처 워크플로.

## 설치 방법

### Codex에 설치

Codex의 스킬 디렉터리에 이 저장소를 clone한다. `CODEX_HOME`을 따로 설정하지 않았다면 기본값은 보통 `~/.codex`다.

```bash
mkdir -p "${CODEX_HOME:-$HOME/.codex}/skills"
git clone https://github.com/dd3ok/naverstock-api-skills.git \
  "${CODEX_HOME:-$HOME/.codex}/skills/naverstock-web-api"
```

이미 설치되어 있다면 최신 버전으로 갱신한다.

```bash
cd "${CODEX_HOME:-$HOME/.codex}/skills/naverstock-web-api"
git pull
```

설치 후 새 Codex 세션에서 `$naverstock-web-api`를 언급하면 스킬을 사용할 수 있다.

### 로컬 스크립트만 사용

스킬 설치 없이 스크립트만 실행하려면 저장소를 clone한 뒤 Python 3로 실행한다. 현재 스크립트는 표준 라이브러리 중심으로 작성되어 별도 패키지 설치 없이 동작하도록 구성되어 있다.

```bash
git clone https://github.com/dd3ok/naverstock-api-skills.git
cd naverstock-api-skills
python3 scripts/stock_summary.py --code 005930 --include-industry
```

### Claude, Gemini, 다른 agent 환경

이 저장소는 `SKILL.md` 중심 구조를 사용한다. Claude Code, Gemini CLI, 사내 agent처럼 로컬 지침 파일을 읽을 수 있는 환경에서는 저장소를 clone한 뒤 `SKILL.md`, `references/`, `scripts/`를 함께 참조하도록 설정한다. 각 도구의 스킬/메모리/프로젝트 지침 위치가 다르므로, 해당 도구가 지원하는 방식으로 이 폴더를 연결한다.

## 사용 방법

Codex에서 예시처럼 요청한다.

```text
$naverstock-web-api로 삼성전자 005930 네이버증권 요약과 현재가를 가져와줘.
$naverstock-web-api로 네이버증권 테마 1위 구성 종목을 확인해줘.
$naverstock-web-api로 KOSPI/KOSDAQ 주요 지수 데이터를 가져와줘.
$naverstock-web-api로 COMPANY 리서치 최신 목록을 가져와줘.
```

새 페이지나 아직 문서화되지 않은 메뉴를 점검할 때는 공개 페이지의 `stock.naver.com/api/...` 네트워크 호출만 확인한다. 로그인, 계정, 관심종목, 보유종목, 알림, 쓰기 요청은 범위에서 제외한다.

## 스크립트 예시

```bash
python3 scripts/stock_summary.py --code 005930 --include-industry
python3 scripts/stock_detail_pages.py hoga --code 005930
python3 scripts/stock_detail_pages.py notice --code 005930 --page-size 5
python3 scripts/category_detail.py stocks theme --rank 1 --page-size 10
python3 scripts/category_detail.py stocks groups --no 19 --order-type marketSum --page-size 10
python3 scripts/domestic_etf.py list --listing-type priceTop --size 10
python3 scripts/marketindex.py majors
python3 scripts/crypto.py rank --market UPBIT --page-size 10
python3 scripts/news.py list --category mainnews --page-size 10
python3 scripts/research.py category --category COMPANY --page-size 10
python3 scripts/discussion.py hot-home --page-size 10
```

더 많은 예시는 [references/script-cookbook.md](references/script-cookbook.md)를 참고한다.

## 문서 구성

- [SKILL.md](SKILL.md): 스킬 진입점, 작업 라우팅, 사용 규칙.
- [references/api-catalog.md](references/api-catalog.md): 네이버증권 API 엔드포인트 카탈로그.
- [references/script-cookbook.md](references/script-cookbook.md): 자주 쓰는 스크립트 실행 예시.
- [references/capture-workflow.md](references/capture-workflow.md): 새 페이지와 하위 페이지의 네트워크 호출 확인 절차.
- [references/response-notes.md](references/response-notes.md): 응답 형태, enum, 페이징 주의사항.
- [references/safety-rules.md](references/safety-rules.md): 책임 범위, 허용/제외 기준, 캡처 처리 규칙.
- [references/eval-prompts.md](references/eval-prompts.md): 스킬 변경 후 평가 프롬프트.
- `scripts/*.py`: 네이버증권 읽기 전용 데이터를 호출하는 도우미 스크립트.
- [agents/openai.yaml](agents/openai.yaml): OpenAI/Codex UI용 표시 메타데이터.

## 검색 키워드

이 저장소는 다음 주제와 관련된 사용자를 위해 작성되었다.

- 네이버증권 API, 네이버 주식 API, 네이버 금융 API 대체, 네이버증권 내부 API
- Naver Stock API, Naver Finance API, stock.naver.com API, Korean stock API
- 국내 주식 시세, 삼성전자 시세, KOSPI API, KOSDAQ API, ETF API, ETN API
- 네이버증권 업종, 네이버증권 테마, 테마주 구성 종목, 그룹사 구성 종목
- 네이버증권 뉴스, 네이버증권 리서치, 네이버 종목토론, 주식 데이터 수집
- Codex skill, OpenAI Codex skill, Claude skill, Gemini agent instructions

## FAQ

### 공식 네이버증권 API인가?

아니다. 공개 `stock.naver.com` 페이지에서 확인되는 비공식 읽기 전용 웹 엔드포인트를 정리한 것이다. 네이버, 네이버페이, 네이버파이낸셜, 증권사가 보증하거나 지원하는 공개 개발자 API가 아니다.

### 업종이나 테마 안의 상세 주식도 확인할 수 있나?

가능하다. `scripts/category_detail.py`가 업종(`industry`/`upjong`), 테마(`theme`), 그룹사(`groups`/`group`) 페이지의 랭킹, 상세 정보, 구성 종목을 조회한다. 단, URL의 숫자는 실제 카테고리 ID가 아니라 현재 랭킹 순번일 수 있으므로 list API로 `no`를 먼저 해석한다.

### finance.naver.com도 사용하나?

아니다. 이 저장소는 `stock.naver.com` 페이지와 `/api/` 호출만 대상으로 한다. 레거시 `finance.naver.com` HTML 스크래핑은 제외한다.

### 실시간 매매 봇에 써도 되나?

권장하지 않는다. 엔드포인트는 비공식·미문서화·불안정할 수 있고, 데이터 지연이나 필드 의미가 바뀔 수 있다. 매매, 투자 판단, 제품 연동에는 별도 검증과 공식 데이터 소스 검토가 필요하다.

## 제외 범위

- 주문, 계좌, 보유종목, 관심종목, 알림, 로그인, 인증, 프로필 수정.
- 댓글 작성, 반응 mutation, 이미지 업로드 등 쓰기 작업.
- 쿠키, 토큰, 세션, 계좌번호, 원본 HAR 저장.
- 대량 스크래핑, rate limit 우회, 접근제어 우회.
- `finance.naver.com` 레거시 HTML 스크래핑.

## 책임 고지

이 저장소는 네이버, 네이버페이, 네이버파이낸셜 또는 증권사가 보증하거나 지원하는 공식 API가 아니다. 결과는 정보 제공 목적이며 금융, 법률, 세무, 투자 조언이 아니다. 사용자와 연동 시스템은 데이터 정확성, 신선도, 약관, 라이선스, 제품 적합성을 직접 확인해야 한다.
