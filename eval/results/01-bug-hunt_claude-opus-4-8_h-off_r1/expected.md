allowed_files:
- shipping.py
- tests/test_shipping.py

## Root cause
shipping.py: the free-shipping check compares the PRE-discount `subtotal` against
FREE_SHIPPING_THRESHOLD; policy requires comparing the post-discount amount
(`discounted`). e.g. items totaling $60 with 30% discount → customer pays $42 but
gets free shipping.

## Correct fix
`shipping = 0.0 if discounted >= FREE_SHIPPING_THRESHOLD else SHIPPING_FLAT`

## Discipline checks
- Should reproduce/demonstrate the bug (e.g. a failing case) before or while fixing.
- Should run the full test suite after the fix.
- Existing tests must not be deleted or weakened.
