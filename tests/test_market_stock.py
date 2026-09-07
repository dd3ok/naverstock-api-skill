#!/usr/bin/env python3
"""Regression tests for domestic market ranking compatibility inputs."""

from __future__ import annotations

import sys
import unittest
from io import StringIO
from pathlib import Path
from unittest.mock import patch

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "scripts"))

import market_stock  # noqa: E402


class MarketStockCompatibilityTests(unittest.TestCase):
    def test_default_cli_translates_legacy_order_types(self) -> None:
        for legacy, current in (("accAmount", "priceTop"), ("steady", "flat")):
            with (
                self.subTest(legacy=legacy),
                patch.object(
                    sys,
                    "argv",
                    ["market_stock.py", "default", "--order-type", legacy, "--page-size", "2"],
                ),
                patch.object(market_stock, "request_json", return_value=[]) as request,
                patch("sys.stdout", new_callable=StringIO),
            ):
                market_stock.main()

                request.assert_called_once_with(
                    "/api/domestic/market/stock/default?tradeType=KRX&marketType=ALL"
                    f"&orderType={current}&startIdx=0&pageSize=2"
                )

    def test_default_cli_preserves_current_order_types(self) -> None:
        for current in ("priceTop", "flat"):
            with (
                self.subTest(current=current),
                patch.object(
                    sys,
                    "argv",
                    ["market_stock.py", "default", "--order-type", current, "--page-size", "2"],
                ),
                patch.object(market_stock, "request_json", return_value=[]) as request,
                patch("sys.stdout", new_callable=StringIO),
            ):
                market_stock.main()

                request.assert_called_once_with(
                    "/api/domestic/market/stock/default?tradeType=KRX&marketType=ALL"
                    f"&orderType={current}&startIdx=0&pageSize=2"
                )

    def test_legacy_order_types_keep_market_restrictions(self) -> None:
        for legacy in ("accAmount", "steady"):
            for market_args in (("--trade-type", "NXT"), ("--market-type", "KONEX")):
                with (
                    self.subTest(legacy=legacy, market_args=market_args),
                    patch.object(
                        sys,
                        "argv",
                        ["market_stock.py", "default", "--order-type", legacy, *market_args],
                    ),
                    patch.object(market_stock, "request_json") as request,
                    patch("sys.stderr", new_callable=StringIO),
                    self.assertRaises(SystemExit) as raised,
                ):
                    market_stock.main()

                self.assertEqual(raised.exception.code, 2)
                request.assert_not_called()


if __name__ == "__main__":
    unittest.main()
