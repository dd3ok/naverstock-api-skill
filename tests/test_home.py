from __future__ import annotations

import argparse
import json
from io import StringIO
import sys
import unittest
from pathlib import Path
from unittest.mock import patch
from urllib.parse import parse_qs, urlsplit


SCRIPTS_DIR = Path(__file__).resolve().parents[1] / "scripts"
sys.path.insert(0, str(SCRIPTS_DIR))

import home  # noqa: E402
import naverstock_api  # noqa: E402


class HomeTests(unittest.TestCase):
    def run_cli(self, options: list[str], payload: object) -> tuple[str, object]:
        with (
            patch.object(sys, "argv", ["home.py", *options]),
            patch.object(home, "request_json", return_value=payload) as request,
            patch("sys.stdout", new_callable=StringIO) as stdout,
        ):
            home.main()
        request.assert_called_once()
        return request.call_args.args[0], json.loads(stdout.getvalue())

    def test_market_status_default_and_explicit_exchanges_preserve_sessions(self) -> None:
        payload = {
            "serverTime": "2026-09-16T20:00:00+09:00",
            "statuses": [{
                "exchange": "krx", "isHoliday": False,
                "currentSession": {"marketSessionType": "afterMarket", "marketState": "CLOSE"},
                "sessions": [{"openTimeKst": "20:00:00", "closeTimeKst": "08:00:00"}],
                "indexCode": None,
            }],
        }
        for options, expected in (
            ([], ["krx", "nxt", "nasdaq", "shanghai", "hongkong", "tokyo", "hanoi"]),
            (["--exchange", "nxt", "--exchange", "krx"], ["nxt", "krx"]),
            (["--exchange", "hongkong"], ["hongkong"]),
        ):
            with self.subTest(options=options):
                path, result = self.run_cli(["market-status", *options], payload)
                self.assertEqual(urlsplit(path).path, "/api/stockSecurity/market-status/current")
                self.assertEqual(parse_qs(urlsplit(path).query), {"exchanges": expected})
                self.assertEqual(result, payload)

    def test_market_status_direct_calls_reject_invalid_exchange_lists(self) -> None:
        for exchanges in ([], "krx", ["KRX"], ["krx,nxt"], ["../personal"], ["krx"] * 8):
            with (
                self.subTest(exchanges=exchanges),
                patch.object(home, "request_json") as request,
                self.assertRaises(ValueError),
            ):
                home.fetch_market_status(argparse.Namespace(exchange=exchanges))
            request.assert_not_called()

    def test_indicators_v1_groups_and_case_are_preserved(self) -> None:
        payload = {"domesticIndex": {"KOSPI": {"price": {"currentPrice": "6000.01"}}},
                   "foreignIndex": {".IXIC": {"breadth": {"risingCount": "12"}}}, "crypto": {}}
        options = ["indicators-v1", "--domestic-index-codes", "KOSPI,KOSDAQ",
                   "--foreign-index-codes", ".IXIC,.DJI"]
        path, result = self.run_cli(options, payload)
        self.assertEqual(urlsplit(path).path, "/api/securityService/integration/v1/indicators")
        self.assertEqual(parse_qs(urlsplit(path).query), {
            "domesticIndexCodes": ["KOSPI,KOSDAQ"], "foreignIndexCodes": [".IXIC,.DJI"],
        })
        self.assertEqual(result, payload)
        for flag, query in (("--domestic-index-codes", "domesticIndexCodes"),
                            ("--foreign-index-codes", "foreignIndexCodes")):
            with self.subTest(flag=flag):
                path, _ = self.run_cli(["indicators-v1", flag, "CaseSensitive"], {})
                self.assertEqual(parse_qs(urlsplit(path).query), {query: ["CaseSensitive"]})

    def test_indicators_v1_boolean_options_distinguish_omitted_true_false(self) -> None:
        for breadth in (None, True, False):
            for trend in (None, True, False):
                options = ["indicators-v1", "--domestic-index-codes", "KOSPI"]
                expected = {"domesticIndexCodes": ["KOSPI"]}
                for flag, key, value in (("breadth", "includeBreadth", breadth),
                                         ("trend", "includeTrend", trend)):
                    if value is not None:
                        options.append(f"--{'include' if value else 'no-include'}-{flag}")
                        expected[key] = [str(value).lower()]
                with self.subTest(breadth=breadth, trend=trend):
                    path, _ = self.run_cli(options, {})
                    self.assertEqual(parse_qs(urlsplit(path).query), expected)

    def test_indicators_v1_accepts_thirty_codes_across_groups(self) -> None:
        domestic = ",".join(f"D{i}" for i in range(15))
        foreign = ",".join(f"F{i}" for i in range(15))
        path, _ = self.run_cli(["indicators-v1", "--domestic-index-codes", domestic,
                                "--foreign-index-codes", foreign], {})
        self.assertEqual(parse_qs(urlsplit(path).query), {
            "domesticIndexCodes": [domestic], "foreignIndexCodes": [foreign],
        })

    def test_new_home_commands_reject_invalid_input_before_network(self) -> None:
        cases = [
            ["market-status", "--exchange", "KRX"],
            ["market-status", "--exchange", "krx,nxt"],
            ["market-status", *(["--exchange", "krx"] * 8)],
            ["indicators-v1"],
            ["indicators-v1", "--include-trend"],
            ["indicators-v1", "--domestic-index-codes", ",".join(["KOSPI"] * 30),
             "--foreign-index-codes", ".IXIC"],
            ["indicators-v1", "--currency-codes", "USD"],
        ]
        for flag in ("--domestic-index-codes", "--foreign-index-codes"):
            for value in ("", "KOSPI,", "../personal", "KOSPI&userId=1", "%2Fauth",
                          "KOSPI\n", "코스피", "X" * 34, ",".join(["KOSPI"] * 31)):
                cases.append(["indicators-v1", flag, value])
        for options in cases:
            with (
                self.subTest(options=options), patch.object(sys, "argv", ["home.py", *options]),
                patch.object(home, "request_json") as request,
                patch("sys.stderr", new_callable=StringIO), self.assertRaises(SystemExit) as exited,
            ):
                home.main()
            self.assertEqual(exited.exception.code, 2)
            request.assert_not_called()

    def test_indicators_v1_direct_call_rejects_non_boolean_flags(self) -> None:
        for flag in ("include_breadth", "include_trend"):
            for value in ("false", 0, 1):
                args = argparse.Namespace(domestic_index_codes="KOSPI", foreign_index_codes=None,
                                          include_breadth=None, include_trend=None)
                setattr(args, flag, value)
                with (
                    self.subTest(flag=flag, value=value),
                    patch.object(home, "request_json") as request, self.assertRaises(ValueError),
                ):
                    home.fetch_indicators_v1(args)
                request.assert_not_called()

    def test_new_home_commands_preserve_empty_payloads_and_output_option(self) -> None:
        for options, payload in (
            (["market-status"], {"serverTime": "2026-09-16T00:00:00+09:00", "statuses": []}),
            (["indicators-v1", "--foreign-index-codes", ".IXIC"], {"foreignIndex": {}, "crypto": {}}),
        ):
            with (
                self.subTest(command=options[0]),
                patch.object(sys, "argv", ["home.py", *options, "--output", "result.json"]),
                patch.object(home, "request_json", return_value=payload) as request,
                patch.object(home, "emit_output") as emit,
            ):
                home.main()
            request.assert_called_once()
            self.assertEqual(json.loads(emit.call_args.args[0]), payload)
            self.assertEqual(emit.call_args.args[1], "result.json")

    def test_new_home_commands_do_not_retry_or_fallback_on_remote_failure(self) -> None:
        for options in (["market-status"], ["indicators-v1", "--domestic-index-codes", "KOSPI"]):
            for status in (403, 429, 404, 500, 307):
                error = naverstock_api.NaverStockAPIError("upstream failure", path="/original",
                                                        status_code=status, kind="http")
                with (
                    self.subTest(command=options[0], status=status),
                    patch.object(sys, "argv", ["home.py", *options]),
                    patch.object(home, "request_json", side_effect=error) as request,
                    patch.object(home, "emit_output") as emit,
                    self.assertRaises(naverstock_api.NaverStockAPIError) as raised,
                ):
                    home.main()
                self.assertIs(raised.exception, error)
                request.assert_called_once()
                emit.assert_not_called()

    def test_legacy_market_info_and_indicators_keep_default_contracts(self) -> None:
        for options, payload, expected in (
            (["market-info"], {"afterMarketClosingTime": "2026-09-16T20:00:00+09:00"},
             "/api/domestic/market/KRX/info"),
            (["indicators"], [{"itemCode": "KOSPI", "currentPrice": "6000.01"}],
             "/api/securityService/integration/indicators?indicatorCodes="
             "KOSPI%2CKOSDAQ%2C.DJI%2C.IXIC%2C.INX%2CFX_USDKRW%2CGCcv1%2CCLcv1"),
        ):
            with self.subTest(command=options[0]):
                path, result = self.run_cli(options, payload)
                self.assertEqual(path, expected)
                self.assertEqual(result, payload)

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

    def test_foreign_notable_etf_forwards_only_supplied_theme_filters(self) -> None:
        payload = [{"reutersCode": "SPY"}]
        for large_code, middle_code, expected_filters in (
            (None, None, {}),
            ("01", None, {"largeCode": ["01"]}),
            (None, "0101", {"middleCode": ["0101"]}),
            ("01", "0101", {"largeCode": ["01"], "middleCode": ["0101"]}),
        ):
            args = argparse.Namespace(
                nation="foreign", order_type="return1Month", start_idx=0, page_size=10,
                large_code=large_code, middle_code=middle_code,
            )
            with (
                self.subTest(large_code=large_code, middle_code=middle_code),
                patch.object(home, "request_json", return_value=payload) as request_json,
            ):
                result = home.fetch_notable_etf(args)

            self.assertIs(result, payload)
            request_json.assert_called_once()
            url = urlsplit(request_json.call_args.args[0])
            self.assertEqual(url.path, "/api/foreign/market/home/notableETF")
            self.assertEqual(parse_qs(url.query), {
                "orderType": ["return1Month"], "startIdx": ["0"], "pageSize": ["10"],
                **expected_filters,
            })

    def test_foreign_notable_etf_cli_preserves_selected_theme_codes(self) -> None:
        argv = [
            "home.py", "notable-etf", "--nation", "foreign", "--order-type", "return1Month",
            "--large-code", " 01 ", "--middle-code", " 0101 ",
        ]
        with (
            patch.object(sys, "argv", argv),
            patch.object(home, "request_json", return_value=[]) as request_json,
            patch("sys.stdout", new_callable=StringIO),
        ):
            home.main()

        request_json.assert_called_once_with(
            "/api/foreign/market/home/notableETF?orderType=return1Month&largeCode=01&middleCode=0101&startIdx=0&pageSize=10"
        )

    def test_domestic_notable_etf_rejects_foreign_filters_before_request(self) -> None:
        for flag, attribute, value in (
            ("--large-code", "large_code", "01"),
            ("--middle-code", "middle_code", "0101"),
        ):
            args = argparse.Namespace(
                nation="domestic", order_type=None, start_idx=0, page_size=10,
                **{attribute: value},
            )
            with (
                self.subTest(flag=flag, entrypoint="function"),
                patch.object(home, "request_json") as request_json,
                self.assertRaisesRegex(ValueError, "require --nation foreign"),
            ):
                home.fetch_notable_etf(args)
            request_json.assert_not_called()

            for nation_args in ([], ["--nation", "domestic"]):
                with (
                    self.subTest(flag=flag, entrypoint="cli", nation_args=nation_args),
                    patch.object(sys, "argv", ["home.py", "notable-etf", *nation_args, flag, value]),
                    patch.object(home, "request_json") as request_json,
                    patch("sys.stderr", new_callable=StringIO) as stderr,
                    self.assertRaises(SystemExit),
                ):
                    home.main()
                request_json.assert_not_called()
                self.assertIn("require --nation foreign", stderr.getvalue())

    def test_notable_etf_rejects_unsafe_or_unbounded_theme_codes_before_request(self) -> None:
        for flag in ("--large-code", "--middle-code"):
            for value in ("", "../personal", "01&userId=1", "01/02", "01%2F02", "a" * 21, "테마"):
                argv = ["home.py", "notable-etf", "--nation", "foreign", flag, value]
                with (
                    self.subTest(flag=flag, value=value),
                    patch.object(sys, "argv", argv),
                    patch.object(home, "request_json") as request_json,
                    patch("sys.stderr", new_callable=StringIO),
                    self.assertRaises(SystemExit),
                ):
                    home.main()
                request_json.assert_not_called()

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
