"""Regressions for observed failures and silently ignored request conditions."""

from __future__ import annotations

import io
import json
from pathlib import Path
import sys
import unittest
import urllib.error
from unittest.mock import patch

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "scripts"))

import naverstock_api as api  # noqa: E402


class RequestContractTests(unittest.TestCase):
    def test_general_feed_rejects_ignored_item_filter_before_network(self) -> None:
        for suffix in ("?itemCode=005930", "?item%43ode=005930", "/?itemCode=005930", "?itemCode="):
            with self.subTest(suffix=suffix), patch.object(
                api, "open_public_url", return_value=io.BytesIO(b'{"posts":[{"itemCode":"028300"}]}')
            ) as open_url:
                with self.assertRaisesRegex(api.RequestValidationError, "item-posts"):
                    api.request_json("/api/community/discussion/posts" + suffix)
                open_url.assert_not_called()

    def test_general_and_dedicated_feeds_keep_their_query_contracts(self) -> None:
        paths = (
            "/api/community/discussion/posts?pageSize=2&offset=-123&discussionGroupType=domesticStock",
            "/api/community/discussion/posts/by-item?itemCode=005930&discussionType=domesticStock&pageSize=2",
            "/api/community/discussion/posts/related/hot?itemCode=005930&pageSize=2",
        )
        for path in paths:
            with self.subTest(path=path):
                self.assertEqual(api.validate_public_request(path), path)

    def assert_http_failure(self, path: str, status: int, hint: str | None) -> None:
        body = io.BytesIO(b'{"message":"upstream failure"}')
        error = urllib.error.HTTPError(api.BASE_URL + path, status, "failure", {}, body)
        with patch.object(api, "open_public_url", side_effect=error) as open_url:
            with self.assertRaises(api.NaverStockAPIError) as caught:
                api.request_json(path)
        open_url.assert_called_once()
        self.assertEqual(open_url.call_args.args[0].full_url, api.BASE_URL + path)
        self.assertTrue(body.closed)
        self.assertIs(caught.exception.__cause__, error)
        self.assertEqual(caught.exception.path, path)
        self.assertEqual(caught.exception.status_code, status)
        self.assertEqual(caught.exception.as_dict()["detail"], {"message": "upstream failure"})
        if hint:
            self.assertIn(hint, str(caught.exception))
        else:
            self.assertEqual(str(caught.exception), f"Naver Stock API returned HTTP {status}")

    def test_legacy_research_404_gives_explicit_migration_without_fallback(self) -> None:
        cases = {
            "company": "category --category COMPANY",
            "industry": "category --category INDUSTRY",
            "invest": "category --category INVEST",
            "economy": "category --category ECONOMY",
            "brokers": "broker-list",
            "latestResearch": "latest",
            "company/by-items": "by-items --item-code",
            "analysis-focus": "analysis-focus",
        }
        for suffix, hint in cases.items():
            with self.subTest(suffix=suffix):
                self.assert_http_failure("/api/stockSecurity/researches/v1/" + suffix, 404, hint)

    def test_market_404_distinguishes_summary_detail_and_polling(self) -> None:
        for path, hint in (
            ("/api/securityService/marketindex/exchange", "exchange-list"),
            ("/api/securityService/marketindex/bond", "major-block --block-type bond"),
            ("/api/polling/marketindex/exchange/FX_USDKRW", "detail --category exchange --code FX_USDKRW"),
        ):
            with self.subTest(path=path):
                self.assert_http_failure(path, 404, hint)

    def test_category_financial_sort_failure_keeps_requested_order(self) -> None:
        for family, code in (("upjong", "307"), ("theme", "155"), ("group", "14")):
            for order in ("sales", "operatingProfit"):
                with self.subTest(family=family, order=order):
                    self.assert_http_failure(
                        f"/api/domestic/market/{family}/{code}/stocklist?orderType={order}&marketType=ALL&pageSize=2",
                        500, "financial sort",
                    )

    def test_monthly_etf_500_explains_observed_theme_condition(self) -> None:
        self.assert_http_failure(
            "/api/foreign/market/home/notableETF?orderType=return1Month&startIdx=0&pageSize=2",
            500, "--middle-code",
        )

    def test_hints_do_not_generalize_to_unobserved_failures(self) -> None:
        for path, status in (
            ("/api/stockSecurity/researches/v2/company/999", 404),
            ("/api/stockSecurity/researches/v1/company", 500),
            ("/api/securityService/marketindex/exchange/FX_USDKRW", 404),
            ("/api/polling/marketindex/exchange/.DXY", 404),
            ("/api/domestic/market/upjong/307/stocklist?orderType=marketSum", 500),
            ("/api/foreign/market/home/notableETF?orderType=up", 500),
            ("/api/foreign/market/home/notableETF?orderType=return1Month&middleCode=0101", 500),
            ("/api/foreign/market/home/notableETF?orderType=return1Month&largeCode=01", 500),
        ):
            with self.subTest(path=path, status=status):
                self.assert_http_failure(path, status, None)

    def test_known_failure_paths_still_accept_future_success_unchanged(self) -> None:
        payload = {"items": [], "hasNext": False}
        paths = (
            "/api/stockSecurity/researches/v1/company?index=0&size=2",
            "/api/domestic/market/upjong/307/stocklist?orderType=sales",
            "/api/foreign/market/home/notableETF?orderType=return1Month",
        )
        for path in paths:
            with self.subTest(path=path):
                response = io.BytesIO(json.dumps(payload).encode())
                with patch.object(api, "open_public_url", return_value=response) as open_url:
                    self.assertEqual(api.request_json(path), payload)
                open_url.assert_called_once()


if __name__ == "__main__":
    unittest.main()
