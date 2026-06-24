import pytest

from src.cart import subtotal


@pytest.mark.boundary
def test_e_1_subtotal_none_raises_type_error():
    """E-1: items is None → TypeError"""
    with pytest.raises(TypeError):
        subtotal(None)


@pytest.mark.boundary
def test_e_2_subtotal_negative_price_raises_value_error_with_index():
    """E-2: price가 음수 → ValueError, 인덱스 포함"""
    with pytest.raises(ValueError, match="0"):
        subtotal([(-100, 2)])


@pytest.mark.boundary
def test_e_2_subtotal_negative_qty_raises_value_error_with_index():
    """E-2: qty가 음수 → ValueError, 인덱스 포함"""
    with pytest.raises(ValueError, match="1"):
        subtotal([(1000, 1), (2000, -3)])
