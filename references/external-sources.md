# 외부 공개 소스

`stock.naver.com` JSON API로 답할 수 없을 때도 임의의 HTML fallback을 만들지 않습니다. 아래 두 스크립트와 고정된 host/path/query allowlist만 사용합니다.

## 선택 순서

1. 같은 의미의 `stock.naver.com` JSON API가 있으면 그 API와 기존 스크립트를 사용합니다.
2. 현재 종목 정보 페이지가 연결하는 기업분석 탭이면 `scripts/wisereport.py`를 사용합니다.
3. 신버전에 대응 화면이 없는 조건검색 7종이면 `scripts/legacy_screeners.py`를 사용합니다.
4. 그 밖의 `finance.naver.com`, WiseReport 또는 외부 iframe 요청은 지원 범위로 추정하지 않습니다.

두 스크립트는 쿠키·인증 헤더를 보내지 않으며 GET만 사용합니다. 응답은 5 MiB, 타임아웃은 60초로 제한하고, 다른 host/path로 redirect되면 중단합니다. HTTP 403·429는 자동 재시도하지 않습니다.

## WiseReport v3

현재 네이버 증권 종목 정보 페이지가 연결하는 `navercomp.wisereport.co.kr/v3/company/` 공개 iframe입니다. 네이버 증권 JSON API가 아니며 별도 외부 소스임을 결과에 표시합니다.

| `--kind` | 화면 의미 | 고정 경로 |
| --- | --- | --- |
| `status` | 기업현황 | `c1010001.aspx` |
| `overview` | 기업개요 | `c1020001.aspx` |
| `financial-analysis` | 재무분석 | `c1030001.aspx` |
| `indicators` | 투자지표 | `c1040001.aspx` |
| `consensus` | 컨센서스 | `c1050001.aspx` |
| `industry` | 업종분석 | `c1060001.aspx` |
| `shareholders` | 주주현황 | `c1070001.aspx` |
| `sector` | 섹터분석 | `c1090001.aspx` |

표는 원본 순서의 2차원 `rows`로 내보냅니다. `rowspan`·`colspan`으로 합쳐진 머리글은 추정해서 재구성하지 않습니다. `--max-tables`는 1~50, `--max-rows`는 표당 1~500입니다.

## 레거시 조건검색

정확히 다음 7개 `finance.naver.com` 공개 HTML 화면만 허용합니다.

| 명령 | 종류 | 시장 선택 |
| --- | --- | --- |
| `technical` | `golden-cross`, `gap-up`, `disparity-overheat`, `sentiment-overheat`, `relative-strength-overheat` | 없음. 원본 화면이 시장 selector를 제공하지 않음 |
| `price-position` | `low-up`, `high-down` | `KOSPI`, `KOSDAQ` |

`low-up`의 첫 지표는 `저가대비등락률`, `high-down`의 첫 지표는 `고가대비등락률`로 출력해 같은 표의 일간 `등락률`과 구분합니다. `--limit`은 원격 페이징 크기를 바꾸지 않고 해당 페이지에서 내보낼 행만 제한합니다.

실행 예시는 [script-cookbook.md](script-cookbook.md)에만 둡니다.

## 의도적으로 제외하는 레거시 범위

- 현재 JSON API와 중복되는 시세, 차트, 수급, ETF/ETN, 업종/테마, 리서치, 환율과 해외지수 HTML.
- 장외시장·포토·TV 뉴스와 기사/PDF 본문의 대량 수집.
- DART·KRX 등 다른 제공자의 iframe을 네이버 API처럼 감싸는 기능.
- WiseReport v2, 임의 URL, 임의 query, 로그인·개인화·mutation 경로.

전체 레거시 구현을 비교할 때만 [dd3ok/naverfinance-api-skill](https://github.com/dd3ok/naverfinance-api-skill)을 참고합니다. 이 저장소로 코드를 되돌리는 fallback으로 사용하지 않습니다.
