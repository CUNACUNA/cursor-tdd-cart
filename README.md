# Cart Discount TDD Practice

## 목적

이 프로젝트는 **장바구니 할인 계산 로직**을 TDD(Test-Driven Development) 방식으로 구현하는 연습 프로젝트입니다.

도메인 로직은 `src/cart.py`의 Entity 계층에 위치합니다. 테스트와 구현은 **계약 ID**를 기준으로 작성·추적하며, 각 계약 ID는 테스트와 구현을 잇는 **추적의 못** 역할을 합니다.

현재 단계는 **1차 GREEN**입니다. 소계(INV-1)와 입력 검증(E-1, E-2)까지 구현되었고, 할인·최종 금액(INV-2~4)은 RED 대기 중입니다.

## Release Notes — v0.1.0 (소계 GREEN)

**장바구니 소계 계산(INV-1)과 입력 검증(E-1, E-2)을 TDD 1차 GREEN으로 구현했습니다.**

> 기준: `124f18c`(프로젝트 셋업) → `3843b6f`(HEAD) · 브랜치 `staging-spec/entity-cart`  
> 테스트: **4 passed, 5 failed** — 할인·최종금액(INV-2~4)은 RED 대기

### ✨ 기능

- **INV-1** — `subtotal(items)`가 `Σ(price × qty)`를 반환합니다.
- **E-1** — `items`가 `None`이면 `TypeError`를 발생시킵니다.
- **E-2** — `price` 또는 `qty`가 음수이면 해당 인덱스를 담은 `ValueError`를 발생시킵니다.
- Entity / Boundary **Dual-Track** 테스트 구조를 도입했습니다.
  - `tests/entity/test_cart.py` — `@pytest.mark.entity` (INV-*)
  - `tests/boundary/test_subtotal_input.py` — `@pytest.mark.boundary` (E-*)

### 🧹 기타

- **RED** — INV-1~INV-4, E-1, E-2 계약 스켈레톤 테스트 및 `cart.py` API 스텁 추가
- **문서** — PRD, README 계약 ID, Report/Prompting Export, EXPORT 커맨드 동기화
- **프로젝트 셋업** — AGENTS.md, Cursor rules(c2c-work / entity-track / boundary-track), pytest 마커 설정

### 🔜 다음 예정 (미구현)

| 계약 | 상태 |
| ---- | ---- |
| INV-2 문턱 할인 (`apply_threshold_discount`) | RED — `NotImplementedError` |
| INV-3 VIP 할인 순서 (`final_total`) | RED — `NotImplementedError` |
| INV-4 `0 ≤ final ≤ subtotal` | RED — `NotImplementedError` |

## 핵심 원칙

- **ID에 없는 동작은 만들지 않는다.** 계약 ID에 정의되지 않은 기능·예외·정책은 구현하지 않습니다.
- **테스트가 먼저다.** 구현보다 실패하는 테스트가 항상 앞섭니다.
- **RED → GREEN → REFACTOR** 순서를 따릅니다.
- **과잉 구현을 금지한다.** 요청·계약 범위를 넘는 기능을 미리 만들지 않습니다.

## 계약 ID 목록

| ID    | 계약(불변식 / 에러)                                                 | 근거 레벨 | 계층        |
| ----- | ------------------------------------------------------------ | ----- | --------- |
| INV-1 | `subtotal(items) == Σ(price × qty)`                          | —     | Entity    |
| INV-2 | `amount ≥ 50000 → round(amount×0.9)` / `< 50000 → 그대로` 경계 포함 | L1    | Entity    |
| INV-3 | `final = 문턱할인 적용 후, VIP면 round(×0.95)`. 순서 문턱→VIP 고정         | L2    | Entity    |
| INV-4 | 모든 입력에서 `0 ≤ final_total ≤ subtotal`. 할인은 금액을 늘리지 않는다        | L3    | Entity    |
| E-1   | `items is None → TypeError`                                  | L0    | Boundary* |
| E-2   | `price` 또는 `qty`가 음수 → `ValueError`, 인덱스 포함                  | L0    | Boundary* |

## 계약 ID 설명

### INV-1

장바구니 소계는 각 품목의 `price × qty`를 모두 더한 값과 같아야 합니다.

### INV-2

문턱 할인 규칙입니다. 소계(`amount`)가 50,000원 이상이면 `round(amount × 0.9)`를 적용하고, 50,000원 미만이면 원래 금액을 그대로 반환합니다. 경계값 50,000원을 포함합니다.

### INV-3

VIP 할인 규칙입니다. 문턱 할인을 먼저 적용한 뒤, VIP 고객이면 `round(× 0.95)`를 적용합니다. 적용 순서는 **문턱 → VIP**로 고정됩니다.

### INV-4

시스템 전역 불변식입니다. 어떤 입력에서도 최종 결제액(`final_total`)은 0 이상이며 소계(`subtotal`) 이하여야 합니다. 할인으로 인해 금액이 커지면 안 됩니다.

### E-1

`items`가 `None`이면 `TypeError`를 발생시킵니다.

### E-2

`price` 또는 `qty`가 음수이면, 해당 인덱스를 포함한 `ValueError`를 발생시킵니다.

## 계층 의미

### Entity

`src/cart.py`가 담당하는 **순수 도메인 계산 로직** 계층입니다. Flask 등 외부 프레임워크를 import하지 않으며, 소계·할인·최종 금액 계산과 관련된 `INV-*` 계약을 구현합니다.

### Boundary*

`E-*` 계약은 입력 검증 경계에 가까운 규칙입니다. 별도 Boundary 모듈이 없는 **현재 실습**에서는 도메인 함수 진입점에서 입력을 검증합니다.

## 파일 구조

```text
.
├── README.md
├── src/
│   └── cart.py
└── tests/
    ├── entity/
    │   └── test_cart.py          # @pytest.mark.entity  — INV-*
    └── boundary/
        └── test_subtotal_input.py  # @pytest.mark.boundary — E-*
```

## TDD 진행 순서

1. **RED** — 계약 ID별로 실패하는 테스트를 먼저 작성합니다.
2. **GREEN** — 해당 계약 ID를 만족하는 최소 구현만 추가합니다. 구현 줄에는 충족한 계약 ID를 주석으로 표기합니다.
3. **REFACTOR** — 모든 테스트가 통과한 상태에서만 구조를 개선합니다. 리팩터 전후 `pytest -q`로 동작 불변을 확인합니다.

## 테스트 실행

```bash
pytest -q
pytest tests/entity -q      # Entity(INV-*)만
pytest tests/boundary -q    # Boundary(E-*)만
```

`-q`는 **quiet mode**로, 테스트 결과를 간략하게 출력합니다.

## 구현 금지 사항

- 할인 정책 추가 금지
- 쿠폰, 세금, 배송비, 포인트 기능 추가 금지
- ID에 없는 예외 처리 추가 금지
- UI, CLI, DB, API 코드 추가 금지
