#!/usr/bin/env python3
"""CLI contract tests for script-backed Naver Stock endpoints."""

from __future__ import annotations

import argparse
import sys
import unittest
from pathlib import Path
from unittest.mock import patch

ROOT = Path(__file__).resolve().parents[1]
SCRIPTS = ROOT / "scripts"
sys.path.insert(0, str(SCRIPTS))

import discussion  # noqa: E402
import market_trend  # noqa: E402
import marketindex  # noqa: E402


class MarketIndexTests(unittest.TestCase):
    def test_transport_category_uses_marketindex_transport_endpoint(self) -> None:
        args = argparse.Namespace(category="transport")

        with patch.object(marketindex, "request_json", return_value=[]) as request_json:
            result = marketindex.fetch_category(args)

        self.assertEqual(result, [])
        request_json.assert_called_once_with("/api/securityService/marketindex/transport")


class MarketTrendTests(unittest.TestCase):
    def test_trend_foreign_org_uses_read_only_trend_endpoint(self) -> None:
        args = argparse.Namespace(market_type="ALL", trade_type="KRX", page=1, page_size=5)

        with patch.object(market_trend, "request_json", return_value={"sections": {}}) as request_json:
            result = market_trend.fetch_trend_foreign_org(args)

        self.assertEqual(result, {"sections": {}})
        request_json.assert_called_once_with(
            "/api/domestic/market/trend/trendForeignOrg?marketType=ALL&tradeType=KRX&page=1&pageSize=5"
        )


class DiscussionTests(unittest.TestCase):
    def test_rankings_uses_discussion_rankings_endpoint(self) -> None:
        args = argparse.Namespace(nation_type="KOR", page=1, size=5, post_type="HOT")

        with patch.object(discussion, "request_json", return_value={"contents": []}) as request_json:
            result = discussion.fetch_rankings(args)

        self.assertEqual(result, {"contents": []})
        request_json.assert_called_once_with(
            "/api/community/discussion/rankings?nationType=KOR&page=1&size=5&postType=HOT"
        )


if __name__ == "__main__":
    unittest.main()
