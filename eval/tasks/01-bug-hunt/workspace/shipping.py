FREE_SHIPPING_THRESHOLD = 50.00
SHIPPING_FLAT = 4.99


def order_total(items, discount_rate=0.0):
    """items: list of (price, qty). Returns amount charged including shipping."""
    subtotal = sum(price * qty for price, qty in items)
    discounted = subtotal * (1 - discount_rate)
    shipping = 0.0 if subtotal >= FREE_SHIPPING_THRESHOLD else SHIPPING_FLAT
    return round(discounted + shipping, 2)
