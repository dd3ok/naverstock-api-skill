#!/usr/bin/env python3
"""CLI contract tests for script-backed Naver Stock endpoints."""

from __future__ import annotations

import argparse
import sys
import unittest
from io import StringIO
from pathlib import Path
from unittest.mock import patch

ROOT = Path(__file__).resolve().parents[1]
SCRIPTS = ROOT / "scripts"
sys.path.insert(0, str(SCRIPTS))

import discussion  # noqa: E402
import market_trend  # noqa: E402
import marketindex  # noqa: E402
import news  # noqa: E402


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

    def test_rankings_cli_maps_page_size_to_api_size_param(self) -> None:
        argv = ["discussion.py", "rankings", "--page-size", "5"]

        with (
            patch.object(sys, "argv", argv),
            patch.object(discussion, "request_json", return_value={"contents": []}) as request_json,
            patch("sys.stdout", new_callable=StringIO),
        ):
            discussion.main()

        request_json.assert_called_once_with(
            "/api/community/discussion/rankings?nationType=KOR&page=1&size=5&postType=HOT"
        )


class NewsTests(unittest.TestCase):
    def test_focus_can_match_section_latest_fallback_params(self) -> None:
        args = argparse.Namespace(
            focus="global-market",
            page=1,
            page_size=15,
            date="20260505",
            enable_fallback=True,
            max_days=7,
        )

        with patch.object(news, "request_json", return_value={"articles": []}) as request_json:
            result = news.fetch_focus(args)

        self.assertEqual(result, {"articles": []})
        request_json.assert_called_once_with(
            "/api/domestic/news/focus?sid=403&page=1&pageSize=15&date=20260505&enableFallback=true&maxDays=7"
        )

    def test_world_detail_uses_foreign_worldnews_article_endpoint(self) -> None:
        args = argparse.Namespace(article_id="2580641")

        with patch.object(news, "request_json", return_value={"article": {"aid": "2580641"}}) as request_json:
            result = news.fetch_world_detail(args)

        self.assertEqual(result, {"article": {"aid": "2580641"}})
        request_json.assert_called_once_with("/api/foreign/news/worldNews/2580641")


if __name__ == "__main__":
    unittest.main()
