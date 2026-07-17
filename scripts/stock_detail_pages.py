#!/usr/bin/env python3
"""Fetch stock-detail subpage payloads such as news, disclosures, IR, and investor stats."""

from __future__ import annotations

import argparse
from typing import Any

from naverstock_api import build_path, emit_output, normalize_item_code, render_json, request_json


INVEST_RESOURCES = {
    "trade": "stock-trade",
    "investor-rank": "stock-investor-rank",
    "invest-rate": "stock-invest-rate",
    "investor-age": "stock-investor-age",
    "floor": "stock-floor",
}

ETF_DETAIL_TYPES = {
    "base": "ETFBase",
    "dividend": "ETFDividend",
    "dividend-hist": "ETFDividendHist",
    "component": "ETFComponent",
    "theme": "ETFTheme",
    "flow-day": "ETFSumFlowDayList",
    "flow-week": "ETFSumFlowWeekList",
}


def _numeric_article_id(value: str) -> str:
    clean = value.strip()
    if not clean.isascii() or not clean.isdigit() or not 1 <= len(clean) <= 30:
        raise argparse.ArgumentTypeError("article-id must contain 1-30 digits")
    return clean


def fetch_price(args: argparse.Namespace) -> Any:
    return request_json(f"/api/domestic/detail/{normalize_item_code(args.code)}/price")


def fetch_hoga(args: argparse.Namespace) -> Any:
    return request_json(f"/api/domestic/detail/{normalize_item_code(args.code)}/hoga")


def fetch_sise_day(args: argparse.Namespace) -> Any:
    return request_json(
        build_path(
            f"/api/domestic/detail/{normalize_item_code(args.code)}/siseDay",
            {"pageSize": args.page_size, "bizdate": args.bizdate},
        )
    )


def fetch_sise_tick(args: argparse.Namespace) -> Any:
    return request_json(
        build_path(
            f"/api/domestic/detail/{normalize_item_code(args.code)}/siseTick",
            {"startIdx": args.start_idx, "pageSize": args.page_size},
        )
    )


def fetch_trend(args: argparse.Namespace) -> Any:
    return request_json(
        build_path(
            f"/api/domestic/detail/{normalize_item_code(args.code)}/trend",
            {"tradeType": args.trade_type, "startIdx": args.start_idx, "pageSize": args.page_size},
        )
    )


def fetch_trader_info(args: argparse.Namespace) -> Any:
    return request_json(f"/api/domestic/detail/{normalize_item_code(args.code)}/traderInfo")


def fetch_chart(args: argparse.Namespace) -> Any:
    return request_json(
        build_path(
            f"/api/securityFe/api/fchart/domestic/stock/{normalize_item_code(args.code)}",
            {"periodType": args.period_type, "range": args.range},
        )
    )


def fetch_chart_prices(args: argparse.Namespace) -> Any:
    return request_json(
        build_path(
            f"/api/securityService/chart/domestic/item/{normalize_item_code(args.code)}",
            {"periodType": args.period_type, "range": args.range},
        )
    )


def fetch_news(args: argparse.Namespace) -> Any:
    return request_json(
        build_path(
            "/api/domestic/detail/news",
            {"itemCode": normalize_item_code(args.code), "page": args.page, "pageSize": args.page_size},
        )
    )


def fetch_research(args: argparse.Namespace) -> Any:
    return request_json(
        build_path(f"/api/domestic/research/{normalize_item_code(args.code)}/research", {"page": args.page, "size": args.size})
    )


def fetch_notice(args: argparse.Namespace) -> Any:
    params: dict[str, Any] = {
        "itemCode": normalize_item_code(args.code),
        "startIdx": args.start_idx,
        "pageSize": args.page_size,
    }
    if args.cause_code:
        params["causeCode"] = args.cause_code
    return request_json(build_path("/api/domestic/detail/notice", params))


def fetch_ir(args: argparse.Namespace) -> Any:
    return request_json(
        build_path(
            "/api/domestic/detail/ir",
            {"itemCode": normalize_item_code(args.code), "startIdx": args.start_idx, "pageSize": args.page_size},
        )
    )


def fetch_ir_detail(args: argparse.Namespace) -> Any:
    return request_json(f"/api/domestic/detail/ir/{normalize_item_code(args.code)}/{args.article_id}")


def fetch_invest_poll(args: argparse.Namespace) -> Any:
    return request_json(f"/api/stockDomestic/invest-info/poll/statistics/{normalize_item_code(args.code)}")


def fetch_invest_resource(args: argparse.Namespace) -> Any:
    params = {
        "item_code": normalize_item_code(args.code),
        "stock_exchange_type": args.stock_exchange_type,
        "statDate": args.stat_date,
        "size": args.size,
        "groupBy": args.group_by,
        "sortBy": args.sort_by,
    }
    return request_json(build_path(f"/api/myasset/resources/invest/{INVEST_RESOURCES[args.resource]}", params))


def fetch_finance_menu(args: argparse.Namespace) -> Any:
    return request_json(f"/api/stockSecurity/finances/v1/domestic/{normalize_item_code(args.code)}/menu-info")


def fetch_finance_esg(args: argparse.Namespace) -> Any:
    return request_json(f"/api/stockSecurity/finances/v1/domestic/{normalize_item_code(args.code)}/esg")


def fetch_etf_detail(args: argparse.Namespace) -> Any:
    code = normalize_item_code(args.code)
    endpoint = ETF_DETAIL_TYPES[args.detail_type]
    params: dict[str, Any] = {}
    if args.detail_type in {"dividend-hist", "component"}:
        params = {"startIdx": args.start_idx, "pageSize": args.page_size}
    elif args.detail_type in {"flow-day", "flow-week"}:
        params = {"count": args.count}
    return request_json(build_path(f"/api/domestic/detail/{code}/{endpoint}", params))


def add_code(parser: argparse.ArgumentParser) -> None:
    parser.add_argument("--code", required=True, help="Six-digit domestic stock code, with or without leading A")


def add_page(parser: argparse.ArgumentParser) -> None:
    parser.add_argument("--page-size", type=int, default=20)
    parser.add_argument("--output")


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    sub = parser.add_subparsers(dest="command", required=True)

    for name, help_text, func in [
        ("price", "Current price payload for the stock price tab", fetch_price),
        ("hoga", "Order book / 호가 payload", fetch_hoga),
        ("trader-info", "Broker trader information", fetch_trader_info),
    ]:
        cmd = sub.add_parser(name, help=help_text)
        add_code(cmd)
        cmd.add_argument("--output")
        cmd.set_defaults(func=func)

    day = sub.add_parser("sise-day", help="Daily price rows")
    add_code(day)
    day.add_argument("--page-size", type=int, default=20)
    day.add_argument("--bizdate")
    day.add_argument("--output")
    day.set_defaults(func=fetch_sise_day)

    tick = sub.add_parser("sise-tick", help="Intraday tick rows")
    add_code(tick)
    tick.add_argument("--start-idx", type=int, default=0)
    tick.add_argument("--page-size", type=int, default=20)
    tick.add_argument("--output")
    tick.set_defaults(func=fetch_sise_tick)

    trend = sub.add_parser("trend", help="Investor trading trend rows")
    add_code(trend)
    trend.add_argument("--trade-type", choices=["KRX", "NXT"], default="KRX")
    trend.add_argument("--start-idx", type=int, default=0)
    trend.add_argument("--page-size", type=int, default=20)
    trend.add_argument("--output")
    trend.set_defaults(func=fetch_trend)

    chart = sub.add_parser("chart", help="Domestic stock fchart payload")
    add_code(chart)
    chart.add_argument("--period-type", default="day")
    chart.add_argument("--range")
    chart.add_argument("--output")
    chart.set_defaults(func=fetch_chart)

    chart_prices = sub.add_parser("chart-prices", help="Domestic stock chart price rows")
    add_code(chart_prices)
    chart_prices.add_argument("--period-type", default="day")
    chart_prices.add_argument("--range")
    chart_prices.add_argument("--output")
    chart_prices.set_defaults(func=fetch_chart_prices)

    news = sub.add_parser("news", help="Stock-specific news clusters")
    add_code(news)
    news.add_argument("--page", type=int, default=1)
    add_page(news)
    news.set_defaults(func=fetch_news)

    notice = sub.add_parser("notice", help="Stock disclosures / 공시")
    add_code(notice)
    notice.add_argument("--start-idx", type=int, default=0)
    notice.add_argument("--cause-code", action="append")
    add_page(notice)
    notice.set_defaults(func=fetch_notice)

    ir = sub.add_parser("ir", help="Stock IR list")
    add_code(ir)
    ir.add_argument("--start-idx", type=int, default=0)
    add_page(ir)
    ir.set_defaults(func=fetch_ir)

    ir_detail = sub.add_parser("ir-detail", help="Stock IR detail")
    add_code(ir_detail)
    ir_detail.add_argument("--article-id", type=_numeric_article_id, required=True)
    ir_detail.add_argument("--output")
    ir_detail.set_defaults(func=fetch_ir_detail)

    research = sub.add_parser("research", help="Stock-specific research reports")
    add_code(research)
    research.add_argument("--page", type=int, default=0)
    research.add_argument("--size", type=int, default=30)
    research.add_argument("--output")
    research.set_defaults(func=fetch_research)

    poll = sub.add_parser("invest-poll", help="Aggregate investor poll statistics for a stock")
    add_code(poll)
    poll.add_argument("--output")
    poll.set_defaults(func=fetch_invest_poll)

    resource = sub.add_parser("invest-resource", help="Aggregate investor distribution resources")
    add_code(resource)
    resource.add_argument("resource", choices=sorted(INVEST_RESOURCES))
    resource.add_argument("--stock-exchange-type")
    resource.add_argument("--stat-date")
    resource.add_argument("--size", type=int)
    resource.add_argument("--group-by")
    resource.add_argument("--sort-by")
    resource.add_argument("--output")
    resource.set_defaults(func=fetch_invest_resource)

    finance_menu = sub.add_parser("finance-menu", help="stockSecurity finance menu metadata")
    add_code(finance_menu)
    finance_menu.add_argument("--output")
    finance_menu.set_defaults(func=fetch_finance_menu)

    finance_esg = sub.add_parser("finance-esg", help="stockSecurity finance ESG payload")
    add_code(finance_esg)
    finance_esg.add_argument("--output")
    finance_esg.set_defaults(func=fetch_finance_esg)

    etf = sub.add_parser("etf-detail", help="ETF detail subpage data")
    add_code(etf)
    etf.add_argument("detail_type", choices=sorted(ETF_DETAIL_TYPES))
    etf.add_argument("--start-idx", type=int, default=0)
    etf.add_argument("--page-size", type=int, default=20)
    etf.add_argument("--count", type=int, default=20)
    etf.add_argument("--output")
    etf.set_defaults(func=fetch_etf_detail)

    args = parser.parse_args()
    emit_output(render_json(args.func(args)), args.output)


if __name__ == "__main__":
    main()
