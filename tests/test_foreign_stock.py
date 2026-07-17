#!/usr/bin/env python3
"""Request-construction and CLI contract tests for foreign_stock.py."""

from __future__ import annotations

import argparse
from io import StringIO
from pathlib import Path
import sys
import unittest
from unittest.mock import patch


ROOT = Path(__file__).resolve().parents[1]
SCRIPTS = ROOT / "scripts"
sys.path.insert(0, str(SCRIPTS))

import foreign_stock  # noqa: E402


class ForeignMarketRequestTests(unittest.TestCase):
    def test_country_stock_list_uses_bounded_public_ranking_endpoint(self) -> None:
        args = argparse.Namespace(
            nation="usa", trade_type="NSQ", order_type="marketValue", start_idx=0, page_size=2
        )

        with patch.object(foreign_stock, "request_json", return_value=[]) as request_json:
            result = foreign_stock.fetch_stocks(args)

        self.assertEqual(result, [])
        request_json.assert_called_once_with(
            "/api/foreign/market/stock/global?nation=usa&tradeType=NSQ&orderType=marketValue&startIdx=0&pageSize=2"
        )

    def test_sector_list_normalizes_nation_for_path(self) -> None:
        args = argparse.Namespace(nation="jpn")

        with patch.object(foreign_stock, "request_json", return_value=[]) as request_json:
            foreign_stock.fetch_sectors(args)

        request_json.assert_called_once_with("/api/foreign/market/JPN/upjong/list")

    def test_sector_constituents_use_observed_filters(self) -> None:
        args = argparse.Namespace(
            nation="usa", industry_code="55501040", order_type="quantTop", start_idx=10, page_size=5
        )

        with patch.object(foreign_stock, "request_json", return_value=[]) as request_json:
            foreign_stock.fetch_sector_stocks(args)

        request_json.assert_called_once_with(
            "/api/foreign/market/USA/upjong/55501040/list?orderType=quantTop&startIdx=10&pageSize=5"
        )


class ForeignEtfRequestTests(unittest.TestCase):
    def test_etf_theme_filters_use_public_theme_endpoint(self) -> None:
        with patch.object(foreign_stock, "request_json", return_value=[]) as request_json:
            foreign_stock.fetch_etf_themes(argparse.Namespace())

        request_json.assert_called_once_with("/api/foreign/market/etf/themes")

    def test_etf_list_keeps_large_and_middle_theme_filters(self) -> None:
        args = argparse.Namespace(
            order_type="dividend", large_code="03", middle_code="0301", start_idx=0, page_size=5
        )

        with patch.object(foreign_stock, "request_json", return_value=[]) as request_json:
            foreign_stock.fetch_etfs(args)

        request_json.assert_called_once_with(
            "/api/foreign/market/etf/usa?orderType=dividend&largeCode=03&middleCode=0301&startIdx=0&pageSize=5"
        )

    def test_notable_etfs_omit_unset_theme_filters(self) -> None:
        args = argparse.Namespace(
            order_type="up", large_code=None, middle_code=None, start_idx=0, page_size=3
        )

        with patch.object(foreign_stock, "request_json", return_value=[]) as request_json:
            foreign_stock.fetch_notable_etfs(args)

        request_json.assert_called_once_with(
            "/api/foreign/market/home/notableETF?orderType=up&startIdx=0&pageSize=3"
        )

    def test_etf_theme_list_uses_count_bound_command(self) -> None:
        args = argparse.Namespace(middle_code="0301", count=3)

        with patch.object(foreign_stock, "request_json", return_value=[]) as request_json:
            foreign_stock.fetch_etf_theme_list(args)

        request_json.assert_called_once_with(
            "/api/foreign/market/usa/etf/themeList?middleCode=0301&count=3"
        )

    def test_etf_prices_and_related_use_distinct_endpoints(self) -> None:
        price_args = argparse.Namespace(code="VOO", page=1, page_size=2)
        related_args = argparse.Namespace(code="VOO", start_idx=0, page_size=2)

        with patch.object(foreign_stock, "request_json", return_value=[]) as request_json:
            foreign_stock.fetch_etf_prices(price_args)
            foreign_stock.fetch_etf_related(related_args)

        self.assertEqual(
            request_json.call_args_list,
            [
                unittest.mock.call("/api/securityService/etf/VOO/price?page=1&pageSize=2"),
                unittest.mock.call("/api/foreign/v2/market/etf/usa/VOO?startIdx=0&pageSize=2"),
            ],
        )


class ForeignSecurityRequestTests(unittest.TestCase):
    def test_stock_news_keeps_global_and_local_feeds_separate(self) -> None:
        args = argparse.Namespace(code="NVDA.O", page=1, page_size=5)

        with patch.object(foreign_stock, "request_json", return_value={}) as request_json:
            foreign_stock.fetch_stock_world_news(args)
            foreign_stock.fetch_stock_local_news(args)

        self.assertEqual(
            request_json.call_args_list,
            [
                unittest.mock.call(
                    "/api/foreign/worldStock/list?reutersCode=NVDA.O&page=1&pageSize=5"
                ),
                unittest.mock.call(
                    "/api/domestic/detail/news?itemCode=NVDA.O&page=1&pageSize=5"
                ),
            ],
        )

    def test_finance_routes_cover_overview_summary_and_periodic_sections(self) -> None:
        with patch.object(foreign_stock, "request_json", return_value={}) as request_json:
            foreign_stock.fetch_finance(
                argparse.Namespace(code="NVDA.O", section="overview", period="annual")
            )
            foreign_stock.fetch_finance(
                argparse.Namespace(code="NVDA.O", section="summary", period="annual")
            )
            foreign_stock.fetch_finance(
                argparse.Namespace(code="NVDA.O", section="income", period="quarter")
            )

        self.assertEqual(
            request_json.call_args_list,
            [
                unittest.mock.call("/api/securityService/stock/overview?reutersCode=NVDA.O"),
                unittest.mock.call(
                    "/api/securityService/stock/finance/summary?reutersCode=NVDA.O"
                ),
                unittest.mock.call(
                    "/api/securityService/stock/finance/income/quarter?reutersCode=NVDA.O"
                ),
            ],
        )

    def test_stock_summary_endpoints_are_separate_read_only_gets(self) -> None:
        args = argparse.Namespace(code="NVDA.O")

        with patch.object(foreign_stock, "request_json", return_value={}) as request_json:
            foreign_stock.fetch_stock_basic(args)
            foreign_stock.fetch_stock_consensus(args)
            foreign_stock.fetch_stock_overview(args)

        self.assertEqual(
            request_json.call_args_list,
            [
                unittest.mock.call("/api/securityService/stock/NVDA.O/basic"),
                unittest.mock.call("/api/securityService/stock/NVDA.O/consensus"),
                unittest.mock.call("/api/securityService/stock/NVDA.O/overview"),
            ],
        )

    def test_stock_daily_prices_use_one_based_page(self) -> None:
        args = argparse.Namespace(code="NVDA.O", page=1, page_size=2)

        with patch.object(foreign_stock, "request_json", return_value=[]) as request_json:
            foreign_stock.fetch_stock_prices(args)

        request_json.assert_called_once_with(
            "/api/securityService/stock/NVDA.O/price?page=1&pageSize=2"
        )

    def test_shared_foreign_detail_keeps_observed_etf_code_type(self) -> None:
        args = argparse.Namespace(code="NVDA.O")

        with patch.object(foreign_stock, "request_json", return_value={}) as request_json:
            foreign_stock.fetch_foreign_detail(args)

        request_json.assert_called_once_with("/api/foreign/NVDA.O/detail?codeType=ETF")

    def test_index_endpoints_cover_basic_prices_and_constituents(self) -> None:
        basic = argparse.Namespace(code=".IXIC")
        paged = argparse.Namespace(code=".IXIC", page=1, page_size=2)

        with patch.object(foreign_stock, "request_json", return_value={}) as request_json:
            foreign_stock.fetch_index_basic(basic)
            foreign_stock.fetch_index_prices(paged)
            foreign_stock.fetch_index_constituents(paged)

        self.assertEqual(
            request_json.call_args_list,
            [
                unittest.mock.call("/api/securityService/index/.IXIC/basic"),
                unittest.mock.call("/api/securityService/index/.IXIC/price?page=1&pageSize=2"),
                unittest.mock.call(
                    "/api/securityService/index/.IXIC/enrollStocks?page=1&pageSize=2"
                ),
            ],
        )

    def test_polling_encodes_repeated_codes_as_one_reuters_code_set(self) -> None:
        args = argparse.Namespace(security_type="stock", code=["NVDA.O", "TSLA.O"])

        with patch.object(foreign_stock, "request_json", return_value={}) as request_json:
            foreign_stock.fetch_poll(args)

        request_json.assert_called_once_with(
            "/api/polling/worldstock/stock?reutersCodes=NVDA.O%2CTSLA.O"
        )

    def test_exchange_time_uses_named_public_exchange(self) -> None:
        args = argparse.Namespace(exchange="NASDAQ")

        with patch.object(foreign_stock, "request_json", return_value={}) as request_json:
            foreign_stock.fetch_exchange_time(args)

        request_json.assert_called_once_with("/api/foreign/operatingTime/exchange/NASDAQ")


class ForeignStockCliContractTests(unittest.TestCase):
    def test_notable_etf_cli_accepts_every_current_ui_order_type(self) -> None:
        for order_type in foreign_stock.NOTABLE_ETF_ORDER_TYPES:
            argv = [
                "foreign_stock.py",
                "notable-etfs",
                "--order-type",
                order_type,
                "--page-size",
                "1",
            ]
            with (
                self.subTest(order_type=order_type),
                patch.object(sys, "argv", argv),
                patch.object(foreign_stock, "request_json", return_value=[]),
                patch("sys.stdout", new_callable=StringIO),
            ):
                foreign_stock.main()

    def test_stock_basic_cli_normalizes_lowercase_code(self) -> None:
        argv = ["foreign_stock.py", "stock-basic", "--code", "nvda.o"]

        with (
            patch.object(sys, "argv", argv),
            patch.object(foreign_stock, "request_json", return_value={}) as request_json,
            patch("sys.stdout", new_callable=StringIO),
        ):
            foreign_stock.main()

        request_json.assert_called_once_with("/api/securityService/stock/NVDA.O/basic")

    def test_cli_rejects_path_separator_in_security_code(self) -> None:
        argv = ["foreign_stock.py", "stock-basic", "--code", "../api/personal"]

        with (
            patch.object(sys, "argv", argv),
            patch("sys.stderr", new_callable=StringIO),
        ):
            with self.assertRaises(SystemExit):
                foreign_stock.main()

    def test_cli_rejects_unbounded_page_size(self) -> None:
        argv = ["foreign_stock.py", "stocks", "--page-size", "10000"]

        with (
            patch.object(sys, "argv", argv),
            patch("sys.stderr", new_callable=StringIO),
        ):
            with self.assertRaises(SystemExit):
                foreign_stock.main()

    def test_cli_does_not_expose_personal_or_mutation_commands(self) -> None:
        argv = ["foreign_stock.py", "favorite", "--code", "NVDA.O"]

        with (
            patch.object(sys, "argv", argv),
            patch("sys.stderr", new_callable=StringIO),
        ):
            with self.assertRaises(SystemExit):
                foreign_stock.main()


if __name__ == "__main__":
    unittest.main()
