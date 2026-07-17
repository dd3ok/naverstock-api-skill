from __future__ import annotations

import argparse
from io import StringIO
from pathlib import Path
import sys
import unittest
from unittest.mock import patch


SCRIPTS_DIR = Path(__file__).resolve().parents[1] / "scripts"
sys.path.insert(0, str(SCRIPTS_DIR))

import crypto  # noqa: E402


class CryptoDetailTests(unittest.TestCase):
    def test_foreign_interval_chart_uses_exchange_segment(self) -> None:
        args = argparse.Namespace(
            asset_type="INDEX",
            exchange="NASDAQ",
            code=".IXIC",
            interval=5,
            start_date_time="20260716130000",
            end_date_time="20260716200000",
            utc=True,
        )

        with patch.object(crypto, "request_json", return_value={}) as request_json:
            crypto.fetch_foreign_interval_chart(args)

        request_json.assert_called_once_with(
            "/api/securityService/chart/foreign/INDEX/NASDAQ/.IXIC/interval/5?startDateTime=20260716130000&endDateTime=20260716200000&utc=true"
        )

    def test_period_and_detail_minute_candles_are_separate(self) -> None:
        period = argparse.Namespace(
            market="UPBIT", ticker="BTC", period="weeks", from_time="a", to_time="b"
        )
        minute = argparse.Namespace(
            market="UPBIT", ticker="BTC", unit=5, from_time="a", to_time="b"
        )

        with patch.object(crypto, "request_json", return_value={}) as request_json:
            crypto.fetch_period_candles(period)
            crypto.fetch_minute_candles(minute)

        self.assertEqual(
            request_json.call_args_list,
            [
                unittest.mock.call("/api/coin/candle/UPBIT/KRW/BTC/weeks?from=a&to=b"),
                unittest.mock.call("/api/coin/candle/UPBIT/KRW/BTC/minutes/5?from=a&to=b"),
            ],
        )

    def test_sector_ticker_categories_and_etf_exposure(self) -> None:
        with patch.object(crypto, "request_json", return_value={}) as request_json:
            crypto.fetch_category_detail(
                argparse.Namespace(category_id="123", exchange_type="UPBIT")
            )
            crypto.fetch_ticker_categories(
                argparse.Namespace(ticker="BTC", exchange_type="UPBIT")
            )
            crypto.fetch_etf_exposure(
                argparse.Namespace(ticker="BTC", size=20, page=1, page_token=None)
            )

        self.assertEqual(
            request_json.call_args_list,
            [
                unittest.mock.call("/api/coin/categories/123?exchangeType=UPBIT"),
                unittest.mock.call("/api/coin/BTC/categories?exchangeType=UPBIT"),
                unittest.mock.call(
                    "/api/coin/etf/BTC?sortType=holdingWeight&size=20&page=1"
                ),
            ],
        )

    def test_public_content_details_and_ai_history(self) -> None:
        with patch.object(crypto, "request_json", return_value={}) as request_json:
            crypto.fetch_market_update_detail(argparse.Namespace(content_id="abc-1"))
            crypto.fetch_expert_content_detail(argparse.Namespace(content_id="def-2"))
            crypto.fetch_coin_briefing_history(
                argparse.Namespace(
                    exchange_type="UPBIT",
                    ticker="BTC",
                    size=20,
                    date="2026-07-17",
                    page_token=None,
                )
            )
            crypto.fetch_coin_briefing_detail(argparse.Namespace(briefing_id="ghi-3"))

        self.assertEqual(
            request_json.call_args_list,
            [
                unittest.mock.call("/api/coin/marketUpdates/detail/abc-1"),
                unittest.mock.call("/api/coin/expertContents/def-2"),
                unittest.mock.call(
                    "/api/securityAi/coinBriefings?exchangeType=UPBIT&nfTicker=BTC&size=20&date=2026-07-17"
                ),
                unittest.mock.call("/api/securityAi/coinBriefing/ghi-3"),
            ],
        )

    def test_cli_rejects_unsafe_or_unbounded_inputs(self) -> None:
        cases = [
            ["crypto.py", "profile", "--ticker", "../BTC"],
            ["crypto.py", "rank", "--page-size", "10000"],
            [
                "crypto.py",
                "price",
                "--ticker",
                "BTC",
                "--market",
                "UPBIT",
                "--exclude-exchange",
                "BITHUMB",
            ],
            [
                "crypto.py",
                "daily-candles",
                "--ticker",
                "BTC",
                "--from-time",
                "2026-07-17T09:00:00",
                "--to-time",
                "2026-07-16T09:00:00",
            ],
            [
                "crypto.py",
                "compare-chart",
                "--nation",
                "domestic",
                "--asset-type",
                "futures",
                "--code",
                "KOSPI",
                "--start-date-time",
                "20260716000000",
                "--end-date-time",
                "20260717000000",
            ],
            [
                "crypto.py",
                "foreign-interval-chart",
                "--asset-type",
                "INDEX",
                "--exchange",
                "NASDAQ",
                "--code",
                ".IXIC",
                "--start-date-time",
                "20260717000000",
                "--end-date-time",
                "20260716000000",
            ],
            [
                "crypto.py",
                "compare-chart",
                "--nation",
                "foreign",
                "--code",
                ".INX",
                "--start-date-time",
                "20261301000000",
                "--end-date-time",
                "20260717000000",
            ],
        ]
        for argv in cases:
            with self.subTest(argv=argv):
                with patch.object(sys, "argv", argv), patch("sys.stderr", new_callable=StringIO):
                    with self.assertRaises(SystemExit):
                        crypto.main()


if __name__ == "__main__":
    unittest.main()
