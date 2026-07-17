from __future__ import annotations

import argparse
import sys
import unittest
from pathlib import Path
from unittest.mock import patch


SCRIPTS_DIR = Path(__file__).resolve().parents[1] / "scripts"
sys.path.insert(0, str(SCRIPTS_DIR))

import crypto  # noqa: E402


class CryptoExtensionTests(unittest.TestCase):
    def test_daily_candles_use_current_days_endpoint(self) -> None:
        args = argparse.Namespace(
            market="UPBIT",
            ticker="BTC",
            from_time="2026-06-17T09:00:00",
            to_time="2026-07-17T10:34:53",
        )

        with patch.object(crypto, "request_json", return_value={}) as request_json:
            crypto.fetch_daily_candles(args)

        request_json.assert_called_once_with(
            "/api/coin/candle/UPBIT/KRW/BTC/days?from=2026-06-17T09%3A00%3A00&to=2026-07-17T10%3A34%3A53"
        )

    def test_compare_chart_uses_asset_family_and_datetime_range(self) -> None:
        args = argparse.Namespace(
            nation="foreign",
            asset_type="futures",
            code="GCcv1",
            period="day",
            start_date_time="20260617090000",
            end_date_time="20260717103453",
        )

        with patch.object(crypto, "request_json", return_value={}) as request_json:
            crypto.fetch_compare_chart(args)

        request_json.assert_called_once_with(
            "/api/securityService/chart/compare/foreign/futures/GCcv1/day?startDateTime=20260617090000&endDateTime=20260717103453"
        )

    def test_public_crypto_overview_feeds_are_distinct(self) -> None:
        args = argparse.Namespace(page_size=9)

        with patch.object(crypto, "request_json", return_value={}) as request_json:
            crypto.fetch_market_updates_overview(args)
            crypto.fetch_expert_contents(args)

        self.assertEqual(
            request_json.call_args_list,
            [
                unittest.mock.call("/api/coin/marketUpdates?pageSize=9"),
                unittest.mock.call("/api/coin/expertContents?pageSize=9"),
            ],
        )


if __name__ == "__main__":
    unittest.main()
