from __future__ import annotations

import argparse
from io import StringIO
import sys
import unittest
from pathlib import Path
from unittest.mock import patch
from urllib.parse import parse_qs, urlsplit


SCRIPTS_DIR = Path(__file__).resolve().parents[1] / "scripts"
sys.path.insert(0, str(SCRIPTS_DIR))

import home  # noqa: E402


class HomeTests(unittest.TestCase):
    def test_public_aggregate_rankings_stay_on_all_segment(self) -> None:
        args = argparse.Namespace(ranking_type="earning", start_idx=0, page_size=20)

        with patch.object(home, "request_json", return_value={}) as request_json:
            home.fetch_public_ranking(args)

        request_json.assert_called_once_with(
            "/api/domestic/home/ranking/earningRate/all?startIdx=0&pageSize=20"
        )

    def test_public_holding_and_related_stocks_are_separate(self) -> None:
        with patch.object(home, "request_json", return_value={}) as request_json:
            home.fetch_holding_stock_ranking(argparse.Namespace())
            home.fetch_related_stock(argparse.Namespace(code="A005930"))

        self.assertEqual(
            request_json.call_args_list,
            [
                unittest.mock.call(
                    "/api/securityService/home/v3/ranking/more/domestic/holdingStock/all"
                ),
                unittest.mock.call("/api/securityService/home/v3/stock/005930/related"),
            ],
        )

    def test_market_briefing_current_uses_domain_selector(self) -> None:
        with patch.object(home, "request_json", return_value={}) as request_json:
            home.fetch_market_briefing(argparse.Namespace())

        request_json.assert_called_once_with("/api/securityAi/marketBriefing/current?marketBriefing=domain")

    def test_market_briefing_list_uses_date_as_query_not_path(self) -> None:
        args = argparse.Namespace(date="2026-07-17", size=20, page_token=None)

        with patch.object(home, "request_json", return_value={}) as request_json:
            home.fetch_market_briefing_list(args)

        request_json.assert_called_once_with("/api/securityAi/marketBriefing?date=2026-07-17&size=20")

    def test_market_briefing_detail_keeps_old_namespace_compatible(self) -> None:
        args = argparse.Namespace(briefing_id="12345")

        with patch.object(home, "request_json", return_value={}) as request_json:
            home.fetch_market_briefing_detail(args)

        request_json.assert_called_once_with("/api/securityAi/marketBriefing/12345")

    def test_market_briefing_v2_preserves_cursor_and_raw_payload(self) -> None:
        token = "next:abc/def+ghi==._~-"
        payload = {"items": [{"id": 12345}], "hasMore": True, "nextPageToken": token}
        for page_token in (None, token):
            args = argparse.Namespace(
                date="2026-09-07", size=20, page_token=page_token, api_version="v2"
            )
            with (
                self.subTest(page_token=page_token),
                patch.object(home, "request_json", return_value=payload) as request_json,
            ):
                result = home.fetch_market_briefing_list(args)

            self.assertIs(result, payload)
            request_json.assert_called_once()
            url = urlsplit(request_json.call_args.args[0])
            self.assertEqual(url.path, "/api/securityAi/v2/marketBriefing")
            expected_query = {"date": ["2026-09-07"], "size": ["20"]}
            if page_token is not None:
                expected_query["pageToken"] = [token]
            self.assertEqual(parse_qs(url.query), expected_query)

    def test_market_briefing_cli_version_selection_preserves_default(self) -> None:
        for command, selector, suffix in (
            ("market-briefing-list", ["--date", "2026-09-07"], "?date=2026-09-07&size=20"),
            ("market-briefing-detail", ["--briefing-id", "12345"], "/12345"),
        ):
            for version in (None, "v1", "v2"):
                argv = ["home.py", command, *selector]
                if version is not None:
                    argv.extend(["--api-version", version])
                with (
                    self.subTest(command=command, version=version),
                    patch.object(sys, "argv", argv),
                    patch.object(home, "request_json", return_value={}) as request_json,
                    patch("sys.stdout", new_callable=StringIO),
                ):
                    home.main()

                base = "/api/securityAi/v2/marketBriefing" if version == "v2" else "/api/securityAi/marketBriefing"
                request_json.assert_called_once_with(base + suffix)

    def test_market_briefing_rejects_invalid_versions_before_request(self) -> None:
        for version in ("v3", "../personal", None):
            args = argparse.Namespace(
                date="2026-09-07", size=20, page_token=None, briefing_id="12345", api_version=version
            )
            for fetch in (home.fetch_market_briefing_list, home.fetch_market_briefing_detail):
                with (
                    self.subTest(version=version, function=fetch.__name__),
                    patch.object(home, "request_json") as request_json,
                    self.assertRaisesRegex(ValueError, "api-version"),
                ):
                    fetch(args)
                request_json.assert_not_called()

        for command, selector in (
            ("market-briefing-list", ["--date", "2026-09-07"]),
            ("market-briefing-detail", ["--briefing-id", "12345"]),
        ):
            with (
                self.subTest(command=command),
                patch.object(sys, "argv", ["home.py", command, *selector, "--api-version", "v3"]),
                patch.object(home, "request_json") as request_json,
                patch.object(sys, "stderr", StringIO()),
                self.assertRaises(SystemExit) as exited,
            ):
                home.main()
            self.assertEqual(exited.exception.code, 2)
            request_json.assert_not_called()

    def test_market_info_uses_trade_type_path(self) -> None:
        args = argparse.Namespace(trade_type="NXT")

        with patch.object(home, "request_json", return_value={}) as request_json:
            home.fetch_market_info(args)

        request_json.assert_called_once_with("/api/domestic/market/NXT/info")

    def test_operating_time_uses_observed_exchange_path(self) -> None:
        args = argparse.Namespace(exchange="NASDAQ")

        with patch.object(home, "request_json", return_value={}) as request_json:
            home.fetch_operating_time(args)

        request_json.assert_called_once_with("/api/foreign/operatingTime/exchange/NASDAQ")

    def test_shorttents_preserves_observed_home_parameters(self) -> None:
        args = argparse.Namespace(
            source="pc.npay_finhome",
            content_type="compact",
            category_first="증권",
            nscs=0,
        )

        with patch.object(home, "request_json", return_value={}) as request_json:
            home.fetch_shorttents(args)

        request_json.assert_called_once_with(
            "/api/shorttents?source=pc.npay_finhome&type=compact&category_first=%EC%A6%9D%EA%B6%8C&nscs=0"
        )

    def test_money_story_repeats_category_ids(self) -> None:
        args = argparse.Namespace(main_category_id=[1, 2], size=3)

        with patch.object(home, "request_json", return_value={}) as request_json:
            home.fetch_money_story(args)

        request_json.assert_called_once_with("/api/content/moneyStory?mainCategoryIdList=1&mainCategoryIdList=2&size=3")

    def test_economic_upcoming_uses_default_home_filters(self) -> None:
        args = argparse.Namespace(gte_importance=3, limit=3, nation_type=None)

        with patch.object(home, "request_json", return_value={}) as request_json:
            home.fetch_economic_upcoming(args)

        request_json.assert_called_once_with(
            "/api/securityService/economic/indicator/nations/upcoming?gteImportance=3&limit=3&nationTypeList=KOR&nationTypeList=USA"
        )

    def test_notable_etf_uses_foreign_compatible_default(self) -> None:
        args = argparse.Namespace(nation="foreign", order_type=None, start_idx=0, page_size=10)

        with patch.object(home, "request_json", return_value={}) as request_json:
            home.fetch_notable_etf(args)

        request_json.assert_called_once_with(
            "/api/foreign/market/home/notableETF?orderType=up&startIdx=0&pageSize=10"
        )

    def test_notable_etf_uses_domestic_compatible_default(self) -> None:
        args = argparse.Namespace(nation="domestic", order_type=None, start_idx=0, page_size=10)

        with patch.object(home, "request_json", return_value={}) as request_json:
            home.fetch_notable_etf(args)

        request_json.assert_called_once_with(
            "/api/domestic/market/home/notableETF?orderType=amount_etf&startIdx=0&pageSize=10"
        )

    def test_cli_accepts_only_nation_specific_notable_etf_enums(self) -> None:
        cases = (
            ("domestic", "1week_earn_rate"),
            ("foreign", "return1Month"),
        )
        for nation, order_type in cases:
            argv = [
                "home.py",
                "notable-etf",
                "--nation",
                nation,
                "--order-type",
                order_type,
            ]
            with (
                self.subTest(nation=nation, order_type=order_type),
                patch.object(sys, "argv", argv),
                patch.object(home, "request_json", return_value=[]) as request_json,
                patch("sys.stdout", new_callable=StringIO),
            ):
                home.main()

            request_json.assert_called_once_with(
                f"/api/{nation}/market/home/notableETF?orderType={order_type}&startIdx=0&pageSize=10"
            )

    def test_cli_rejects_invalid_briefing_inputs(self) -> None:
        argv_sets = (
            ["home.py", "market-briefing-list", "--date", "2026-02-30"],
            [
                "home.py",
                "market-briefing-list",
                "--date",
                "2026-07-17",
                "--page-token",
                "unsafe cursor",
            ],
            ["home.py", "market-briefing-detail", "--briefing-id", "../personal"],
        )
        for argv in argv_sets:
            with (
                self.subTest(argv=argv),
                patch.object(sys, "argv", argv),
                patch.object(sys, "stderr", StringIO()),
                self.assertRaises(SystemExit),
            ):
                home.main()

    def test_cli_rejects_unbounded_home_queries(self) -> None:
        argv_sets = (
            ["home.py", "money-story", "--size", "101"],
            ["home.py", "notable-etf", "--page-size", "101"],
            ["home.py", "notable-etf", "--nation", "foreign", "--order-type", "amount_etf"],
            ["home.py", "notable-etf", "--nation", "domestic", "--order-type", "up"],
            ["home.py", "economic-upcoming", "--limit", "0"],
        )
        for argv in argv_sets:
            with (
                self.subTest(argv=argv),
                patch.object(sys, "argv", argv),
                patch.object(sys, "stderr", StringIO()),
                self.assertRaises(SystemExit),
            ):
                home.main()

    def test_cli_rejects_invalid_indicator_codes(self) -> None:
        with (
            patch.object(sys, "argv", ["home.py", "indicators", "--indicator-codes", "KOSPI,../personal"]),
            patch.object(sys, "stderr", StringIO()),
            self.assertRaises(SystemExit),
        ):
            home.main()

    def test_related_stock_code_is_normalized_and_path_safe(self) -> None:
        self.assertEqual(home._domestic_code("A005930"), "005930")
        with (
            patch.object(sys, "argv", ["home.py", "related-stock", "--code", "../auth"]),
            patch.object(sys, "stderr", StringIO()),
            self.assertRaises(SystemExit),
        ):
            home.main()


if __name__ == "__main__":
    unittest.main()
