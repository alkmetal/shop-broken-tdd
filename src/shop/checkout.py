
"""Order checkout.

The rules live in `src/shop/specs/checkout.md` - read it first.
Both functions below are stubs: their signature is final, the bodies are yours.
Do not change the constants: the tests rely on them.
"""

from shop.money import percent_of

PROMO_CODES = {"WELCOME10": 10, "SUMMER15": 15, "VIP35": 35}
SUPPORTED_CITIES = ("msk", "spb")
MAX_DISCOUNT_PERCENT = 30
VAT_PERCENT = 20
SHIPPING_KOPEKS = 49_000
FREE_DELIVERY_FROM_KOPEKS = 500_000
TIER_DISCOUNTS = ((10, 5), (25, 10), (50, 15))
REQUIRED_LINE_KEYS = ("sku", "qty", "unit_price_kopecks")


def validate_order(
    lines: list[dict[str, str]],
    promo_code: str = "",
    shipping_city: str = "",
) -> str | None:
    """Return a human readable reason why the order is invalid, or None if it is fine."""
    if not lines:
        return "order has no lines"

    seen_skus: set[str] = set()
    for index, line in enumerate(lines, start=1):
        for key in REQUIRED_LINE_KEYS:
            if key not in line:
                return f"line {index}: missing key {key}"

        sku = line["sku"]
        if not sku:
            return f"line {index}: sku is empty"
        if sku in seen_skus:
            return f"line {index}: duplicate sku {sku}"
        seen_skus.add(sku)

        try:
            qty = int(line["qty"])
        except (ValueError, TypeError):
            return f"line {index}: qty is not a number"
        if qty <= 0:
            return f"line {index}: qty must be positive"

        try:
            price = int(line["unit_price_kopecks"])
        except (ValueError, TypeError):
            return f"line {index}: price is not a number"
        if price < 0:
            return f"line {index}: price must be non-negative"

    if promo_code and promo_code not in PROMO_CODES:
        return f"unknown promo code: {promo_code}"
    if shipping_city and shipping_city not in SUPPORTED_CITIES:
        return f"unsupported city: {shipping_city}"
    return None


def calculate_order_total(
    lines: list[dict[str, str]],
    promo_code: str = "",
    shipping_city: str = "",
) -> int | None:
    """Return the order total in kopecks, or None if the order is invalid."""
    if validate_order(lines, promo_code, shipping_city) is not None:
        return None

    subtotal = 0
    total_qty = 0
    for line in lines:
        qty = int(line["qty"])
        price = int(line["unit_price_kopecks"])
        subtotal += qty * price
        total_qty += qty

    tier_percent = 0
    for threshold, percent in TIER_DISCOUNTS:
        if total_qty >= threshold:
            tier_percent = percent

    promo_percent = PROMO_CODES.get(promo_code, 0) if promo_code else 0
    discount_percent = max(tier_percent, promo_percent)
    if discount_percent > MAX_DISCOUNT_PERCENT:
        discount_percent = MAX_DISCOUNT_PERCENT

    discount = percent_of(subtotal, discount_percent)
    discounted_subtotal = subtotal - discount

    delivery = 0
    if shipping_city and discounted_subtotal < FREE_DELIVERY_FROM_KOPEKS:
        delivery = SHIPPING_KOPEKS

    base = discounted_subtotal + delivery
    vat = percent_of(base, VAT_PERCENT)
    return base + vat
