#!/usr/bin/env python3
"""Fetch public read-only Naver Stock foreign market and security payloads."""

from __future__ import annotations

import argparse
import re
from typing import Any, Callable

from naverstock_api import build_path, emit_output, render_json, request_json


NATIONS = ("usa", "chn", "hkg", "jpn", "vnm")
NATION_API_NAMES = {nation: nation.upper() for nation in NATIONS}
TRADE_TYPES = ("ALL", "NSQ", "NYS", "AMX", "SHH", "SHZ", "HKG", "TYO", "HSX", "HNX")
STOCK_ORDER_TYPES = ("quantTop", "priceTop", "up", "down", "marketValue", "dividend")
ETF_ORDER_TYPES = ("quantTop", "priceTop", "up", "down", "marketValue", "dividend")
NOTABLE_ETF_ORDER_TYPES = ("priceTop", "up", "return1Month", "dividend")
POLL_TYPES = ("stock", "etf", "index")
EXCHANGES = ("NASDAQ", "NYSE", "AMEX")

_REUTERS_CODE = re.compile(r"^(?:[A-Z0-9][A-Z0-9._-]{0,31}|\.[A-Z0-9][A-Z0-9._-]{0,30})$")
_INDUSTRY_CODE = re.compile(r"^[0-9]{2,12}$")
_THEME_CODE = re.compile(r"^(?:all|[A-Za-z0-9_-]{1,20})$")


def bounded_int(name: str, minimum: int, maximum: int) -> Callable[[str], int]:
    """Build an argparse integer parser with an explicit safe range."""

    def parse(value: str) -> int:
        try:
            result = int(value)
        except ValueError as exc:
            raise argparse.ArgumentTypeError(f"{name} must be an integer") from exc
        if not minimum <= result <= maximum:
            raise argparse.ArgumentTypeError(f"{name} must be between {minimum} and {maximum}")
        return result

    return parse


def reuters_code(value: str) -> str:
    """Normalize a public Reuters code while rejecting path/query separators."""

    result = value.strip().upper()
    if not _REUTERS_CODE.fullmatch(result):
        raise argparse.ArgumentTypeError(
            "Reuters code must contain only letters, digits, dot, underscore, or hyphen"
        )
    return result


def industry_code(value: str) -> str:
    result = value.strip()
    if not _INDUSTRY_CODE.fullmatch(result):
        raise argparse.ArgumentTypeError("industry code must contain 2-12 digits")
    return result


def theme_code(value: str) -> str:
    result = value.strip()
    if not _THEME_CODE.fullmatch(result):
        raise argparse.ArgumentTypeError("theme code must be 'all' or a short alphanumeric code")
    return result


def fetch_stocks(args: argparse.Namespace) -> Any:
    return request_json(
        build_path(
            "/api/foreign/market/stock/global",
            {
                "nation": args.nation,
                "tradeType": args.trade_type,
                "orderType": args.order_type,
                "startIdx": args.start_idx,
                "pageSize": args.page_size,
            },
        )
    )


def fetch_sectors(args: argparse.Namespace) -> Any:
    return request_json(f"/api/foreign/market/{NATION_API_NAMES[args.nation]}/upjong/list")


def fetch_sector_stocks(args: argparse.Namespace) -> Any:
    return request_json(
        build_path(
            f"/api/foreign/market/{NATION_API_NAMES[args.nation]}/upjong/{args.industry_code}/list",
            {"orderType": args.order_type, "startIdx": args.start_idx, "pageSize": args.page_size},
        )
    )


def fetch_etf_themes(_: argparse.Namespace) -> Any:
    return request_json("/api/foreign/market/etf/themes")


def fetch_etfs(args: argparse.Namespace) -> Any:
    return request_json(
        build_path(
            "/api/foreign/market/etf/usa",
            {
                "orderType": args.order_type,
                "largeCode": args.large_code,
                "middleCode": args.middle_code,
                "startIdx": args.start_idx,
                "pageSize": args.page_size,
            },
        )
    )


def fetch_notable_etfs(args: argparse.Namespace) -> Any:
    return request_json(
        build_path(
            "/api/foreign/market/home/notableETF",
            {
                "orderType": args.order_type,
                "largeCode": args.large_code,
                "middleCode": args.middle_code,
                "startIdx": args.start_idx,
                "pageSize": args.page_size,
            },
        )
    )


def fetch_etf_theme_list(args: argparse.Namespace) -> Any:
    return request_json(
        build_path(
            "/api/foreign/market/usa/etf/themeList",
            {"middleCode": args.middle_code, "count": args.count},
        )
    )


def fetch_stock_basic(args: argparse.Namespace) -> Any:
    return request_json(f"/api/securityService/stock/{args.code}/basic")


def fetch_stock_consensus(args: argparse.Namespace) -> Any:
    return request_json(f"/api/securityService/stock/{args.code}/consensus")


def fetch_stock_overview(args: argparse.Namespace) -> Any:
    return request_json(f"/api/securityService/stock/{args.code}/overview")


def fetch_finance(args: argparse.Namespace) -> Any:
    if args.section == "overview":
        path = "/api/securityService/stock/overview"
    elif args.section == "summary":
        path = "/api/securityService/stock/finance/summary"
    elif args.section == "finance":
        path = f"/api/securityService/stock/finance/{args.period}"
    else:
        path = f"/api/securityService/stock/finance/{args.section}/{args.period}"
    return request_json(build_path(path, {"reutersCode": args.code}))


def fetch_stock_prices(args: argparse.Namespace) -> Any:
    return request_json(
        build_path(
            f"/api/securityService/stock/{args.code}/price",
            {"page": args.page, "pageSize": args.page_size},
        )
    )


def fetch_foreign_detail(args: argparse.Namespace) -> Any:
    # The current web bundle sends the literal codeType=ETF for this shared
    # stock/ETF master-detail endpoint, including when the result is a stock.
    return request_json(build_path(f"/api/foreign/{args.code}/detail", {"codeType": "ETF"}))


def fetch_etf_prices(args: argparse.Namespace) -> Any:
    return request_json(
        build_path(
            f"/api/securityService/etf/{args.code}/price",
            {"page": args.page, "pageSize": args.page_size},
        )
    )


def fetch_etf_related(args: argparse.Namespace) -> Any:
    return request_json(
        build_path(
            f"/api/foreign/v2/market/etf/usa/{args.code}",
            {"startIdx": args.start_idx, "pageSize": args.page_size},
        )
    )


def fetch_index_basic(args: argparse.Namespace) -> Any:
    return request_json(f"/api/securityService/index/{args.code}/basic")


def fetch_index_prices(args: argparse.Namespace) -> Any:
    return request_json(
        build_path(
            f"/api/securityService/index/{args.code}/price",
            {"page": args.page, "pageSize": args.page_size},
        )
    )


def fetch_index_constituents(args: argparse.Namespace) -> Any:
    return request_json(
        build_path(
            f"/api/securityService/index/{args.code}/enrollStocks",
            {"page": args.page, "pageSize": args.page_size},
        )
    )


def fetch_poll(args: argparse.Namespace) -> Any:
    codes = ",".join(args.code)
    return request_json(build_path(f"/api/polling/worldstock/{args.security_type}", {"reutersCodes": codes}))


def fetch_exchange_time(args: argparse.Namespace) -> Any:
    return request_json(f"/api/foreign/operatingTime/exchange/{args.exchange}")


def fetch_stock_world_news(args: argparse.Namespace) -> Any:
    return request_json(
        build_path(
            "/api/foreign/worldStock/list",
            {"reutersCode": args.code, "page": args.page, "pageSize": args.page_size},
        )
    )


def fetch_stock_local_news(args: argparse.Namespace) -> Any:
    return request_json(
        build_path(
            "/api/domestic/detail/news",
            {"itemCode": args.code, "page": args.page, "pageSize": args.page_size},
        )
    )


def add_output(parser: argparse.ArgumentParser) -> None:
    parser.add_argument("--output", help="Write output to a file instead of stdout")


def add_bounded_paging(parser: argparse.ArgumentParser, *, page_based: bool = False) -> None:
    if page_based:
        parser.add_argument("--page", type=bounded_int("page", 1, 1000), default=1)
    else:
        parser.add_argument("--start-idx", type=bounded_int("start index", 0, 10000), default=0)
    parser.add_argument("--page-size", type=bounded_int("page size", 1, 100), default=20)
    add_output(parser)


def add_code(parser: argparse.ArgumentParser, help_text: str) -> None:
    parser.add_argument("--code", required=True, type=reuters_code, help=help_text)
    add_output(parser)


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    sub = parser.add_subparsers(dest="command", required=True)

    stocks = sub.add_parser("stocks", help="Foreign country stock ranking/list")
    stocks.add_argument("--nation", choices=NATIONS, default="usa")
    stocks.add_argument("--trade-type", choices=TRADE_TYPES, default="ALL")
    stocks.add_argument("--order-type", choices=STOCK_ORDER_TYPES, default="marketValue")
    add_bounded_paging(stocks)
    stocks.set_defaults(func=fetch_stocks)

    sectors = sub.add_parser("sectors", help="Foreign industry/sector list")
    sectors.add_argument("--nation", choices=NATIONS, default="usa")
    add_output(sectors)
    sectors.set_defaults(func=fetch_sectors)

    sector_stocks = sub.add_parser("sector-stocks", help="Stocks in a foreign industry/sector")
    sector_stocks.add_argument("--nation", choices=NATIONS, default="usa")
    sector_stocks.add_argument("--industry-code", required=True, type=industry_code)
    sector_stocks.add_argument("--order-type", choices=STOCK_ORDER_TYPES, default="marketValue")
    add_bounded_paging(sector_stocks)
    sector_stocks.set_defaults(func=fetch_sector_stocks)

    etf_themes = sub.add_parser("etf-themes", help="US ETF large/middle theme filters")
    add_output(etf_themes)
    etf_themes.set_defaults(func=fetch_etf_themes)

    etfs = sub.add_parser("etfs", help="US ETF ranking/list")
    etfs.add_argument("--order-type", choices=ETF_ORDER_TYPES, default="marketValue")
    etfs.add_argument("--large-code", type=theme_code, default="all")
    etfs.add_argument("--middle-code", type=theme_code, default="all")
    add_bounded_paging(etfs)
    etfs.set_defaults(func=fetch_etfs)

    notable = sub.add_parser("notable-etfs", help="Notable US ETF list used on market/home")
    notable.add_argument("--order-type", choices=NOTABLE_ETF_ORDER_TYPES, default="up")
    notable.add_argument("--large-code", type=theme_code)
    notable.add_argument("--middle-code", type=theme_code)
    add_bounded_paging(notable)
    notable.set_defaults(func=fetch_notable_etfs)

    theme_list = sub.add_parser("etf-theme-list", help="US ETF list for one middle theme")
    theme_list.add_argument("--middle-code", required=True, type=theme_code)
    theme_list.add_argument("--count", type=bounded_int("count", 1, 20), default=3)
    add_output(theme_list)
    theme_list.set_defaults(func=fetch_etf_theme_list)

    for name, help_text, func in [
        ("stock-basic", "Foreign stock basic/current summary", fetch_stock_basic),
        ("stock-consensus", "Foreign stock analyst consensus", fetch_stock_consensus),
        ("stock-overview", "Foreign stock company overview", fetch_stock_overview),
        ("foreign-detail", "Shared foreign stock/ETF master detail", fetch_foreign_detail),
        ("index-basic", "Foreign index basic/current summary", fetch_index_basic),
    ]:
        command = sub.add_parser(name, help=help_text)
        add_code(command, "Reuters code, for example NVDA.O, VOO, or .IXIC")
        command.set_defaults(func=func)

    finance = sub.add_parser("finance", help="Foreign stock finance overview, statements, ratios, or summary")
    finance.add_argument("--code", required=True, type=reuters_code)
    finance.add_argument(
        "--section",
        choices=["overview", "summary", "finance", "ratios", "balance", "income", "cash"],
        required=True,
    )
    finance.add_argument("--period", choices=["annual", "quarter"], default="annual")
    add_output(finance)
    finance.set_defaults(func=fetch_finance)

    for name, help_text, func in [
        ("stock-prices", "Foreign stock daily price rows", fetch_stock_prices),
        ("etf-prices", "Foreign ETF daily price rows", fetch_etf_prices),
        ("index-prices", "Foreign index daily price rows", fetch_index_prices),
        ("index-constituents", "Foreign index constituent stocks", fetch_index_constituents),
    ]:
        command = sub.add_parser(name, help=help_text)
        command.add_argument("--code", required=True, type=reuters_code)
        add_bounded_paging(command, page_based=True)
        command.set_defaults(func=func)

    related = sub.add_parser("etf-related", help="US ETF theme peers related to an ETF")
    related.add_argument("--code", required=True, type=reuters_code)
    add_bounded_paging(related)
    related.set_defaults(func=fetch_etf_related)

    poll = sub.add_parser("poll", help="Public current price polling for foreign securities")
    poll.add_argument("security_type", choices=POLL_TYPES)
    poll.add_argument(
        "--code",
        required=True,
        action="append",
        type=reuters_code,
        help="Reuters code; repeat for up to 20 codes",
    )
    add_output(poll)
    poll.set_defaults(func=fetch_poll)

    exchange = sub.add_parser("exchange-time", help="US exchange operating-time metadata")
    exchange.add_argument("--exchange", choices=EXCHANGES, default="NASDAQ")
    add_output(exchange)
    exchange.set_defaults(func=fetch_exchange_time)

    for name, help_text, func in [
        ("stock-world-news", "Foreign stock global/Reuters news", fetch_stock_world_news),
        ("stock-local-news", "Korean local news for a foreign stock", fetch_stock_local_news),
    ]:
        command = sub.add_parser(name, help=help_text)
        command.add_argument("--code", required=True, type=reuters_code)
        add_bounded_paging(command, page_based=True)
        command.set_defaults(func=func)

    args = parser.parse_args()
    if args.command == "poll" and len(args.code) > 20:
        parser.error("poll accepts at most 20 --code values")
    emit_output(render_json(args.func(args)), args.output)


if __name__ == "__main__":
    main()
