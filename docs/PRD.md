# PRD — 장바구니 할인 계산기 (cursor-tdd-cart)

| 항목 | 내용 |
|------|------|
| **문서 버전** | 1.0 |
| **작성일** | 2026-06-24 |
| **근거 문서** | [Report/01.REPORT.md](../Report/01.REPORT.md), [Report/02.REPORT.md](../Report/02.REPORT.md), [Prompting/01.Export-Transcript.md](../Prompting/01.Export-Transcript.md), [Prompting/02.Export-Transcript.md](../Prompting/02.Export-Transcript.md) |
| **상태** | Discovery 완료 · Entity 계약 확정 · 구현 전 |

---

## 1. 개요

### 1.1 제품 목적

주문 품목(단가·수량)과 고객 유형(VIP 여부)을 입력받아 **최종 결제 금액**을 계산하는 장바구니 할인 계산기.

- **Entity**: 순수 할인 로직 (`src/cart.py`)
- **Boundary**: Flask 주문 폼 (`src/app.py`) — *입력 사례 확보 전 OOS*

### 1.2 Discovery 방법

MomTest 기반 Product Discovery로 실제 사례에서만 계약을 추출한다.

- 계약 ID(`INV-*`, `AC-*`, `E-*`)가 테스트·구현의 추적 못
- **ID에 없는 동작은 구현하지 않는다**
- 근거 없는 기능은 `OOS-*`로 명시하고 제외한다

### 1.3 인터뷰 근거 (원문)

**인터뷰 메모**

- 2024-03-12: A 3개(12,000원) + B 1개(30,000원) = 66,000원. 5만 원 넘으면 10% 할인. 기대 59,400원.
- VIP 고객은 문턱 할인 후 추가 5% 할인. 순서는 문턱 → VIP 고정.

**실제 주문 사례**

- #1107: 소계 60,000 → 결제 54,000 (10% 할인)

---

## 2. 범위

### 2.1 In Scope (v1 — Entity)

| ID | 요약 |
|----|------|
| INV-001 | 소계 = Σ(단가 × 수량) |
| AC-001 | 소계 > 50,000원 → 10% 할인 |
| INV-002 | 할인 순서: 문턱 → VIP 고정 |
| AC-002 | VIP → 문턱 후 추가 5% |
| AC-003 | 비-VIP → AC-001과 동일 |

### 2.2 Out of Scope (OOS)

| OOS ID | 제외 동작 | 제외 이유 |
|--------|----------|----------|
| OOS-001 | `subtotal == 50000` 할인 여부 | 사례 없음 |
| OOS-002 | `subtotal <= 50000` 원금 반환 | 사례 없음 |
| OOS-003 | 비정수 결과 반올림 규칙 | 정수 사례만 존재 |
| OOS-004 | VIP + 소계 ≤ 50,000 | 사례 없음 |
| OOS-005 | VIP만, 문턱 미적용 | 사례 없음 |
| OOS-006 | `E-*` 입력 오류 계약 | 실패 사례 미제공 |
| OOS-007 | 쿠폰·세금·배송비·포인트 | 언급 없음 |
| OOS-008 | Flask `app.py` Boundary | UI·입력 경로 사례 없음 |

---

## 3. 도메인 규칙 (테스트 가능 계약)

### 3.1 불변식 (Invariant)

#### INV-001 — 소계 합산

| 항목 | 내용 |
|------|------|
| **계약** | `subtotal(items) == sum(price_i * qty_i for each item i)` |
| **근거 레벨** | L1 |
| **근거** | 2024-03-12: (12,000×3) + (30,000×1) = 66,000 |
| **계층** | Entity (`src/cart.py`) |
| **테스트** | `[(12000, 3), (30000, 1)]` → `66000` |

#### INV-002 — 할인 적용 순서

| 항목 | 내용 |
|------|------|
| **계약** | VIP 할인이 있으면, 문턱 할인(해당 시)을 적용한 **이후** 금액에 VIP 할인을 적용한다. 순서 변경 금지. |
| **근거 레벨** | L2 |
| **근거** | 인터뷰: "순서는 문턱 → VIP 고정" |
| **계층** | Entity |
| **테스트** | VIP 경로에서 문턱 선적용 후 ×0.95; 잘못된 순서와 결과 비교 |

### 3.2 수용 기준 (Acceptance Criteria)

#### AC-001 — 문턱 10% 할인

| 항목 | 내용 |
|------|------|
| **계약** | `subtotal > 50000`이면 `subtotal * 0.9`를 반환한다. |
| **근거 레벨** | L1 |
| **근거** | 2024-03-12 (66,000→59,400), #1107 (60,000→54,000) |
| **계층** | Entity |
| **테스트** | `66000` → `59400`; `60000` → `54000` |

> **문턱 해석**: 「5만 원 넘으면」→ `>` (초과). `=50000` 동작은 OOS-001.

#### AC-002 — VIP 추가 5% 할인

| 항목 | 내용 |
|------|------|
| **계약** | `is_vip == True`이면 INV-002 순서로 최종 금액에 `× 0.95`를 적용한다. |
| **근거 레벨** | L2 |
| **근거** | 인터뷰: "문턱 할인 후 추가 5% 할인" |
| **계층** | Entity |
| **테스트** | `subtotal=66000, vip=True` → `56430` *(규칙 검산; VIP 실결제 사례는 미제공)* |

#### AC-003 — 비-VIP 경로

| 항목 | 내용 |
|------|------|
| **계약** | `subtotal > 50000`이고 `is_vip == False`이면 AC-001 결과와 동일하다. |
| **근거 레벨** | L2 |
| **근거** | #1107 (비-VIP로 해석 가능한 10% 단일 할인) |
| **계층** | Entity |
| **테스트** | `60000, vip=False` → `54000` |

### 3.3 검산표

| 사례 | 입력 | 계산 | 기대 결제액 | 근거 |
|------|------|------|------------|------|
| 2024-03-12 | A×3(12,000) + B×1(30,000), VIP=False | 66,000 × 0.9 | **59,400** | 인터뷰 |
| #1107 | 소계 60,000, VIP=False | 60,000 × 0.9 | **54,000** | 실제 주문 |
| VIP 가설 | 소계 66,000, VIP=True | 66,000 × 0.9 × 0.95 | **56,430** | 규칙 문장 *(수치 사례 없음)* |

---

## 4. 미확정 항목 (Discovery 잔여)

다음 사례가 수집되기 전까지 계약 ID를 부여하지 않는다.

1. 소계 **정확히 50,000원**인 주문 — 할인 적용 여부
2. 소계 **50,000원 이하** 주문 — 원금 반환 여부
3. **VIP 실결제** 사례 (품목·중간 금액·결제액)
4. VIP + 소계 ≤ 50,000 조합
5. **1원 단위 반올림**이 필요한 사례
6. 빈 장바구니·음수·누락 등 **잘못된 입력** 실패 사례

---

## 5. 기술 요구사항

### 5.1 스택

| 구분 | 기술 |
|------|------|
| 언어 | Python 3.12 |
| 테스트 | pytest (Dual-Track) |
| Boundary (향후) | Flask + Jinja2 |
| 워크플로 | RED → GREEN → REFACTOR (ARRR) |

### 5.2 아키텍처 (ECB)

```
src/cart.py          Entity   — 순수 로직, Flask import 금지
src/app.py           Boundary — Flask 주문 폼 (OOS-008)
tests/entity/        INV-*, AC-* 검증
tests/boundary/      E-*, UC-* 검증 (사례 확보 후)
```

### 5.3 구현 규칙

- 모든 구현 줄에 충족한 계약 ID 주석 (`# INV-001` 등)
- RED: `tests/`만 수정 · GREEN: 최소 구현 · REFACTOR: 통과 후 구조 정리
- 커밋 분리: `test(RED)` / `feat(GREEN)` / `refactor` — 메시지에 계약 ID 포함
- `assert True`, `pytest.skip`, 예외 삼키기 금지

### 5.4 테스트 명령

```bash
pytest -q                    # 전체
pytest tests/entity -q       # Entity만
pytest tests/boundary -q     # Boundary만
```

---

## 6. 구현 로드맵

### Phase 0 — 환경 (완료)

- [x] 프로젝트 스캐폴드, `AGENTS.md`, Cursor Rules
- [x] pytest 설정 (`conftest.py`, `pytest.ini`)
- [x] MomTest Discovery · 계약 ID 정의

*출처: [Report/01.REPORT.md](../Report/01.REPORT.md), [Report/02.REPORT.md](../Report/02.REPORT.md)*

### Phase 1 — Entity TDD (다음)

- [ ] RED: `INV-001` 소계 합산 (`tests/entity/`)
- [ ] RED: `AC-001` 문턱 10% 할인
- [ ] GREEN: `src/cart.py` 최소 구현
- [ ] RED: `INV-002` + `AC-002` VIP 순서·5%
- [ ] RED: `AC-003` 비-VIP 경로
- [ ] REFACTOR: `pytest -q` 동작 불변 확인

### Phase 2 — Discovery 보완

- [ ] 잔여 MomTest 질문 6건 인터뷰
- [ ] OOS-001~006 해제 여부 판단 → 신규 계약 ID 부여

### Phase 3 — Boundary (사례 확보 후)

- [ ] `src/app.py` Flask 스캐폴드
- [ ] `tests/boundary/` 입력·UI 계약 (`E-*`)

---

## 7. 성공 기준

| 기준 | 측정 |
|------|------|
| 계약 추적 | 모든 테스트·구현이 `INV-*` / `AC-*` ID 참조 |
| 검산 일치 | 59,400원·54,000원 사례 통과 |
| VIP 규칙 | `66000, vip=True` → `56430` |
| 과잉 구현 없음 | OOS 항목 미구현 |
| 테스트 통과 | `pytest -q` 전체 green |

---

## 8. 참고

| 문서 | 설명 |
|------|------|
| [AGENTS.md](../AGENTS.md) | 저장소 지도 · ECB · ARRR 워크플로 |
| [Report/01.REPORT.md](../Report/01.REPORT.md) | Session 01 — 환경 구축 |
| [Report/02.REPORT.md](../Report/02.REPORT.md) | Session 02 — MomTest 계약 추출 |
| [Prompting/02.Export-Transcript.md](../Prompting/02.Export-Transcript.md) | Discovery 대화 전문 |
| [GitHub #1](https://github.com/CUNACUNA/cursor-tdd-cart/issues/1) | Cursor.AI 활용 가이드 |

---

*본 문서는 docs/PRD.md — Report·Prompting 세션 산출물을 통합한 제품 요구사항 정의서입니다.*
