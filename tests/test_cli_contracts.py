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
import notices  # noqa: E402
import research  # noqa: E402
import stock_detail_pages  # noqa: E402


class OutputTests(unittest.TestCase):
    def test_build_path_preserves_repeated_query_params(self) -> None:
        self.assertEqual(
            naverstock_api.build_path("/x", {"causeCode": ["A", "B"]}),
            "/x?causeCode=A&causeCode=B",
        )

    def test_build_path_preserves_bool_values_inside_lists(self) -> None:
        self.assertEqual(
            naverstock_api.build_path("/x", {"flag": [True, False]}),
            "/x?flag=true&flag=false",
        )

    def test_emit_output_writes_unicode_to_text_stdout(self) -> None:
        stream = StringIO()

        with patch.object(sys, "stdout", stream):
            naverstock_api.emit_output("낯선문자\u11a2\n", None)

        self.assertEqual(stream.getvalue(), "낯선문자\u11a2\n")

    def test_emit_output_ignores_stdout_reconfigure_oserror(self) -> None:
        class ReconfigureRaisesOSError(StringIO):
            def reconfigure(self, **_: object) -> None:
                raise OSError("unsupported stream")

        stream = ReconfigureRaisesOSError()

        with patch.object(sys, "stdout", stream):
            naverstock_api.emit_output("ok\n", None)

        self.assertEqual(stream.getvalue(), "ok\n")


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

    def test_exchange_prices_use_currency_specific_endpoint(self) -> None:
        args = argparse.Namespace(currency="USD", start_idx=0, page_size=20)

        with patch.object(marketindex, "request_json", return_value=[]) as request_json:
            marketindex.fetch_exchange_prices(args)

        request_json.assert_called_once_with("/api/domestic/exchange/USD/list?startIdx=0&pageSize=20")

    def test_market_polling_uses_observed_marketindex_endpoint(self) -> None:
        args = argparse.Namespace(category="metals", codes="GCcv1")

        with patch.object(marketindex, "request_json", return_value={}) as request_json:
            marketindex.fetch_market_polling(args)

        request_json.assert_called_once_with("/api/polling/marketindex/metals/GCcv1")

    def test_foreign_chart_uses_foreign_asset_type(self) -> None:
        args = argparse.Namespace(asset_type="index", code=".DJI", period_type="day", range=None)

        with patch.object(marketindex, "request_json", return_value={}) as request_json:
            marketindex.fetch_foreign_chart(args)

        request_json.assert_called_once_with("/api/securityService/chart/foreign/index/.DJI?periodType=day")

    def test_bank_round_chart_uses_stock_security_v2_endpoint(self) -> None:
        args = argparse.Namespace(currency="USD", bank_type="hana")

        with patch.object(marketindex, "request_json", return_value={}) as request_json:
            marketindex.fetch_bank_round_chart(args)

        request_json.assert_called_once_with("/api/stockSecurity/exchange-rates/v2/USD/charts/round?bankType=hana")

    def test_krx_gold_uses_domestic_gold_endpoint(self) -> None:
        with patch.object(marketindex, "request_json", return_value={}) as request_json:
            marketindex.fetch_krx_gold(argparse.Namespace())

        request_json.assert_called_once_with("/api/stockDomestic/gold/sise/krx")

    def test_standard_interest_calendars_use_nation_and_paging(self) -> None:
        args = argparse.Namespace(nation_type="USA", page=1, page_size=20)

        with patch.object(marketindex, "request_json", return_value={}) as request_json:
            marketindex.fetch_standard_interest_calendars(args)

        request_json.assert_called_once_with(
            "/api/securityService/marketindex/standardInterest/USA/calendars?page=1&pageSize=20"
        )

    def test_economic_upcoming_preserves_repeated_nation_types(self) -> None:
        args = argparse.Namespace(limit=5, nation_type=["USA", "KOR"])

        with patch.object(marketindex, "request_json", return_value={"contents": []}) as request_json:
            result = marketindex.fetch_economic_upcoming(args)

        self.assertEqual(result, {"contents": []})
        request_json.assert_called_once_with(
            "/api/securityService/economic/indicator/nations/upcoming?limit=5&nationTypeList=USA&nationTypeList=KOR"
        )


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

    def test_aggregate_uses_read_post_body(self) -> None:
        args = argparse.Namespace(
            trade_type="KRX",
            market_type="KOSPI",
            period_type="TIME",
            start_date=None,
            end_date=None,
        )

        with patch.object(market_trend, "request_json", return_value={"success": True}) as request_json:
            result = market_trend.fetch_aggregate(args)

        self.assertEqual(result, {"success": True})
        request_json.assert_called_once_with(
            "/api/domestic/home/marketaggregate/aggregateInvestor",
            method="POST",
            body={
                "sections": {
                    "investorTrend": {
                        "tradeType": "KRX",
                        "marketType": "KOSPI",
                        "periodType": "TIME",
                    }
                }
            },
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

    def test_item_posts_include_required_current_filters(self) -> None:
        args = argparse.Namespace(
            item_code="005930",
            discussion_type="domesticStock",
            page_size=5,
            offset=None,
            is_holder_only=False,
            excludes_item_news=False,
            is_item_news_only=False,
        )

        with patch.object(discussion, "request_json", return_value={"posts": []}) as request_json:
            result = discussion.fetch_item_posts(args)

        self.assertEqual(result, {"posts": []})
        request_json.assert_called_once_with(
            "/api/community/discussion/posts/by-item?itemCode=005930&discussionType=domesticStock&pageSize=5&isHolderOnly=false&excludesItemNews=false&isItemNewsOnly=false"
        )

    def test_stats_by_items_uses_start_date_and_domestic_codes(self) -> None:
        args = argparse.Namespace(start_date="2026-07-02", domestic_codes=["005930", "000660"], foreign_codes=None)

        with patch.object(discussion, "request_json", return_value={"stats": []}) as request_json:
            result = discussion.fetch_stats_by_items(args)

        self.assertEqual(result, {"stats": []})
        request_json.assert_called_once_with(
            "/api/community/discussion/stats/by-items?startDate=2026-07-02&domesticCodes=005930%2C000660"
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

    def test_notice_repeats_cause_code_query_params(self) -> None:
        args = argparse.Namespace(code="005930", start_idx=0, page_size=5, cause_code=["20", "30"])

        with patch.object(stock_detail_pages, "request_json", return_value={"content": []}) as request_json:
            result = stock_detail_pages.fetch_notice(args)

        self.assertEqual(result, {"content": []})
        request_json.assert_called_once_with(
            "/api/domestic/detail/notice?itemCode=005930&startIdx=0&pageSize=5&causeCode=20&causeCode=30"
        )

    def test_chart_prices_cli_maps_to_current_endpoint(self) -> None:
        argv = ["stock_detail_pages.py", "chart-prices", "--code", "A005930"]

        with (
            patch.object(sys, "argv", argv),
            patch.object(stock_detail_pages, "request_json", return_value={"priceInfos": []}) as request_json,
            patch("sys.stdout", new_callable=StringIO),
        ):
            stock_detail_pages.main()

        request_json.assert_called_once_with("/api/securityService/chart/domestic/item/005930?periodType=day")

    def test_finance_menu_uses_stock_security_finance_endpoint(self) -> None:
        args = argparse.Namespace(code="A005930")

        with patch.object(stock_detail_pages, "request_json", return_value={"menus": []}) as request_json:
            result = stock_detail_pages.fetch_finance_menu(args)

        self.assertEqual(result, {"menus": []})
        request_json.assert_called_once_with("/api/stockSecurity/finances/v1/domestic/005930/menu-info")

    def test_finance_esg_uses_stock_security_finance_endpoint(self) -> None:
        args = argparse.Namespace(code="005930")

        with patch.object(stock_detail_pages, "request_json", return_value={"grade": "A"}) as request_json:
            result = stock_detail_pages.fetch_finance_esg(args)

        self.assertEqual(result, {"grade": "A"})
        request_json.assert_called_once_with("/api/stockSecurity/finances/v1/domestic/005930/esg")


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

    def test_v1_category_uses_stock_security_research_endpoint(self) -> None:
        args = argparse.Namespace(category="company", index=0, size=2, broker_codes=None, item_code=None)

        with patch.object(research, "request_json", return_value={"content": []}) as request_json:
            result = research.fetch_v1_category(args)

        self.assertEqual(result, {"content": []})
        request_json.assert_called_once_with("/api/stockSecurity/researches/v1/company?index=0&size=2")

    def test_v1_by_items_repeats_item_codes(self) -> None:
        args = argparse.Namespace(item_codes=["A005930", "000660"], size=2)

        with patch.object(research, "request_json", return_value={"content": []}) as request_json:
            result = research.fetch_v1_by_items(args)

        self.assertEqual(result, {"content": []})
        request_json.assert_called_once_with(
            "/api/stockSecurity/researches/v1/company/by-items?itemCodes=005930&itemCodes=000660&size=2"
        )

    def test_v1_latest_research_uses_latest_research_endpoint(self) -> None:
        args = argparse.Namespace(size=2)

        with patch.object(research, "request_json", return_value={"content": []}) as request_json:
            result = research.fetch_v1_latest(args)

        self.assertEqual(result, {"content": []})
        request_json.assert_called_once_with("/api/stockSecurity/researches/v1/latestResearch?size=2")

    def test_v1_brokers_uses_stock_security_brokers_endpoint(self) -> None:
        args = argparse.Namespace()

        with patch.object(research, "request_json", return_value=[]) as request_json:
            result = research.fetch_v1_brokers(args)

        self.assertEqual(result, [])
        request_json.assert_called_once_with("/api/stockSecurity/researches/v1/brokers")

    def test_v1_analysis_focus_uses_stock_security_endpoint(self) -> None:
        args = argparse.Namespace()

        with patch.object(research, "request_json", return_value={}) as request_json:
            result = research.fetch_v1_analysis_focus(args)

        self.assertEqual(result, {})
        request_json.assert_called_once_with("/api/stockSecurity/researches/v1/analysis-focus")


class NoticesTests(unittest.TestCase):
    def test_notices_list_uses_stock_security_notice_endpoint(self) -> None:
        args = argparse.Namespace(size=2, cursor="abc")

        with patch.object(notices, "request_json", return_value={"content": []}) as request_json:
            result = notices.fetch_list(args)

        self.assertEqual(result, {"content": []})
        request_json.assert_called_once_with("/api/stockSecurity/notices/v2?size=2&cursor=abc")

    def test_notices_detail_uses_notice_id_path(self) -> None:
        args = argparse.Namespace(notice_id="123")

        with patch.object(notices, "request_json", return_value={"noticeId": "123"}) as request_json:
            result = notices.fetch_detail(args)

        self.assertEqual(result, {"noticeId": "123"})
        request_json.assert_called_once_with("/api/stockSecurity/notices/v2/123")

    def test_notices_banners_uses_banner_endpoint(self) -> None:
        args = argparse.Namespace(size=2, banner_type="PC_TOP")

        with patch.object(notices, "request_json", return_value={"banners": []}) as request_json:
            result = notices.fetch_banners(args)

        self.assertEqual(result, {"banners": []})
        request_json.assert_called_once_with("/api/stockSecurity/notices/v2/banners?size=2&type=PC_TOP")

    def test_notices_cli_rejects_unsafe_or_unbounded_inputs(self) -> None:
        argv_sets = (
            ["notices.py", "detail", "--notice-id", "../personal"],
            ["notices.py", "list", "--size", "101"],
            ["notices.py", "list", "--cursor", "unsafe/cursor"],
            ["notices.py", "banners", "--banner-type", "PC/TOP"],
        )
        for argv in argv_sets:
            with (
                self.subTest(argv=argv),
                patch.object(sys, "argv", argv),
                patch("sys.stderr", new_callable=StringIO),
                self.assertRaises(SystemExit),
            ):
                notices.main()


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

    def test_categories_ranking_uses_current_category_endpoint(self) -> None:
        args = argparse.Namespace(exchange_type="UPBIT", page=1, page_size=2)

        with patch.object(crypto, "request_json", return_value={"categories": []}) as request_json:
            result = crypto.fetch_categories_ranking(args)

        self.assertEqual(result, {"categories": []})
        request_json.assert_called_once_with("/api/coin/categories/ranking?exchangeType=UPBIT&page=1&pageSize=2")

    def test_prices_repeats_fqnf_tickers(self) -> None:
        args = argparse.Namespace(fqnf_tickers=["BTC_KRW_UPBIT", "ETH_KRW_UPBIT"])

        with patch.object(crypto, "request_json", return_value={"prices": []}) as request_json:
            result = crypto.fetch_prices(args)

        self.assertEqual(result, {"prices": []})
        request_json.assert_called_once_with(
            "/api/coin/prices?fqnfTickers=BTC_KRW_UPBIT&fqnfTickers=ETH_KRW_UPBIT"
        )

    def test_global_market_trend_uses_current_endpoint(self) -> None:
        args = argparse.Namespace()

        with patch.object(crypto, "request_json", return_value={}) as request_json:
            result = crypto.fetch_global_market_trend(args)

        self.assertEqual(result, {})
        request_json.assert_called_once_with("/api/coin/globalMarketTrend")

    def test_coinmacro_news_uses_security_fe_endpoint(self) -> None:
        args = argparse.Namespace(page=1, page_size=10)

        with patch.object(crypto, "request_json", return_value={"articles": []}) as request_json:
            result = crypto.fetch_coinmacro_news(args)

        self.assertEqual(result, {"articles": []})
        request_json.assert_called_once_with("/api/securityFe/api/news/coinmacro?page=1&pageSize=10")

    def test_coin_briefing_uses_security_ai_endpoint(self) -> None:
        args = argparse.Namespace(exchange_type="UPBIT", ticker="btc")

        with patch.object(crypto, "request_json", return_value={}) as request_json:
            result = crypto.fetch_coin_briefing(args)

        self.assertEqual(result, {})
        request_json.assert_called_once_with("/api/securityAi/coinBriefing/current?exchangeType=UPBIT&nfTicker=BTC")


class DiscussionFeedTests(unittest.TestCase):
    def test_feed_uses_general_discussion_posts_endpoint(self) -> None:
        args = argparse.Namespace(page_size=5, offset=None, discussion_group_type=None)

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
