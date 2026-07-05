from shipping import order_total


def test_no_discount_under_threshold():
    assert order_total([(10.00, 2)]) == 24.99


def test_no_discount_over_threshold():
    assert order_total([(30.00, 2)]) == 60.00
