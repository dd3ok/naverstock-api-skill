#!/usr/bin/env python3
"""Foreign identifier regression tests for public aggregate investor insights."""

from __future__ import annotations

from io import StringIO
from pathlib import Path
import sys
import unittest
from unittest.mock import patch


ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "scripts"))

import stock_insights  # noqa: E402


class StockInsightsCodeTests(unittest.TestCase):
    def test_foreign_cli_preserves_explicit_suffix_for_both_insight_requests(self) -> None:
        for command, path in [
            ("holder-ranking", "/api/securityService/home/v3/mystock/ranking/RIV_r"),
            ("what-if", "/api/securityService/home/v3/whatIf/worldstock/RIV_r?periodType=year&range=5"),
        ]:
            with (
                self.subTest(command=command),
                patch.object(sys, "argv", [
                    "stock_insights.py", command, "--asset-type", "worldstock", "--code", "RIV_r",
                ]),
                patch.object(stock_insights, "request_json", return_value={}) as request_json,
                patch("sys.stdout", new_callable=StringIO),
            ):
                stock_insights.main()

                request_json.assert_called_once_with(path)

    def test_foreign_normalization_keeps_existing_character_boundary(self) -> None:
        for supplied, expected in [
            ("nvda.o", "NVDA.O"),
            ("riv_r", "RIV_r"),
            ("abc_aB.n", "ABC_aB.N"),
            ("abc=", "ABC="),
        ]:
            with self.subTest(code=supplied):
                self.assertEqual(stock_insights._asset_code("worldstock", supplied), expected)

        for code in (".IXIC", "../api/personal", "RIV_r?x=1", "RIV_r#x", "RIV_r\\x", "RIV%5fr", "Aß", "ı", "RIV_ſ", "ＮVDA.O", "A" * 33):
            with self.subTest(code=code), self.assertRaises(ValueError):
                stock_insights._asset_code("worldstock", code)

    def test_domestic_normalization_remains_separate(self) -> None:
        self.assertEqual(stock_insights._asset_code("domestic", "A005930"), "005930")
        with self.assertRaises(ValueError):
            stock_insights._asset_code("domestic", "RIV_r")


if __name__ == "__main__":
    unittest.main()
