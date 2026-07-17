#!/usr/bin/env python3
"""Fetch public Npay Stock home-page and cross-market payloads."""

from __future__ import annotations

import argparse
import datetime as dt
import re
from typing import Any

from naverstock_api import (
    bounded_int,
    build_path,
    emit_output,
    normalize_item_code,
    render_json,
    request_json,
    validate_identifier,
)


DEFAULT_INDICATORS = "KOSPI,KOSDAQ,.DJI,.IXIC,.INX,FX_USDKRW,GCcv1,CLcv1"
DOMESTIC_NOTABLE_ETF_ORDER_TYPES = (
    "amount_etf",
    "up_etf",
    "1week_earn_rate",
    "dividend_earn_rate",
)
FOREIGN_NOTABLE_ETF_ORDER_TYPES = ("priceTop", "up", "return1Month", "dividend")
_INDICATOR_CODE = re.compile(r"^(?:\.?[A-Za-z0-9][A-Za-z0-9._=-]{0,31})$")
_DOMESTIC_CODE = re.compile(r"^[A-Z0-9]{6}$")


def _bounded_integer(name: str, minimum: int, maximum: int) -> Any:
    def parse(value: str) -> int:
        try:
            return bounded_int(value, name=name, minimum=minimum, maximum=maximum)
        except ValueError as exc:
            raise argparse.ArgumentTypeError(str(exc)) from exc

    return parse


def _iso_date(value: str) -> str:
    try:
        return dt.date.fromisoformat(value).isoformat()
    except (TypeError, ValueError) as exc:
        raise argparse.ArgumentTypeError("date must be a valid YYYY-MM-DD date") from exc


def _short_text(value: str) -> str:
    clean = value.strip()
    if not clean or len(clean) > 50 or any(ord(char) < 32 or ord(char) == 127 for char in clean):
        raise argparse.ArgumentTypeError("value must be 1-50 printable characters")
    return clean


def _opaque_cursor(value: str) -> str:
    clean = value.strip()
    if not clean or len(clean) > 512 or re.search(r"[^A-Za-z0-9._~+=:/-]", clean):
        raise argparse.ArgumentTypeError("page-token must be a URL-safe cursor of at most 512 characters")
    return clean


def _briefing_id(value: str) -> str:
    try:
        return validate_identifier(value, name="briefing-id")
    except ValueError as exc:
        raise argparse.ArgumentTypeError(str(exc)) from exc


def _domestic_code(value: str) -> str:
    clean = normalize_item_code(value).upper()
    if not _DOMESTIC_CODE.fullmatch(clean):
        raise argparse.ArgumentTypeError("code must be a six-character domestic item code")
    return clean


def _indicator_codes(value: str) -> str:
    codes = value.split(",")
    if not 1 <= len(codes) <= 30 or any(not _INDICATOR_CODE.fullmatch(code) for code in codes):
        raise argparse.ArgumentTypeError(
            "indicator-codes must contain 1-30 comma-separated market codes without path separators"
        )
    return ",".join(codes)


def fetch_market_info(args: argparse.Namespace) -> Any:
    return request_json(f"/api/domestic/market/{args.trade_type}/info")


def fetch_operating_time(args: argparse.Namespace) -> Any:
    return request_json(f"/api/foreign/operatingTime/exchange/{args.exchange}")


def fetch_market_briefing(args: argparse.Namespace) -> Any:
    return request_json("/api/securityAi/marketBriefing/current?marketBriefing=domain")


def fetch_market_briefing_list(args: argparse.Namespace) -> Any:
    return request_json(
        build_path(
            "/api/securityAi/marketBriefing",
            {"date": args.date, "size": args.size, "pageToken": args.page_token},
        )
    )


def fetch_market_briefing_detail(args: argparse.Namespace) -> Any:
    briefing_id = validate_identifier(args.briefing_id, name="briefing-id")
    return request_json(f"/api/securityAi/marketBriefing/{briefing_id}")


def fetch_shorttents(args: argparse.Namespace) -> Any:
    return request_json(
        build_path(
            "/api/shorttents",
            {
                "source": args.source,
                "type": args.content_type,
                "category_first": args.category_first,
                "nscs": args.nscs,
            },
        )
    )


def fetch_money_story(args: argparse.Namespace) -> Any:
    category_ids = args.main_category_id or [1]
    return request_json(
        build_path(
            "/api/content/moneyStory",
            {"mainCategoryIdList": category_ids, "size": args.size},
        )
    )


def fetch_indicators(args: argparse.Namespace) -> Any:
    return request_json(
        build_path(
            "/api/securityService/integration/indicators",
            {"indicatorCodes": args.indicator_codes},
        )
    )


def fetch_notable_etf(args: argparse.Namespace) -> Any:
    order_type = args.order_type or ("amount_etf" if args.nation == "domestic" else "up")
    return request_json(
        build_path(
            f"/api/{args.nation}/market/home/notableETF",
            {
                "orderType": order_type,
                "startIdx": args.start_idx,
                "pageSize": args.page_size,
            },
        )
    )


def fetch_economic_upcoming(args: argparse.Namespace) -> Any:
    nation_types = args.nation_type or ["KOR", "USA"]
    return request_json(
        build_path(
            "/api/securityService/economic/indicator/nations/upcoming",
            {
                "gteImportance": args.gte_importance,
                "limit": args.limit,
                "nationTypeList": nation_types,
            },
        )
    )


def fetch_public_ranking(args: argparse.Namespace) -> Any:
    ranking = "assetAmount" if args.ranking_type == "asset" else "earningRate"
    return request_json(
        build_path(
            f"/api/domestic/home/ranking/{ranking}/all",
            {"startIdx": args.start_idx, "pageSize": args.page_size},
        )
    )


def fetch_holding_stock_ranking(args: argparse.Namespace) -> Any:
    return request_json("/api/securityService/home/v3/ranking/more/domestic/holdingStock/all")


def fetch_related_stock(args: argparse.Namespace) -> Any:
    return request_json(
        f"/api/securityService/home/v3/stock/{normalize_item_code(args.code)}/related"
    )


def add_output(parser: argparse.ArgumentParser) -> None:
    parser.add_argument("--output")


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    sub = parser.add_subparsers(dest="command", required=True)

    market_info = sub.add_parser("market-info", help="KRX or NXT market status")
    market_info.add_argument("--trade-type", choices=["KRX", "NXT"], default="KRX")
    add_output(market_info)
    market_info.set_defaults(func=fetch_market_info)

    operating_time = sub.add_parser("operating-time", help="Foreign exchange operating time")
    operating_time.add_argument(
        "--exchange",
        choices=["NASDAQ", "SHANGHAI", "HONG_KONG", "TOKYO", "HANOI"],
        default="NASDAQ",
    )
    add_output(operating_time)
    operating_time.set_defaults(func=fetch_operating_time)

    briefing = sub.add_parser("market-briefing", help="AI market briefing observed on the home page")
    add_output(briefing)
    briefing.set_defaults(func=fetch_market_briefing)

    briefing_list = sub.add_parser("market-briefing-list", help="AI market briefing list by date")
    briefing_list.add_argument("--date", type=_iso_date, required=True)
    briefing_list.add_argument("--size", type=_bounded_integer("size", 1, 100), default=20)
    briefing_list.add_argument("--page-token", type=_opaque_cursor)
    add_output(briefing_list)
    briefing_list.set_defaults(func=fetch_market_briefing_list)

    briefing_detail = sub.add_parser("market-briefing-detail", help="AI market briefing detail by ID")
    briefing_detail.add_argument("--briefing-id", type=_briefing_id, required=True)
    add_output(briefing_detail)
    briefing_detail.set_defaults(func=fetch_market_briefing_detail)

    shorttents = sub.add_parser("shorttents", help="Compact public finance content feed")
    shorttents.add_argument("--source", choices=["pc.npay_finhome"], default="pc.npay_finhome")
    shorttents.add_argument("--content-type", choices=["compact"], default="compact")
    shorttents.add_argument("--category-first", type=_short_text, default="증권")
    shorttents.add_argument("--nscs", type=_bounded_integer("nscs", 0, 100_000), default=0)
    add_output(shorttents)
    shorttents.set_defaults(func=fetch_shorttents)

    money_story = sub.add_parser("money-story", help="Public money-story content")
    money_story.add_argument(
        "--main-category-id",
        type=_bounded_integer("main-category-id", 1, 100_000),
        action="append",
    )
    money_story.add_argument("--size", type=_bounded_integer("size", 1, 100), default=3)
    add_output(money_story)
    money_story.set_defaults(func=fetch_money_story)

    indicators = sub.add_parser("indicators", help="Integrated home-page market indicators")
    indicators.add_argument("--indicator-codes", type=_indicator_codes, default=DEFAULT_INDICATORS)
    add_output(indicators)
    indicators.set_defaults(func=fetch_indicators)

    notable_etf = sub.add_parser("notable-etf", help="Domestic or foreign notable ETFs")
    notable_etf.add_argument("--nation", choices=["domestic", "foreign"], default="domestic")
    notable_etf.add_argument(
        "--order-type",
        choices=DOMESTIC_NOTABLE_ETF_ORDER_TYPES + FOREIGN_NOTABLE_ETF_ORDER_TYPES,
        help="Defaults to amount_etf for domestic and up for foreign",
    )
    notable_etf.add_argument("--start-idx", type=_bounded_integer("start-idx", 0, 10_000), default=0)
    notable_etf.add_argument("--page-size", type=_bounded_integer("page-size", 1, 100), default=10)
    add_output(notable_etf)
    notable_etf.set_defaults(func=fetch_notable_etf)

    economic = sub.add_parser("economic-upcoming", help="Important upcoming economic indicators")
    economic.add_argument("--gte-importance", type=_bounded_integer("gte-importance", 1, 5), default=3)
    economic.add_argument("--limit", type=_bounded_integer("limit", 1, 100), default=3)
    economic.add_argument("--nation-type", choices=["KOR", "USA", "CHN", "JPN", "EUR"], action="append")
    add_output(economic)
    economic.set_defaults(func=fetch_economic_upcoming)

    ranking = sub.add_parser("public-ranking", help="Public all-user asset or earning-rate ranking")
    ranking.add_argument("--ranking-type", choices=["asset", "earning"], required=True)
    ranking.add_argument("--start-idx", type=_bounded_integer("start-idx", 0, 10_000), default=0)
    ranking.add_argument("--page-size", type=_bounded_integer("page-size", 1, 100), default=20)
    add_output(ranking)
    ranking.set_defaults(func=fetch_public_ranking)

    holding = sub.add_parser("holding-stock-ranking", help="Public all-user holding-stock ranking")
    add_output(holding)
    holding.set_defaults(func=fetch_holding_stock_ranking)

    related = sub.add_parser("related-stock", help="Public related stocks for a domestic code")
    related.add_argument("--code", required=True, type=_domestic_code)
    add_output(related)
    related.set_defaults(func=fetch_related_stock)

    args = parser.parse_args()
    if args.command == "money-story" and args.main_category_id and len(args.main_category_id) > 20:
        parser.error("money-story accepts at most 20 --main-category-id values")
    if args.command == "economic-upcoming" and args.nation_type and len(args.nation_type) > 10:
        parser.error("economic-upcoming accepts at most 10 --nation-type values")
    if args.command == "notable-etf" and args.order_type:
        allowed = (
            DOMESTIC_NOTABLE_ETF_ORDER_TYPES
            if args.nation == "domestic"
            else FOREIGN_NOTABLE_ETF_ORDER_TYPES
        )
        if args.order_type not in allowed:
            parser.error(f"{args.order_type} is not valid for --nation {args.nation}")
    emit_output(render_json(args.func(args)), args.output)


if __name__ == "__main__":
    main()
