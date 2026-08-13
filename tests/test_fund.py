#!/usr/bin/env python3
"""Request-construction and input-validation tests for fund.py."""

from __future__ import annotations

import argparse
from datetime import date as date_class
from io import StringIO
from pathlib import Path
import sys
import unittest
from unittest.mock import call, patch


ROOT = Path(__file__).resolve().parents[1]
SCRIPTS = ROOT / "scripts"
sys.path.insert(0, str(SCRIPTS))

import fund  # noqa: E402


FUND_CODE = "K55105B00244"


class FundRequestTests(unittest.TestCase):
    def test_unparameterized_detail_paths_match_observed_routes(self) -> None:
        args = argparse.Namespace(code=FUND_CODE)

        with patch.object(fund, "request_json", return_value={}) as request_json:
            fund.fetch_left_panel(args)
            fund.fetch_chart_price_panel(args)
            fund.fetch_performance(args)
            fund.fetch_class_returns(args)
            fund.fetch_allocation(args)

        self.assertEqual(
            request_json.call_args_list,
            [
                call(f"/api/fund/funds/{FUND_CODE}/left-panel"),
                call(f"/api/fund/funds/{FUND_CODE}/chart-price-panel"),
                call(f"/api/fund/funds/{FUND_CODE}/fund-performance"),
                call(f"/api/fund/funds/{FUND_CODE}/classes/returns"),
                call(f"/api/fund/funds/{FUND_CODE}/fund-allocation"),
            ],
        )

    def test_base_price_chart_keeps_observed_term_query(self) -> None:
        args = argparse.Namespace(code=FUND_CODE, term="3m")

        with patch.object(fund, "request_json", return_value={}) as request_json:
            fund.fetch_base_price_chart(args)

        request_json.assert_called_once_with(
            f"/api/fund/funds/{FUND_CODE}/base-price/chart?term=3m"
        )

    def test_metrics_keeps_observed_term_query(self) -> None:
        args = argparse.Namespace(code=FUND_CODE, term="1y")

        with patch.object(fund, "request_json", return_value={}) as request_json:
            fund.fetch_metrics(args)

        request_json.assert_called_once_with(
            f"/api/fund/funds/{FUND_CODE}/metrics/detail?term=1y"
        )

    def test_daily_prices_keeps_iso_date_and_bounded_size(self) -> None:
        args = argparse.Namespace(code=FUND_CODE, date="2026-08-13", size=10)

        with patch.object(fund, "request_json", return_value={}) as request_json:
            fund.fetch_daily_prices(args)

        request_json.assert_called_once_with(
            f"/api/fund/funds/{FUND_CODE}/prices/daily?date=2026-08-13&size=10"
        )


class FundInputValidationTests(unittest.TestCase):
    def test_fund_code_normalizes_case_and_allows_path_safe_token(self) -> None:
        self.assertEqual(fund.fund_code(" k55105b00244 "), FUND_CODE)
        self.assertEqual(fund.fund_code("FUND_1-A"), "FUND_1-A")

    def test_fund_code_rejects_path_and_query_separators(self) -> None:
        for value in ["../auth", "ABC/DEF", "ABC?user=1", "ABC%2FDEF", ""]:
            with self.subTest(value=value), self.assertRaises(argparse.ArgumentTypeError):
                fund.fund_code(value)

    def test_term_accepts_short_tokens_without_assuming_closed_enum(self) -> None:
        self.assertEqual(fund.term_token(" 3M "), "3m")
        self.assertEqual(fund.term_token("year_1"), "year_1")

    def test_term_rejects_separators_and_unbounded_values(self) -> None:
        for value in ["1y&size=500", "../1y", "1y/extra", "x" * 17, ""]:
            with self.subTest(value=value), self.assertRaises(argparse.ArgumentTypeError):
                fund.term_token(value)

    def test_date_requires_canonical_real_iso_date(self) -> None:
        self.assertEqual(fund.iso_date("2026-08-13"), "2026-08-13")
        for value in ["2026-02-30", "2026-8-3", "08/13/2026", ""]:
            with self.subTest(value=value), self.assertRaises(argparse.ArgumentTypeError):
                fund.iso_date(value)

    def test_size_parser_is_numeric_and_bounded(self) -> None:
        parser = fund.bounded_int("size", 1, 100)
        self.assertEqual(parser("10"), 10)
        for value in ["0", "101", "many"]:
            with self.subTest(value=value), self.assertRaises(argparse.ArgumentTypeError):
                parser(value)

    def test_cli_defaults_match_observed_detail_requests(self) -> None:
        cases = [
            (
                ["fund.py", "base-price-chart", "--code", FUND_CODE],
                f"/api/fund/funds/{FUND_CODE}/base-price/chart?term=3m",
            ),
            (
                ["fund.py", "metrics", "--code", FUND_CODE],
                f"/api/fund/funds/{FUND_CODE}/metrics/detail?term=1y",
            ),
        ]
        for argv, expected in cases:
            with (
                self.subTest(argv=argv),
                patch.object(sys, "argv", argv),
                patch.object(fund, "request_json", return_value={}) as request_json,
                patch("sys.stdout", new_callable=StringIO),
            ):
                fund.main()
                request_json.assert_called_once_with(expected)

    def test_daily_prices_defaults_to_today_and_size_ten(self) -> None:
        argv = ["fund.py", "daily-prices", "--code", FUND_CODE]

        with (
            patch.object(sys, "argv", argv),
            patch.object(fund, "date") as date,
            patch.object(fund, "request_json", return_value={}) as request_json,
            patch("sys.stdout", new_callable=StringIO),
        ):
            date.today.return_value = date_class(2026, 8, 13)
            date.fromisoformat.side_effect = date_class.fromisoformat
            fund.main()

        request_json.assert_called_once_with(
            f"/api/fund/funds/{FUND_CODE}/prices/daily?date=2026-08-13&size=10"
        )

    def test_cli_rejects_unsafe_fund_code_before_request(self) -> None:
        argv = ["fund.py", "left-panel", "--code", "../personal"]

        with (
            patch.object(sys, "argv", argv),
            patch.object(fund, "request_json") as request_json,
            patch("sys.stderr", new_callable=StringIO),
        ):
            with self.assertRaises(SystemExit):
                fund.main()

        request_json.assert_not_called()

    def test_cli_rejects_invalid_daily_price_inputs_before_request(self) -> None:
        for option, value in [("--date", "2026-02-30"), ("--size", "1000")]:
            argv = ["fund.py", "daily-prices", "--code", FUND_CODE, option, value]
            with (
                self.subTest(option=option),
                patch.object(sys, "argv", argv),
                patch.object(fund, "request_json") as request_json,
                patch("sys.stderr", new_callable=StringIO),
            ):
                with self.assertRaises(SystemExit):
                    fund.main()
                request_json.assert_not_called()


if __name__ == "__main__":
    unittest.main()
