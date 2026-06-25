def _validate_line_items(items):
    for i, (price, qty) in enumerate(items):
        if price < 0 or qty < 0:  # E-2
            raise ValueError(i)


def subtotal(items):
    """장바구니 소계. E-1, E-2, INV-1."""
    if items is None:  # E-1
        raise TypeError
    _validate_line_items(items)  # E-2
    total = 0
    for price, qty in items:
        total += price * qty  # INV-1
    return total


def apply_threshold_discount(amount):
    """문턱 할인. INV-2."""
    raise NotImplementedError


def final_total(items, is_vip=False):
    """최종 결제액. INV-3, INV-4."""
    raise NotImplementedError
