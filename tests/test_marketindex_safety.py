#!/usr/bin/env python3
"""CLI safety boundaries for marketindex.py."""

from __future__ import annotations

from io import StringIO
from pathlib import Path
import sys
import unittest
from unittest.mock import patch


SCRIPTS_DIR = Path(__file__).resolve().parents[1] / "scripts"
sys.path.insert(0, str(SCRIPTS_DIR))

import marketindex  # noqa: E402


class MarketIndexSafetyTests(unittest.TestCase):
    def assert_cli_rejected(self, argv: list[str]) -> None:
        with (
            patch.object(sys, "argv", argv),
            patch.object(sys, "stderr", StringIO()),
            self.assertRaises(SystemExit),
        ):
            marketindex.main()

    def test_rejects_path_like_market_codes(self) -> None:
        argv_sets = (
            ["marketindex.py", "chart", "--code", "../personal"],
            ["marketindex.py", "market-polling", "--category", "metals", "--codes", "GCcv1/auth"],
            ["marketindex.py", "detail", "--category", "energy", "--code", "CLcv1?userId=1"],
        )
        for argv in argv_sets:
            with self.subTest(argv=argv):
                self.assert_cli_rejected(argv)

    def test_rejects_unbounded_pagination_and_limit(self) -> None:
        argv_sets = (
            ["marketindex.py", "prices", "--category", "energy", "--code", "CLcv1", "--page-size", "101"],
            ["marketindex.py", "exchange-prices", "--start-idx", "-1"],
            ["marketindex.py", "economic-upcoming", "--limit", "0"],
        )
        for argv in argv_sets:
            with self.subTest(argv=argv):
                self.assert_cli_rejected(argv)

    def test_rejects_invalid_date_currency_and_block(self) -> None:
        argv_sets = (
            ["marketindex.py", "economic-release", "--release-date", "2026-02-30"],
            ["marketindex.py", "exchange-prices", "--currency", "../../USD"],
            ["marketindex.py", "major-block", "--block-type", "personal"],
        )
        for argv in argv_sets:
            with self.subTest(argv=argv):
                self.assert_cli_rejected(argv)

    def test_accepts_observed_market_code_shapes(self) -> None:
        self.assertEqual(marketindex._market_codes(".DJI,FX_USDKRW,KR10YT=RR"), ".DJI,FX_USDKRW,KR10YT=RR")
        self.assertEqual(marketindex._iso_date("2026-07-17"), "20260717")


if __name__ == "__main__":
    unittest.main()
