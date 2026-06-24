import pytest

from src.cart import apply_threshold_discount, final_total, subtotal


@pytest.mark.entity
def test_inv_1_subtotal_equals_sum_of_price_times_qty():
    """INV-1: subtotal(items) == Σ(price × qty)"""
    items = [(12000, 3), (30000, 1)]
    assert subtotal(items) == 12000 * 3 + 30000 * 1


@pytest.mark.entity
def test_inv_2_threshold_discount_applies_at_and_above_50000():
    """INV-2: amount ≥ 50000 → round(amount×0.9) (경계 포함)"""
    assert apply_threshold_discount(50000) == round(50000 * 0.9)
    assert apply_threshold_discount(66000) == round(66000 * 0.9)


@pytest.mark.entity
def test_inv_2_threshold_discount_unchanged_below_50000():
    """INV-2: amount < 50000 → 그대로"""
    assert apply_threshold_discount(49999) == 49999


@pytest.mark.entity
def test_inv_3_final_total_applies_threshold_then_vip_discount():
    """INV-3: final = 문턱할인 적용 후, VIP면 round(×0.95). 순서 문턱→VIP 고정"""
    items = [(12000, 3), (30000, 1)]
    after_threshold = round(66000 * 0.9)
    assert final_total(items, is_vip=True) == round(after_threshold * 0.95)


@pytest.mark.entity
def test_inv_4_final_total_is_between_zero_and_subtotal():
    """INV-4: 모든 입력에서 0 ≤ final_total ≤ subtotal"""
    items = [(12000, 3), (30000, 1)]
    sub = subtotal(items)
    final = final_total(items, is_vip=False)
    assert 0 <= final <= sub


@pytest.mark.entity
def test_inv_4_final_total_never_exceeds_subtotal_for_vip():
    """INV-4: 할인은 금액을 늘리지 않는다 — VIP 경로"""
    items = [(12000, 3), (30000, 1)]
    sub = subtotal(items)
    final = final_total(items, is_vip=True)
    assert 0 <= final <= sub
