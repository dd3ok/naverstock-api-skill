from __future__ import annotations

from io import StringIO
import json
from pathlib import Path
import sys
import unittest
from unittest.mock import patch
from urllib.parse import parse_qs, urlsplit

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "scripts"))

import discussion  # noqa: E402
import domestic_etf  # noqa: E402
import foreign_stock  # noqa: E402
import home  # noqa: E402
import market_stock  # noqa: E402
import naverstock_api as api  # noqa: E402
import news  # noqa: E402
import research  # noqa: E402
import stock_detail_pages as detail  # noqa: E402


class PageAuditContracts(unittest.TestCase):
    """Exercise CLI boundaries against contracts observed on the public pages."""

    def run_cli(self, module, options, payload):
        def reply(path):
            api.validate_public_request(path)
            return payload

        with (
            patch.object(sys, "argv", [module.__name__, *options]),
            patch.object(module, "request_json", side_effect=reply) as request,
            patch("sys.stdout", new_callable=StringIO) as stdout,
        ):
            module.main()
        request.assert_called_once()
        parsed = urlsplit(request.call_args.args[0])
        return parsed.path, parse_qs(parsed.query, keep_blank_values=True), json.loads(stdout.getvalue())

    def test_exchange_sessions_preserve_distinct_schema_and_repeated_values(self):
        payload = {"serverTime": "2026-09-16T12:00:00+09:00", "exchanges": [
            {"exchange": "nxt", "zoneId": "Asia/Seoul", "statuses": [
                {"stockType": "stock", "latest": {"session": None}, "next": None}]}]}
        path, query, result = self.run_cli(home, ["exchange-sessions", "--exchange", "shenzhen",
                                                "--exchange", "hochiminh"], payload)
        self.assertEqual(path, "/api/stockSecurity/exchanges/market-status")
        self.assertEqual(query, {"exchanges": ["shenzhen", "hochiminh"]})
        self.assertEqual(result, payload)
        self.assertEqual(self.run_cli(home, ["exchange-sessions"], payload)[1], {"exchanges": ["krx", "nxt"]})

    def test_indicators_accept_new_groups_without_rewriting_codes(self):
        payload = {"exchangeRate": {"USD": {}}, "governmentBond": {"US10YT=RR": {}}, "commodity": {"CLcv1": {}}}
        _, query, result = self.run_cli(home, ["indicators-v1", "--currency-codes", "USD",
                                              "--bond-codes", "US10YT=RR,KR10YT=RR",
                                              "--commodity-codes", "CLcv1,GCcv1"], payload)
        self.assertEqual(query, {"currencyCodes": ["USD"], "bondCodes": ["US10YT=RR,KR10YT=RR"],
                                 "commodityCodes": ["CLcv1,GCcv1"]})
        self.assertEqual(result, payload)

    def test_domestic_v3_retains_string_index_and_separate_exchange_quotes(self):
        payload = {"index": "1", "size": "2", "totalCount": "10", "hasNext": True,
                   "items": [{"itemCode": "005930", "krx": {"price": "1"}, "nxt": None}]}
        path, query, result = self.run_cli(market_stock, ["list-v3", "--index", "1", "--size", "2"], payload)
        self.assertEqual(path, "/api/stockSecurity/individual-stocks/v3/domestic")
        self.assertEqual(query, {"listingType": ["tradingValueDesc"], "exchangeType": ["consolidated"],
                                 "index": ["1"], "size": ["2"]})
        self.assertEqual(result, payload)

    def test_current_us_etf_sort_mapping_and_all_filter_omission(self):
        for order, sort_type, direction in (("priceTop", "tradingValue", "desc"),
                ("marketValue", "marketCap", "desc"), ("up", "changeRate", "desc"),
                ("down", "changeRate", "asc"), ("trading", "tradingVolume", "desc"),
                ("dividend", "dividend", "desc")):
            with self.subTest(order=order):
                path, query, result = self.run_cli(foreign_stock, ["etfs-v2", "--order-type", order,
                    "--index", "1", "--size", "2", "--large-category-code", "all"],
                    {"index": "1", "items": [], "hasNext": False})
                self.assertEqual(path, "/api/stockSecurity/etfs/v2/foreign")
                self.assertEqual(query, {"sortType": [sort_type], "sortDirection": [direction], "index": ["1"], "size": ["2"]})
                self.assertFalse(result["hasNext"])
        themes = [{"largeCategoryCode": "01", "middleCategories": []}]
        self.assertEqual(self.run_cli(foreign_stock, ["etf-themes-v2"], themes)[2], themes)

    def test_domestic_etf_version_is_opt_in(self):
        for options, version in (([], "v2"), (["--api-version", "v3"], "v3")):
            path, query, _ = self.run_cli(domestic_etf, ["list", *options], {"items": []})
            self.assertEqual(path, f"/api/stockSecurity/etfs/{version}/domestic")
            self.assertEqual(query["index"], ["0"])

    def test_returned_cursors_are_round_tripped_without_decoding_or_auto_fetch(self):
        cursor = "next/2026-09-14:2+opaque=="
        cases = ((domestic_etf, ["popular"], "/api/stockSecurity/rankings/v2/domestic/popular-etf"),
                 (foreign_stock, ["popular-etfs"], "/api/stockSecurity/rankings/v2/foreign/popular-etf"),
                 (detail, ["daily-prices-v2", "--code", "A005930"], "/api/stockSecurity/items/v2/domestic/005930/daily-prices"))
        for module, command, expected in cases:
            with self.subTest(command=command):
                payload = {"items": [], "cursor": cursor, "hasNext": True}
                path, first_query, result = self.run_cli(module, [*command, "--size", "2"], payload)
                self.assertEqual(path, expected)
                self.assertNotIn("cursor", first_query)
                _, next_query, final = self.run_cli(module, [*command, "--size", "2", "--cursor", result["cursor"]],
                                                   {"items": [], "cursor": None, "hasNext": False})
                self.assertEqual(next_query["cursor"], [cursor])
                self.assertEqual(final, {"items": [], "cursor": None, "hasNext": False})
                if module is foreign_stock:
                    self.assertEqual(next_query["nationType"], ["USA"])

    def test_popular_aggregates_remain_arrays_without_cursor(self):
        for module, command, suffix in ((domestic_etf, "popular-summary", "domesticPopularEtf"),
                                        (foreign_stock, "popular-etf-summary", "foreignPopularEtf")):
            path, query, result = self.run_cli(module, [command, "--size", "2"], [])
            self.assertEqual(path, "/api/stockSecurity/aggregate/" + suffix)
            self.assertEqual(query, {"size": ["2"]})
            self.assertEqual(result, [])

    def test_snapshot_preserves_null_and_venue_objects(self):
        payload = {"itemCode": "005930", "iNav": None, "krx": {"closePrice": "1"}, "nxt": None}
        path, query, result = self.run_cli(detail, ["price-snapshot", "--code", "A005930"], payload)
        self.assertEqual(path, "/api/stockSecurity/items/v2/domestic/005930/price-snapshot")
        self.assertEqual(query, {})
        self.assertEqual(result, payload)

    def test_ipo_prefix_and_empty_news_query_are_preserved(self):
        for command, suffix in (("ipo-detail", ""), ("ipo-info", "/info")):
            path, _, _ = self.run_cli(market_stock, [command, "--code", "A250030"], {"ipoCode": "A250030"})
            self.assertEqual(path, "/api/domestic/ipo/A250030/detail" + suffix)
        path, query, _ = self.run_cli(news, ["ipo-news", "--page", "2", "--page-size", "2"], {"items": [], "total": "0"})
        self.assertEqual(path, "/api/domestic/news/search")
        self.assertEqual(query, {"query": [""], "IPO": ["true"], "page": ["2"], "pageSize": ["2"]})

    def test_ipo_discussion_keeps_negative_offset_and_sanitization(self):
        _, query, result = self.run_cli(discussion, ["item-posts", "--discussion-type", "IPO",
            "--item-code", "A250030", "--offset=-429406550"],
            {"posts": [{"id": 123, "profileId": "secret", "body": "test@example.com"}], "lastOffset": -123})
        self.assertEqual(query["itemCode"], ["A250030"])
        self.assertEqual(query["offset"], ["-429406550"])
        for flag in ("isHolderOnly", "excludesItemNews", "isItemNewsOnly", "isCleanbotPassedOnly"):
            self.assertEqual(query[flag], ["false"])
        self.assertEqual(result, {"posts": [{"id": 123, "body": "[redacted-email]"}], "lastOffset": -123})

    def test_research_detail_page_keeps_item_context_and_adjacent_objects(self):
        payload = {"researchContent": {"nid": 96027}, "researchSummaries": {"prev": {"nid": 95868}, "next": None}}
        path, query, result = self.run_cli(research, ["detail-page", "--research-id", "96027", "--item-code", "A005930"], payload)
        self.assertEqual(path, "/api/stockSecurity/researches/v2/company/96027/detail-page")
        self.assertEqual(query, {"size": ["1"], "itemCode": ["005930"]})
        self.assertEqual(result, payload)

    def test_invalid_inputs_fail_before_network(self):
        cases = [(market_stock, ["ipo-detail", "--code", code]) for code in ("250030", "A250030/../auth", "Ａ250030")]
        cases += [(discussion, ["item-posts", "--discussion-type", "IPO", "--item-code", "250030"]),
                  (foreign_stock, ["etfs-v2", "--order-type", "top"]),
                  (domestic_etf, ["list", "--api-version", "v4"]),
                  (home, ["exchange-sessions", *(["--exchange", "krx"] * 10)])]
        for module, command in ((market_stock, ["list-v3"]), (foreign_stock, ["etfs-v2"]),
                                (domestic_etf, ["popular"]), (detail, ["daily-prices-v2", "--code", "005930"])):
            cases.extend((module, [*command, "--size", size]) for size in ("0", "101"))
        for cursor in ("x&userId=1", "x\n", "x" * 513):
            cases.append((foreign_stock, ["popular-etfs", "--cursor", cursor]))
        for module, options in cases:
            with (self.subTest(options=options), patch.object(sys, "argv", [module.__name__, *options]),
                  patch.object(module, "request_json") as request, patch("sys.stderr", new_callable=StringIO),
                  self.assertRaises(SystemExit) as error):
                module.main()
            self.assertEqual(error.exception.code, 2)
            request.assert_not_called()

    def test_new_reads_do_not_bypass_private_profile_boundary(self):
        with self.assertRaises(api.RequestValidationError):
            api.validate_public_request("/api/stockSecurity/items/v2/domestic/005930/profile")
        with self.assertRaises(api.RequestValidationError):
            api.validate_public_request("/api/community/profiles/123")


if __name__ == "__main__":
    unittest.main()
