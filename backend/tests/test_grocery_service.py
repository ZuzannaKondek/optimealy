"""Tests for grocery list package size matching."""

from types import SimpleNamespace
from unittest.mock import AsyncMock, Mock
from uuid import uuid4

import pytest

from src.services.grocery_service import GroceryService


def test_match_package_size_picks_smallest_covering_package() -> None:
    """Returns a single package when one size can cover the requirement."""
    purchase_g = GroceryService._match_package_size_g(450.0, [500, 1000])
    assert purchase_g == pytest.approx(500.0)


def test_match_package_size_allows_repeating_package_sizes() -> None:
    """Never under-buys when requirement exceeds the largest package."""
    purchase_g = GroceryService._match_package_size_g(1500.0, [500, 1000])
    assert purchase_g == pytest.approx(1500.0)


def test_match_package_size_handles_single_small_package() -> None:
    """Scales up a single package size to meet larger requirements."""
    purchase_g = GroceryService._match_package_size_g(1500.0, [100])
    assert purchase_g == pytest.approx(1500.0)


def test_match_package_size_uses_required_quantity_when_sizes_missing() -> None:
    """Falls back to exact required quantity when package sizes are absent."""
    purchase_g = GroceryService._match_package_size_g(1500.0, [])
    assert purchase_g == pytest.approx(1500.0)


@pytest.mark.asyncio
async def test_get_owned_quantities_reads_live_pantry_rows() -> None:
    """Loads owned quantities from current pantry state."""
    user_id = uuid4()
    product_a = uuid4()
    product_b = uuid4()

    pantry_rows = [
        SimpleNamespace(product_id=product_a, quantity_g=100.0),
        SimpleNamespace(product_id=product_a, quantity_g=250.0),
        SimpleNamespace(product_id=product_b, quantity_g=400.0),
    ]

    scalars = Mock()
    scalars.all.return_value = pantry_rows
    result = Mock()
    result.scalars.return_value = scalars

    db = AsyncMock()
    db.execute.return_value = result

    owned = await GroceryService._get_owned_quantities_g(db, user_id)

    assert owned[str(product_a)] == pytest.approx(350.0)
    assert owned[str(product_b)] == pytest.approx(400.0)
    assert len(owned) == 2
