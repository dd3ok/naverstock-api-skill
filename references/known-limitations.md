# 알려진 제한과 검증 범위

기준일: 2026-09-07 후속 실검증. 상태는 아래 요청 조건에 한정하며 네이버의 영구 지원 계약이 아닙니다. HTTP 200, 올바른 상품·필터 결과, 페이징 완료, 수치 정확성은 별도 판정입니다.

## 실패 또는 의미 불일치가 확인된 조건

| 조건 | 관찰 및 처리 | 사용 방법 |
| --- | --- | --- |
| 일반 토론 `/posts?itemCode=005930&pageSize=2` | 200이지만 다른 종목 `005380`, `028300` 반환. 공통 요청 helper는 이 잘못된 필터를 네트워크 요청 전에 거부 | `discussion.py item-posts --item-code 005930 --page-size 2`. 기존 `feed` 명령은 원래 종목 옵션을 받지 않았으며 전용 명령도 이미 `/posts/by-item` 사용 |
| 리서치 v1 8개 경로 | 앞선 감사에서 모두 404, 후속 company 재현도 404. 실패 시 v2 명령 안내 | `research.py category`, `broker-list`, `latest`, `by-items`, `analysis-focus`. v1 `index=0`은 v2 CLI `--page 1`; 옵션·응답 차이 확인. [리서치 계약](api-content.md) |
| 시장지표 bare `/exchange`, `/bond` | 후속 재현도 404. 오류에 용도별 대안 안내 | 환율 전체는 `marketindex.py exchange-list`; 요약은 `major-block --block-type exchange` 또는 `bond`. 요약 5개가 전체 목록을 대신하지 않음 |
| 환율 폴링 `exchange/FX_USDKRW` | 후속 재현도 404 | `marketindex.py detail --category exchange --code FX_USDKRW`는 200인 일회 조회. 폴링 구조·갱신 주기를 보장하지 않음. `.DXY`는 다른 지표이므로 대체 불가 |
| 업종·테마·그룹 종목의 `sales`, `operatingProfit` 정렬 | 실제 ID `307`, `155`, `14` × 두 정렬, `marketType=ALL&startIdx=0&pageSize=2`가 다시 500. 같은 조건의 `marketSum`은 200 | 현재 UI 정렬 `marketSum`, `accAmount`, `up`, `down`, `accQuant` 사용. 재무 정렬 입력은 호환 유지하고 실패 시 안내. 임의 정렬 변경이나 첫 페이지 안에서의 재정렬로 전체 순위를 가장하지 않음 |
| 해외 주목 ETF `return1Month`에서 테마 생략 | `startIdx=0&pageSize=2`가 다시 500. 동일 조건에 `middleCode=0101` 추가 시 200 | `foreign_stock.py etf-themes`에서 원하는 테마 선택 후 `home.py notable-etf --nation foreign --order-type return1Month --middle-code CODE`. 임의 테마 삽입·자동 재시도 없음 |
| 통합 가격 `foreignCodes=.IXIC` | 200이지만 `foreign={}`. `foreignCodes=NVDA.O`는 해당 주식 정보 반환 | 지수에는 검증한 `foreign_stock.py index-basic --code .IXIC` 사용. 통합 가격의 해외 주식과 지수 지원을 구분 |

실패 안내는 확인한 경로·상태·정렬 조합에만 붙입니다. HTTP 상태, 요청 경로, 원격 오류 detail, 예외 종류는 유지합니다. 정상 응답은 그대로 반환하므로 향후 네이버가 해당 요청을 복구했을 때 과거 실패 기록만으로 성공 응답을 차단하지 않습니다. 토론의 잘못된 종목 필터 거부는 의도적인 입력 제한이며 이를 재허용하려면 실제 필터 적용을 재검증해야 합니다.

현재 [홈](https://stock.naver.com/)에서 미국 ETF의 테마를 바꾸면 해당 테마의 1개월 수익률 순서로 표시됩니다. [업종 상세](https://stock.naver.com/market/stock/kr/industry/1?no=278)의 매출액·영업이익은 표시 열이며 현재 정렬 메뉴와 다릅니다. 표시 열의 이름을 API 정렬값으로 추정하지 않습니다. 페이지와 현재 로드되는 chunk를 대조했지만 실패 응답만으로 네이버 내부 원인까지 확정할 수는 없습니다.

## 후속 검증으로 해소한 공백

| 검증 대상 | 확인한 결과 | 범위 |
| --- | --- | --- |
| 리서치 6개 카테고리 | `size=2`, `index=0/1`의 nid 비중복. 응답 totalCount로 계산한 마지막 index도 200, 1~2행, `hasNext=false` | COMPANY/INDUSTRY/INVEST/MARKET/ECONOMY/DEBENTURE, 무필터 표본. 중간 모든 페이지의 무누락을 입증한 것은 아님 |
| 해외뉴스 | `page=1/2&pageSize=2`의 aid가 각각 `2732728,2732727` / `2732726,2732725`로 비중복 | 표본 다음 페이지. 전체 과거 뉴스의 끝 페이지는 미검증 |
| 뉴스 날짜 검색 | 삼성전자, `page=1&pageSize=2`, startDate=endDate를 09-04와 09-03으로 설정하자 각각 해당 날짜 기사 반환 | `datetime`은 `YYYYMMDDHHmm`. 날짜의 포함 표본 확인이며 정확한 자정·시간대 경계까지 확정하지 않음 |
| 미국 섹터 랭킹 | `sortType=changeRate`와 `marketCap`, `period=daily&size=2`, 서버 cursor를 그대로 전달해 다음 코드 비중복·cursor 전진 확인 | 첫·다음 묶음. 필터 전환 시 cursor 재사용 금지, 끝 페이지 미검증 |
| 펀드 클래스 | 검색에서 얻은 `K55301B35070`의 classes 7행 확인. 성과분석의 ‘다른 클래스 보기’와 표의 7개 연결도 확인 | 기존 빈 배열 표본과 값이 있는 분기 모두 확인. 전체 펀드·수익률 정확성 검증은 아님 |

## 여전히 확인 범위가 제한된 항목

- 펀드 목록·테마 후보는 현재 진입 화면과 유효한 enum을 확정하지 못해 `needs-recheck` 및 CLI 미노출을 유지합니다. 이름 검색에는 검증된 `search.py search --query 펀드 --target fund`를 사용하고 실제 결과 코드로 상세를 조회합니다.
- 공지·토론·CMC 등 cursor 목록은 다음 묶음 검증과 전체 종료 검증을 구분합니다. 전 이력을 수집해 종료를 강제로 확인하지 않습니다. 모든 시장 그룹, Bithumb 토론, 홈 집계 필터 조합이 검증된 것은 아닙니다.
- IR은 실제 목록의 BOARD 식별자만 검증됐습니다. 숫자·PLAN 식별자를 추측해 호출하지 않습니다.
- WiseReport는 고정 v3 8개 HTML 응답과 제한된 표 파싱 범위입니다. 동적으로 로드되는 재무표·필터·모든 셀의 정확성까지 검증된 것이 아닙니다.
- 가격·통화·단위·수익률 전체를 독립 원천과 대조하거나 재계산하지 않았습니다. 정상 JSON과 스키마만으로 데이터 정확성·미래 가용성을 보증하지 않습니다.

## 다음 수정의 완료 기준

1. 해당 조건의 현재 UI·query·응답을 기록하고 이전 기록과 한 변수씩 비교합니다. 403·429·인증 요구·redirect에는 중단합니다.
2. 잘못된 데이터 선택은 명시적으로 거부하거나 검증된 별도 명령으로 안내합니다. 기존 성공 계약·기본값·페이징·출력 형식은 유지합니다.
3. 수정한 오류를 재현하는 집중 테스트, 정상/빈 응답·관련 없는 실패·요청 횟수 검증, 변경 조건의 실응답을 확인합니다.
4. 공개 문서의 상태를 갱신하고 로컬 전략 문서에 재현·처리·검증·남은 범위를 연결합니다. 미확인 항목의 기록만으로 그 항목을 검증 완료 처리하지 않습니다.
