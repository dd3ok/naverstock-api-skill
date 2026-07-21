#!/usr/bin/env python3
"""Fetch Naver Stock domestic market list and ranking payloads."""

from __future__ import annotations

import argparse
from typing import Any

from naverstock_api import build_path, emit_output, render_json, request_json


MARKET_TYPES = ("ALL", "KOSPI", "KOSDAQ", "KONEX")
ALERT_TYPES = ("01", "02", "03")
NXT_ORDER_TYPES = frozenset({"down", "marketSum", "quantTop", "searchTop", "up"})

# User-facing names follow the current stock-list chips. Dividend and popular
# search keep their dedicated commands to avoid duplicate meanings. Keep the
# raw ``default`` command for backwards compatibility and API investigation.
RANKING_TYPES = {
    "52-week-high": ("high52week", None),
    "52-week-low": ("low52week", None),
    "fall": ("down", None),
    "flat": ("flat", None),
    "foreign-hold": ("frgnRate", None),
    "investment-caution": ("marketAlertType", "01"),
    "investment-risk": ("marketAlertType", "03"),
    "investment-warning": ("marketAlertType", "02"),
    "management": ("statusTag", None),
    "market-cap": ("marketSum", None),
    "new-stock": ("newStock", None),
    "rise": ("up", None),
    "trading-halt": ("tradeStopYn", None),
    "trading-value": ("priceTop", None),
    "volume": ("quantTop", None),
    "volume-drop": ("lowerQuantTop", None),
    "volume-surge": ("upperQuantTop", None),
}

RAW_ORDER_TYPES = tuple(
    sorted(
        {
            "accAmount",
            "searchTop",
            "steady",
            *(order_type for order_type, _ in RANKING_TYPES.values()),
        }
    )
)


class MarketStockArgumentError(ValueError):
    """Raised for an invalid market-list filter combination."""


def _validate_default_filters(
    *, trade_type: str, market_type: str, order_type: str, alert_type: str | None
) -> None:
    if market_type == "KONEX" and trade_type != "KRX":
        raise MarketStockArgumentError("KONEX is available only with --trade-type KRX")
    if market_type == "KONEX" and order_type != "quantTop":
        raise MarketStockArgumentError(
            "The current KONEX page supports only the volume ranking (orderType quantTop)"
        )
    if trade_type == "NXT" and order_type not in NXT_ORDER_TYPES:
        raise MarketStockArgumentError(
            "The current NXT page supports only market-cap, rise, fall, volume, "
            "and search-top rankings"
        )
    if order_type == "marketAlertType":
        if alert_type not in ALERT_TYPES:
            raise MarketStockArgumentError(
                "marketAlertType requires --alert-type 01, 02, or 03"
            )
    elif alert_type is not None:
        raise MarketStockArgumentError(
            "--alert-type is valid only with --order-type marketAlertType"
        )


def _fetch_default_list(
    *,
    trade_type: str,
    market_type: str,
    order_type: str,
    start_idx: int,
    page_size: int,
    alert_type: str | None = None,
) -> Any:
    _validate_default_filters(
        trade_type=trade_type,
        market_type=market_type,
        order_type=order_type,
        alert_type=alert_type,
    )
    return request_json(
        build_path(
            "/api/domestic/market/stock/default",
            {
                "tradeType": trade_type,
                "marketType": market_type,
                "orderType": order_type,
                "startIdx": start_idx,
                "pageSize": page_size,
                "alertType": alert_type,
            },
        )
    )


def fetch_default(args: argparse.Namespace) -> Any:
    return _fetch_default_list(
        trade_type=args.trade_type,
        market_type=args.market_type,
        order_type=args.order_type,
        start_idx=args.start_idx,
        page_size=args.page_size,
        alert_type=args.alert_type,
    )


def fetch_ranking(args: argparse.Namespace) -> Any:
    order_type, alert_type = RANKING_TYPES[args.kind]
    return _fetch_default_list(
        trade_type=args.trade_type,
        market_type=args.market_type,
        order_type=order_type,
        start_idx=args.start_idx,
        page_size=args.page_size,
        alert_type=alert_type,
    )


def fetch_dividend(args: argparse.Namespace) -> Any:
    return request_json(
        build_path(
            "/api/domestic/market/stock/dividend",
            {
                "tradeType": args.trade_type,
                "marketType": args.market_type,
                "dividend": args.dividend,
                "startIdx": args.start_idx,
                "pageSize": args.page_size,
            },
        )
    )


def fetch_search_top(args: argparse.Namespace) -> Any:
    return request_json(
        build_path(
            "/api/domestic/market/searchTop",
            {"nationType": args.nation_type, "startIdx": args.start_idx, "pageSize": args.page_size},
        )
    )


def fetch_ipo(args: argparse.Namespace) -> Any:
    return request_json(
        build_path(
            "/api/domestic/market/ipo/progress",
            {"IpoProgressType": args.ipo_progress_type, "startIdx": args.start_idx, "pageSize": args.page_size},
        )
    )


def fetch_upjong_theme(args: argparse.Namespace) -> Any:
    return request_json(
        build_path(
            "/api/domestic/home/upjongTheme/ranking",
            {"sortType": args.sort_type},
        )
    )


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    sub = parser.add_subparsers(dest="command", required=True)

    ranking = sub.add_parser("ranking", help="Domestic stock ranking with stable semantic names")
    ranking.add_argument("kind", choices=sorted(RANKING_TYPES))
    ranking.add_argument("--trade-type", choices=["KRX", "NXT"], default="KRX")
    ranking.add_argument("--market-type", choices=MARKET_TYPES, default="ALL")
    ranking.add_argument("--start-idx", type=int, default=0)
    ranking.add_argument("--page-size", type=int, default=20)
    ranking.add_argument("--output")
    ranking.set_defaults(func=fetch_ranking)

    default = sub.add_parser("default", help="Low-level domestic stock list (compatibility/debugging)")
    default.add_argument("--trade-type", choices=["KRX", "NXT"], default="KRX")
    default.add_argument("--market-type", choices=MARKET_TYPES, default="ALL")
    default.add_argument("--order-type", choices=RAW_ORDER_TYPES, default="marketSum")
    default.add_argument("--start-idx", type=int, default=0)
    default.add_argument("--page-size", type=int, default=20)
    default.add_argument("--alert-type", choices=ALERT_TYPES)
    default.add_argument("--output")
    default.set_defaults(func=fetch_default)

    dividend = sub.add_parser("dividend", help="High-dividend stock list")
    dividend.add_argument("--trade-type", choices=["KRX", "NXT"], default="KRX")
    dividend.add_argument("--market-type", choices=["ALL", "KOSPI", "KOSDAQ"], default="ALL")
    dividend.add_argument("--dividend", default="dividendRate")
    dividend.add_argument("--start-idx", type=int, default=0)
    dividend.add_argument("--page-size", type=int, default=20)
    dividend.add_argument("--output")
    dividend.set_defaults(func=fetch_dividend)

    search = sub.add_parser("search-top", help="Popular search ranking")
    search.add_argument("--nation-type", choices=["KOR", "USA"], default="KOR")
    search.add_argument("--start-idx", type=int, default=0)
    search.add_argument("--page-size", type=int, default=20)
    search.add_argument("--output")
    search.set_defaults(func=fetch_search_top)

    ipo = sub.add_parser("ipo", help="IPO progress list")
    ipo.add_argument("--ipo-progress-type", help="Observed value: LISTING")
    ipo.add_argument("--start-idx", type=int, default=0)
    ipo.add_argument("--page-size", type=int, default=20)
    ipo.add_argument("--output")
    ipo.set_defaults(func=fetch_ipo)

    upjong = sub.add_parser("upjong-theme", help="Sector/theme ranking")
    upjong.add_argument("--sort-type", default="changeRate")
    upjong.add_argument("--output")
    upjong.set_defaults(func=fetch_upjong_theme)

    args = parser.parse_args()
    try:
        payload = args.func(args)
    except MarketStockArgumentError as exc:
        parser.error(str(exc))
    emit_output(render_json(payload), args.output)


if __name__ == "__main__":
    main()
