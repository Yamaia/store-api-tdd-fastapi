from typing import Any


def product_data(**overrides: Any) -> dict[str, Any]:
    data = {
        "name": "iPhone 14 Pro Max",
        "quantity": 10,
        "price": "8500.00",
        "status": True,
    }
    data.update(overrides)
    return data


def products_with_prices() -> list[dict[str, Any]]:
    """Produtos com preços variados, incluindo os limites 5000 e 8000."""
    prices = ["3000.00", "5000.00", "6500.00", "7500.00", "8000.00", "9500.00"]
    return [product_data(name=f"Produto {p}", price=p) for p in prices]
