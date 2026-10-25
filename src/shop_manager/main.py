"""Entry point and demonstration of the online shop manager."""

from __future__ import annotations

from shop_manager.analytics import (
    generate_products,
    get_category_stats,
    invalidate_cache,
    set_products_for_cache,
    total_stock_value_python,
)
from shop_manager.models import Product
from shop_manager.parallel import demonstrate_race_condition
from shop_manager.services import (
    filter_by_category,
    most_expensive,
    sort_by_price,
)


def main() -> None:
    print("=" * 60)
    print("Online Shop Manager – Lab 09 (variant 3)")
    print("=" * 60)

    # Small demo catalog
    products = generate_products(20, seed=1)
    print(f"\nGenerated {len(products)} demo products.")

    # Basic services
    electronics = filter_by_category(products, "Electronics")
    print(f"Electronics count: {len(electronics)}")

    best = most_expensive(products)
    if best:
        print(f"Most expensive: {best.name} – {best.price:.2f} UAH")

    total = total_stock_value_python(products)
    print(f"Total stock value: {total:,.2f} UAH")

    # Caching demo
    set_products_for_cache(products)
    stats1 = get_category_stats("Electronics")
    print(f"\nCached Electronics stats: {stats1}")

    # Mutation + invalidation
    products.append(
        Product(name="New Gadget", category="Electronics", price=999.0, quantity=5)
    )
    invalidate_cache()
    set_products_for_cache(products)
    stats2 = get_category_stats("Electronics")
    print(f"After add + invalidate: {stats2}")

    # Race condition demo
    print("\n--- Race condition demonstration ---")
    no_lock, with_lock = demonstrate_race_condition(2000)
    print(f"Result WITHOUT Lock (may be wrong): {no_lock}")
    print(f"Result WITH Lock (always correct):  {with_lock}")

    print("\nTop-5 by price:")
    for p in sort_by_price(products)[:5]:
        print(f"  {p.name:20} {p.category:12} {p.price:8.2f}")


if __name__ == "__main__":
    main()
