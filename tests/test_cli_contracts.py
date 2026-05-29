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
import crypto  # noqa: E402
import market_stock  # noqa: E402
import market_trend  # noqa: E402
import marketindex  # noqa: E402
import naverstock_api  # noqa: E402
import news  # noqa: E402
import research  # noqa: E402
import stock_detail_pages  # noqa: E402


class OutputTests(unittest.TestCase):
    def test_emit_output_writes_unicode_to_text_stdout(self) -> None:
        stream = StringIO()

        with patch.object(sys, "stdout", stream):
            naverstock_api.emit_output("낯선문자\u11a2\n", None)

        self.assertEqual(stream.getvalue(), "낯선문자\u11a2\n")


class MarketIndexTests(unittest.TestCase):
    def test_transport_category_uses_marketindex_transport_endpoint(self) -> None:
        args = argparse.Namespace(category="transport")

        with patch.object(marketindex, "request_json", return_value=[]) as request_json:
            result = marketindex.fetch_category(args)

        self.assertEqual(result, [])
        request_json.assert_called_once_with("/api/securityService/marketindex/transport")

    def test_marketindex_major_block_uses_security_service_type_endpoint(self) -> None:
        args = argparse.Namespace(block_type="bond")

        with patch.object(marketindex, "request_json", return_value=[]) as request_json:
            result = marketindex.fetch_major_block(args)

        self.assertEqual(result, [])
        request_json.assert_called_once_with("/api/securityService/marketindex/majors/bond")

    def test_exchange_list_uses_current_exchange_endpoint(self) -> None:
        args = argparse.Namespace()

        with patch.object(marketindex, "request_json", return_value=[]) as request_json:
            result = marketindex.fetch_exchange_list(args)

        self.assertEqual(result, [])
        request_json.assert_called_once_with("/api/domestic/exchange/List")

    def test_exchange_list_cli_maps_to_current_endpoint(self) -> None:
        argv = ["marketindex.py", "exchange-list"]

        with (
            patch.object(sys, "argv", argv),
            patch.object(marketindex, "request_json", return_value=[]) as request_json,
            patch("sys.stdout", new_callable=StringIO),
        ):
            marketindex.main()

        request_json.assert_called_once_with("/api/domestic/exchange/List")


class MarketStockTests(unittest.TestCase):
    def test_search_top_uses_current_home_search_params(self) -> None:
        args = argparse.Namespace(nation_type="KOR", start_idx=0, page_size=10)

        with patch.object(market_stock, "request_json", return_value=[]) as request_json:
            result = market_stock.fetch_search_top(args)

        self.assertEqual(result, [])
        request_json.assert_called_once_with("/api/domestic/market/searchTop?nationType=KOR&startIdx=0&pageSize=10")

    def test_dividend_uses_current_market_list_params(self) -> None:
        args = argparse.Namespace(
            trade_type="KRX",
            market_type="ALL",
            dividend="dividendRate",
            start_idx=0,
            page_size=100,
        )

        with patch.object(market_stock, "request_json", return_value=[]) as request_json:
            result = market_stock.fetch_dividend(args)

        self.assertEqual(result, [])
        request_json.assert_called_once_with(
            "/api/domestic/market/stock/dividend?tradeType=KRX&marketType=ALL&dividend=dividendRate&startIdx=0&pageSize=100"
        )

    def test_ipo_can_request_listing_progress_type(self) -> None:
        args = argparse.Namespace(ipo_progress_type="LISTING", start_idx=0, page_size=100)

        with patch.object(market_stock, "request_json", return_value={"listingList": []}) as request_json:
            result = market_stock.fetch_ipo(args)

        self.assertEqual(result, {"listingList": []})
        request_json.assert_called_once_with(
            "/api/domestic/market/ipo/progress?IpoProgressType=LISTING&startIdx=0&pageSize=100"
        )

    def test_upjong_theme_uses_sort_type_params(self) -> None:
        args = argparse.Namespace(sort_type="changeRate")

        with patch.object(market_stock, "request_json", return_value={"upjongRankList": []}) as request_json:
            result = market_stock.fetch_upjong_theme(args)

        self.assertEqual(result, {"upjongRankList": []})
        request_json.assert_called_once_with("/api/domestic/home/upjongTheme/ranking?sortType=changeRate")

    def test_search_top_cli_maps_to_current_params(self) -> None:
        argv = ["market_stock.py", "search-top", "--page-size", "10"]

        with (
            patch.object(sys, "argv", argv),
            patch.object(market_stock, "request_json", return_value=[]) as request_json,
            patch("sys.stdout", new_callable=StringIO),
        ):
            market_stock.main()

        request_json.assert_called_once_with("/api/domestic/market/searchTop?nationType=KOR&startIdx=0&pageSize=10")


class MarketTrendTests(unittest.TestCase):
    def test_trend_foreign_org_uses_read_only_trend_endpoint(self) -> None:
        args = argparse.Namespace(
            investor_type="FOREIGNER",
            market_type="ALL",
            trade_type="KRX",
            start_idx=0,
            page_size=5,
            period_type="DAY",
        )

        with patch.object(market_trend, "request_json", return_value={"sections": {}}) as request_json:
            result = market_trend.fetch_trend_foreign_org(args)

        self.assertEqual(result, {"sections": {}})
        request_json.assert_called_once_with(
            "/api/domestic/market/trend/trendForeignOrg?investorType=FOREIGNER&tradeType=KRX&marketType=ALL&startIdx=0&pageSize=5&periodType=DAY"
        )

    def test_trend_daily_uses_current_daily_endpoint(self) -> None:
        args = argparse.Namespace(
            trade_type="KRX",
            market_type="ALL",
            bizdate="20260529",
            start_idx=0,
            page_size=5,
        )

        with patch.object(market_trend, "request_json", return_value={"content": []}) as request_json:
            result = market_trend.fetch_trend_daily(args)

        self.assertEqual(result, {"content": []})
        request_json.assert_called_once_with(
            "/api/domestic/market/trend/daily?tradeType=KRX&marketType=ALL&bizdate=20260529&startIdx=0&pageSize=5"
        )

    def test_trend_time_chart_uses_current_chart_endpoint(self) -> None:
        args = argparse.Namespace(
            trade_type="KRX",
            market_type="ALL",
            selected_range="1일",
            bizdate="20260529",
            start_date="20260529",
            end_date="20260529",
        )

        with patch.object(market_trend, "request_json", return_value={"netAmounts": []}) as request_json:
            result = market_trend.fetch_trend_time_chart(args)

        self.assertEqual(result, {"netAmounts": []})
        request_json.assert_called_once_with(
            "/api/domestic/market/trend/chart/time?tradeType=KRX&marketType=ALL&selectedRange=1%EC%9D%BC&bizdate=20260529&startDate=20260529&endDate=20260529"
        )

    def test_trend_program_uses_current_program_endpoint(self) -> None:
        args = argparse.Namespace(
            trade_type="KRX",
            krx_market_type="ALL",
            bizdate="20260529",
            start_idx=0,
            page_size=5,
            period_type="TIME",
        )

        with patch.object(market_trend, "request_json", return_value={"content": []}) as request_json:
            result = market_trend.fetch_trend_program(args)

        self.assertEqual(result, {"content": []})
        request_json.assert_called_once_with(
            "/api/domestic/market/trendProgram?tradeType=KRX&krxMarketType=ALL&bizdate=20260529&startIdx=0&pageSize=5&periodType=TIME"
        )

    def test_trend_program_chart_uses_current_program_chart_endpoint(self) -> None:
        args = argparse.Namespace(
            trade_type="KRX",
            krx_market_type="ALL",
            bizdate="20260529",
            start_date="20260529",
            end_date="20260529",
            period_type="TIME",
        )

        with patch.object(market_trend, "request_json", return_value=[]) as request_json:
            result = market_trend.fetch_trend_program_chart(args)

        self.assertEqual(result, [])
        request_json.assert_called_once_with(
            "/api/domestic/market/trendProgram/chart?tradeType=KRX&krxMarketType=ALL&bizdate=20260529&startDate=20260529&endDate=20260529&periodType=TIME"
        )

    def test_trend_program_cli_maps_to_current_endpoint(self) -> None:
        argv = ["market_trend.py", "trend-program", "--bizdate", "20260529", "--page-size", "5"]

        with (
            patch.object(sys, "argv", argv),
            patch.object(market_trend, "request_json", return_value={"content": []}) as request_json,
            patch("sys.stdout", new_callable=StringIO),
        ):
            market_trend.main()

        request_json.assert_called_once_with(
            "/api/domestic/market/trendProgram?tradeType=KRX&krxMarketType=ALL&bizdate=20260529&startIdx=0&pageSize=5&periodType=TIME"
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

    def test_popular_hot_omits_viewer_profile_id(self) -> None:
        args = argparse.Namespace()

        with patch.object(discussion, "request_json", return_value={"posts": []}) as request_json:
            result = discussion.fetch_popular_hot(args)

        self.assertEqual(result, {"posts": []})
        request_json.assert_called_once_with("/api/community/discussion/posts/popular/hot")


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


class StockDetailPageTests(unittest.TestCase):
    def test_chart_prices_uses_security_service_item_chart_endpoint(self) -> None:
        args = argparse.Namespace(code="005930", period_type="day", range=None)

        with patch.object(stock_detail_pages, "request_json", return_value={"priceInfos": []}) as request_json:
            result = stock_detail_pages.fetch_chart_prices(args)

        self.assertEqual(result, {"priceInfos": []})
        request_json.assert_called_once_with("/api/securityService/chart/domestic/item/005930?periodType=day")

    def test_stock_research_uses_item_research_endpoint(self) -> None:
        args = argparse.Namespace(code="005930", page=0, size=10)

        with patch.object(stock_detail_pages, "request_json", return_value=[]) as request_json:
            result = stock_detail_pages.fetch_research(args)

        self.assertEqual(result, [])
        request_json.assert_called_once_with("/api/domestic/research/005930/research?page=0&size=10")

    def test_chart_prices_cli_maps_to_current_endpoint(self) -> None:
        argv = ["stock_detail_pages.py", "chart-prices", "--code", "A005930"]

        with (
            patch.object(sys, "argv", argv),
            patch.object(stock_detail_pages, "request_json", return_value={"priceInfos": []}) as request_json,
            patch("sys.stdout", new_callable=StringIO),
        ):
            stock_detail_pages.main()

        request_json.assert_called_once_with("/api/securityService/chart/domestic/item/005930?periodType=day")


class ResearchTests(unittest.TestCase):
    def test_ranking_uses_research_ranking_endpoint(self) -> None:
        args = argparse.Namespace(ranking_type="SEARCH_TOP", selected_rank=1)

        with patch.object(research, "request_json", return_value={"ranking": []}) as request_json:
            result = research.fetch_ranking(args)

        self.assertEqual(result, {"ranking": []})
        request_json.assert_called_once_with("/api/domestic/research/ranking?rankingType=SEARCH_TOP&selectedRank=1")

    def test_category_latest_keeps_observed_lastest_spelling(self) -> None:
        args = argparse.Namespace()

        with patch.object(research, "request_json", return_value={}) as request_json:
            result = research.fetch_category_latest(args)

        self.assertEqual(result, {})
        request_json.assert_called_once_with("/api/domestic/research/category-lastest")

    def test_industry_research_uses_industry_research_endpoint(self) -> None:
        args = argparse.Namespace()

        with patch.object(research, "request_json", return_value={}) as request_json:
            result = research.fetch_industry_research(args)

        self.assertEqual(result, {})
        request_json.assert_called_once_with("/api/domestic/research/industry-research")

    def test_ranking_cli_maps_to_current_endpoint(self) -> None:
        argv = ["research.py", "ranking", "--ranking-type", "SEARCH_TOP", "--selected-rank", "1"]

        with (
            patch.object(sys, "argv", argv),
            patch.object(research, "request_json", return_value={"ranking": []}) as request_json,
            patch("sys.stdout", new_callable=StringIO),
        ):
            research.main()

        request_json.assert_called_once_with("/api/domestic/research/ranking?rankingType=SEARCH_TOP&selectedRank=1")


class CryptoTests(unittest.TestCase):
    def test_global_news_uses_plain_coin_ticker(self) -> None:
        args = argparse.Namespace(ticker="BTC", page_size=5, offset_timestamp=None)

        with patch.object(crypto, "request_json", return_value={"items": []}) as request_json:
            result = crypto.fetch_global_news(args)

        self.assertEqual(result, {"items": []})
        request_json.assert_called_once_with("/api/coin/globalNews/BTC?pageSize=5")

    def test_global_news_cli_maps_to_current_endpoint(self) -> None:
        argv = ["crypto.py", "global-news", "--ticker", "btc", "--page-size", "5"]

        with (
            patch.object(sys, "argv", argv),
            patch.object(crypto, "request_json", return_value={"items": []}) as request_json,
            patch("sys.stdout", new_callable=StringIO),
        ):
            crypto.main()

        request_json.assert_called_once_with("/api/coin/globalNews/BTC?pageSize=5")

    def test_market_updates_uses_plain_coin_ticker(self) -> None:
        args = argparse.Namespace(ticker="BTC", page_size=5, offset_timestamp="1770000000")

        with patch.object(crypto, "request_json", return_value={"items": []}) as request_json:
            result = crypto.fetch_market_updates(args)

        self.assertEqual(result, {"items": []})
        request_json.assert_called_once_with("/api/coin/marketUpdates/BTC?pageSize=5&offsetTimestamp=1770000000")

    def test_profile_uses_plain_coin_ticker(self) -> None:
        args = argparse.Namespace(ticker="BTC")

        with patch.object(crypto, "request_json", return_value={"info": {}}) as request_json:
            result = crypto.fetch_profile(args)

        self.assertEqual(result, {"info": {}})
        request_json.assert_called_once_with("/api/coin/profile/BTC")


class DiscussionFeedTests(unittest.TestCase):
    def test_feed_uses_general_discussion_posts_endpoint(self) -> None:
        args = argparse.Namespace(page_size=5, offset=None)

        with patch.object(discussion, "request_json", return_value={"posts": []}) as request_json:
            result = discussion.fetch_feed(args)

        self.assertEqual(result, {"posts": []})
        request_json.assert_called_once_with("/api/community/discussion/posts?pageSize=5")

    def test_market_feed_requires_market_index_filter_by_default(self) -> None:
        args = argparse.Namespace(
            filter_type="marketIndex",
            page_size=5,
            offset=None,
            discussion_group_type=None,
        )

        with patch.object(discussion, "request_json", return_value={"posts": []}) as request_json:
            result = discussion.fetch_market_feed(args)

        self.assertEqual(result, {"posts": []})
        request_json.assert_called_once_with("/api/community/discussion/posts/market?filterType=marketIndex&pageSize=5")

    def test_feed_cli_does_not_expose_viewer_profile_id(self) -> None:
        with (
            patch.object(sys, "argv", ["discussion.py", "feed", "--viewer-profile-id", "123"]),
            patch("sys.stderr", new_callable=StringIO),
        ):
            with self.assertRaises(SystemExit):
                discussion.main()


if __name__ == "__main__":
    unittest.main()
