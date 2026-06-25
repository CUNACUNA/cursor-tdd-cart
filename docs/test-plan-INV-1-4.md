# Test Plan — INV-1 ~ INV-4 · E-1 · E-2

| 항목 | 내용 |
|------|------|
| **문서 버전** | 1.0 |
| **작성일** | 2026-06-24 |
| **근거 문서** | [README.md](../README.md) (계약 ID 목록), [PRD.md](./PRD.md) |
| **상태** | RED 완료 · GREEN 대기 |

---

## 1. 개요

본 문서는 [README.md](../README.md) 계약 ID **INV-1 ~ INV-4**, **E-1**, **E-2**를 검증하기 위한 테스트 플랜이다.

| ID | 계약 | 근거 레벨 | 계층 | 대상 함수 |
|----|------|----------|------|----------|
| INV-1 | `subtotal(items) == Σ(price × qty)` | — | Entity | `subtotal` |
| INV-2 | `amount ≥ 50000 → round(amount×0.9)` / `< 50000 → 그대로` (경계 포함) | L1 | Entity | `apply_threshold_discount` |
| INV-3 | `final = 문턱할인 적용 후, VIP면 round(×0.95)`. 순서 문턱→VIP 고정 | L2 | Entity | `final_total` |
| INV-4 | 모든 입력에서 `0 ≤ final_total ≤ subtotal`. 할인은 금액을 늘리지 않는다 | L3 | Entity | `final_total` |
| E-1 | `items is None → TypeError` | L0 | Boundary* | `subtotal` |
| E-2 | `price` 또는 `qty`가 음수 → `ValueError`, 인덱스 포함 | L0 | Boundary* | `subtotal` |

**입력 형식**: `items: list[tuple[int, int]]` — `(price, qty)` 튜플 리스트

**현재 실습**: Boundary 모듈 없음 → E-1/E-2는 `subtotal()` 진입점에서 검증 ([README § Boundary*](../README.md))

---

## 2. 파일·마커 구조

```text
src/cart.py
tests/
├── entity/
│   └── test_cart.py          # @pytest.mark.entity  — INV-1 ~ INV-4
└── boundary/
    └── test_subtotal_input.py # @pytest.mark.boundary — E-1, E-2
```

| 명령 | 용도 |
|------|------|
| `pytest tests/entity -q` | Entity(INV-*)만 |
| `pytest tests/boundary -q` | Boundary(E-*)만 |
| `pytest -q` | 전체 (작업 종료 시 필수) |

---

## 3. TDD 사이클 순서

가장 단순한 실패 테스트부터 **RED → GREEN → REFACTOR** 순으로 진행한다.

| 순서 | 단계 | 계약 | 커밋 메시지 예 |
|------|------|------|----------------|
| 1 | RED | INV-1 | `test(RED): INV-1 subtotal 합산` |
| 2 | GREEN | INV-1 | `feat(GREEN): INV-1 Σ(price×qty)` |
| 3 | RED | INV-2 | `test(RED): INV-2 문턱 할인 경계` |
| 4 | GREEN | INV-2 | `feat(GREEN): INV-2 apply_threshold_discount` |
| 5 | RED | INV-3 | `test(RED): INV-3 문턱→VIP 순서` |
| 6 | GREEN | INV-3 | `feat(GREEN): INV-3 final_total VIP 할인` |
| 7 | RED | INV-4 | `test(RED): INV-4 final ≤ subtotal` |
| 8 | GREEN | INV-4 | `feat(GREEN): INV-4 전역 불변식` |
| 9 | RED | E-1 | `test(RED): E-1 None TypeError` |
| 10 | GREEN | E-1 | `feat(GREEN): E-1 None 검증` |
| 11 | RED | E-2 | `test(RED): E-2 음수 ValueError` |
| 12 | GREEN | E-2 | `feat(GREEN): E-2 인덱스 ValueError` |
| 13 | REFACTOR | — | `refactor: cart.py 구조 정리` |

**구현 진입점 검증 순서** (`subtotal` 내부):

```text
1. items is None          → TypeError           (E-1)
2. enumerate(items)       → 음수 price/qty      → ValueError(인덱스) (E-2)
3. Σ(price × qty)                               (INV-1)
```

---

## 4. INV-1 — 소계 합산

### 4.1 계약

장바구니 소계는 각 품목의 `price × qty`를 모두 더한 값과 같아야 한다.

```
subtotal(items) == sum(price_i * qty_i for each item i)
```

### 4.2 테스트 케이스

| ID | 테스트 함수 | 입력 | 기대 | 상태 |
|----|------------|------|------|------|
| T-INV-1-01 | `test_inv_1_subtotal_equals_sum_of_price_times_qty` | `[(12000, 3), (30000, 1)]` | `66000` | RED ✓ |

**검산**: 12,000×3 + 30,000×1 = 66,000 (인터뷰 사례)

### 4.3 GREEN 최소 구현

```python
def subtotal(items):
    if items is None:       # E-1
        raise TypeError
    total = 0
    for i, (price, qty) in enumerate(items):
        if price < 0 or qty < 0:  # E-2
            raise ValueError(i)
        total += price * qty      # INV-1
    return total
```

---

## 5. INV-2 — 문턱 할인

### 5.1 계약

| 조건 | 결과 |
|------|------|
| `amount ≥ 50000` | `round(amount × 0.9)` |
| `amount < 50000` | `amount` 그대로 |

경계값 **50,000원 포함** (`≥`).

### 5.2 테스트 케이스

| ID | 테스트 함수 | 입력 | 기대 | 상태 |
|----|------------|------|------|------|
| T-INV-2-01 | `test_inv_2_threshold_discount_applies_at_and_above_50000` | `50000`, `66000` | `45000`, `59400` | RED ✓ |
| T-INV-2-02 | `test_inv_2_threshold_discount_unchanged_below_50000` | `49999` | `49999` | RED ✓ |

**검산**:

- `round(50000 × 0.9)` = **45,000**
- `round(66000 × 0.9)` = **59,400**
- `49999` → **49,999** (할인 없음)

### 5.3 GREEN 최소 구현

```python
def apply_threshold_discount(amount):
    if amount >= 50000:           # INV-2
        return round(amount * 0.9)  # INV-2
    return amount                   # INV-2
```

---

## 6. INV-3 — VIP 할인 (문턱 → VIP 순서)

### 6.1 계약

문턱 할인을 **먼저** 적용한 뒤, VIP 고객이면 `round(× 0.95)`를 적용한다. 순서 변경 금지.

```
final = round( apply_threshold_discount(subtotal) × 0.95 )  # VIP
final = apply_threshold_discount(subtotal)                  # 비-VIP
```

### 6.2 테스트 케이스

| ID | 테스트 함수 | 입력 | 기대 | 상태 |
|----|------------|------|------|------|
| T-INV-3-01 | `test_inv_3_final_total_applies_threshold_then_vip_discount` | `[(12000,3),(30000,1)], is_vip=True` | `56430` | RED ✓ |

**검산**:

1. subtotal = 66,000
2. 문턱 할인: `round(66000 × 0.9)` = 59,400
3. VIP 할인: `round(59400 × 0.95)` = **56,430**

### 6.3 GREEN 최소 구현

```python
def final_total(items, is_vip=False):
    amount = apply_threshold_discount(subtotal(items))  # INV-3
    if is_vip:                                          # INV-3
        return round(amount * 0.95)                     # INV-3
    return amount
```

---

## 7. INV-4 — 전역 불변식

### 7.1 계약

어떤 입력에서도 최종 결제액은 다음을 만족한다.

```
0 ≤ final_total ≤ subtotal
```

할인으로 금액이 커지면 안 된다.

### 7.2 테스트 케이스

| ID | 테스트 함수 | 입력 | 검증 | 상태 |
|----|------------|------|------|------|
| T-INV-4-01 | `test_inv_4_final_total_is_between_zero_and_subtotal` | `[(12000,3),(30000,1)], is_vip=False` | `0 ≤ final ≤ sub` | RED ✓ |
| T-INV-4-02 | `test_inv_4_final_total_never_exceeds_subtotal_for_vip` | `[(12000,3),(30000,1)], is_vip=True` | `0 ≤ final ≤ sub` | RED ✓ |

**기대값 (참고)**:

| 경로 | subtotal | final_total |
|------|----------|-------------|
| 비-VIP | 66,000 | 59,400 |
| VIP | 66,000 | 56,430 |

INV-4는 INV-1~3가 올바르게 구현되면 자연스럽게 충족된다. 테스트는 **관계 불변식**을 직접 단언한다.

---

## 8. E-1 — None 입력

### 8.1 계약

`items`가 `None`이면 `TypeError`를 발생시킨다.

### 8.2 테스트 케이스

| ID | 테스트 함수 | 입력 | 기대 | 상태 |
|----|------------|------|------|------|
| T-E-1-01 | `test_e_1_subtotal_none_raises_type_error` | `None` | `TypeError` | RED ✓ |

**주의**: 예외 **타입**만 검증. 메시지 문자열은 계약에 없음.

---

## 9. E-2 — 음수 입력

### 9.1 계약

`price` 또는 `qty`가 음수이면, **해당 인덱스를 포함한** `ValueError`를 발생시킨다.

### 9.2 테스트 케이스

| ID | 테스트 함수 | 입력 | 기대 | 상태 |
|----|------------|------|------|------|
| T-E-2-01 | `test_e_2_subtotal_negative_price_raises_value_error_with_index` | `[(-100, 2)]` | `ValueError`, `match="0"` | RED ✓ |
| T-E-2-02 | `test_e_2_subtotal_negative_qty_raises_value_error_with_index` | `[(1000,1),(2000,-3)]` | `ValueError`, `match="1"` | RED ✓ |

**GREEN 구현 예**: `raise ValueError(i)` — `str(exc)`에 인덱스가 포함되어 `match` 검증 가능.

---

## 10. 계약 추적 매트릭스

| 계약 ID | 테스트 파일 | 테스트 함수 | 구현 함수 | 구현 상태 |
|---------|------------|------------|----------|----------|
| INV-1 | `tests/entity/test_cart.py` | `test_inv_1_*` | `subtotal` | RED |
| INV-2 | `tests/entity/test_cart.py` | `test_inv_2_*` (×2) | `apply_threshold_discount` | RED |
| INV-3 | `tests/entity/test_cart.py` | `test_inv_3_*` | `final_total` | RED |
| INV-4 | `tests/entity/test_cart.py` | `test_inv_4_*` (×2) | `final_total` | RED |
| E-1 | `tests/boundary/test_subtotal_input.py` | `test_e_1_*` | `subtotal` | RED |
| E-2 | `tests/boundary/test_subtotal_input.py` | `test_e_2_*` (×2) | `subtotal` | RED |

---

## 11. 완료 기준

- [ ] INV-1: T-INV-1-01 통과
- [ ] INV-2: T-INV-2-01, T-INV-2-02 통과
- [ ] INV-3: T-INV-3-01 통과
- [ ] INV-4: T-INV-4-01, T-INV-4-02 통과
- [ ] E-1: T-E-1-01 통과
- [ ] E-2: T-E-2-01, T-E-2-02 통과
- [ ] 구현 줄에 `# INV-*`, `# E-*` 주석
- [ ] `pytest -q` 전체 green

---

## 12. 범위 밖 (본 플랜에서 테스트하지 않음)

| 항목 | 이유 |
|------|------|
| 빈 리스트 `[]` | 계약·사례에 명시 없음 |
| `price`/`qty` 타입 오류 (문자열 등) | E-* 계약에 없음 |
| 쿠폰·세금·배송비·포인트 | README 구현 금지 |
| Flask `app.py` 폼 검증 | Boundary UI 사례 없음 |
| `pytest.skip`, `assert True` | AGENTS.md 금지 |

---

*본 문서는 docs/test-plan-INV-1-4.md — README 계약 ID INV-1~INV-4, E-1, E-2 테스트 플랜입니다.*
