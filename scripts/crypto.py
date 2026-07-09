#!/usr/bin/env python3
"""Fetch Naver Stock crypto ranking, polling, candle, news, and profile payloads."""

from __future__ import annotations

import argparse
from typing import Any

from naverstock_api import build_path, emit_output, render_json, request_json


def fetch_rank(args: argparse.Namespace) -> Any:
    return request_json(
        build_path(
            f"/api/coin/rank/{args.market}",
            {"sortType": args.sort_type, "page": args.page, "pageSize": args.page_size},
        )
    )


def fetch_majors(args: argparse.Namespace) -> Any:
    return request_json(f"/api/coin/rank/{args.market}/majors")


def fetch_price(args: argparse.Namespace) -> Any:
    if args.market:
        return request_json(f"/api/coin/price/{args.market}/{args.ticker}")
    return request_json(build_path(f"/api/coin/price/{args.ticker}", {"excludeExchange": args.exclude_exchange}))


def fetch_polling(args: argparse.Namespace) -> Any:
    return request_json(build_path("/api/polling/coin/price", {"fqnfTickers": args.fqnf_tickers}))


def fetch_candles(args: argparse.Namespace) -> Any:
    return request_json(
        build_path(
            f"/api/coin/candle/{args.market}/KRW/{args.ticker}/minutes/{args.unit}/marketInfo",
            {"from": args.from_time, "to": args.to_time},
        )
    )


def fetch_global_news(args: argparse.Namespace) -> Any:
    return request_json(
        build_path(
            f"/api/coin/globalNews/{args.ticker.upper()}",
            {"pageSize": args.page_size, "offsetTimestamp": args.offset_timestamp},
        )
    )


def fetch_market_updates(args: argparse.Namespace) -> Any:
    return request_json(
        build_path(
            f"/api/coin/marketUpdates/{args.ticker.upper()}",
            {"pageSize": args.page_size, "offsetTimestamp": args.offset_timestamp},
        )
    )


def fetch_profile(args: argparse.Namespace) -> Any:
    return request_json(f"/api/coin/profile/{args.ticker.upper()}")


def fetch_categories_ranking(args: argparse.Namespace) -> Any:
    return request_json(
        build_path(
            "/api/coin/categories/ranking",
            {"exchangeType": args.exchange_type, "page": args.page, "pageSize": args.page_size},
        )
    )


def fetch_prices(args: argparse.Namespace) -> Any:
    return request_json(build_path("/api/coin/prices", {"fqnfTickers": args.fqnf_tickers}))


def fetch_global_market_trend(args: argparse.Namespace) -> Any:
    return request_json("/api/coin/globalMarketTrend")


def fetch_coinmacro_news(args: argparse.Namespace) -> Any:
    return request_json("/api/securityFe/api/news/coinmacro")


def fetch_coin_briefing(args: argparse.Namespace) -> Any:
    return request_json(
        build_path(
            "/api/securityAi/coinBriefing/current",
            {"exchangeType": args.exchange_type, "nfTicker": args.ticker.upper()},
        )
    )


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    sub = parser.add_subparsers(dest="command", required=True)

    rank = sub.add_parser("rank", help="Crypto ranking list")
    rank.add_argument("--market", choices=["UPBIT", "BITHUMB"], default="UPBIT")
    rank.add_argument("--sort-type", default="marketValue")
    rank.add_argument("--page", type=int, default=1)
    rank.add_argument("--page-size", type=int, default=20)
    rank.add_argument("--output")
    rank.set_defaults(func=fetch_rank)

    majors = sub.add_parser("majors", help="Major crypto list")
    majors.add_argument("--market", choices=["UPBIT", "BITHUMB"], default="UPBIT")
    majors.add_argument("--output")
    majors.set_defaults(func=fetch_majors)

    price = sub.add_parser("price", help="Single or multi-exchange crypto price")
    price.add_argument("--ticker", default="BTC", help="Example: BTC")
    price.add_argument("--market", choices=["UPBIT", "BITHUMB"])
    price.add_argument("--exclude-exchange", choices=["UPBIT", "BITHUMB"])
    price.add_argument("--output")
    price.set_defaults(func=fetch_price)

    polling = sub.add_parser("polling", help="Crypto polling prices")
    polling.add_argument("--fqnf-tickers", required=True, help="Example: BTC_KRW_UPBIT")
    polling.add_argument("--output")
    polling.set_defaults(func=fetch_polling)

    candles = sub.add_parser("candles", help="Minute candles")
    candles.add_argument("--market", choices=["UPBIT", "BITHUMB"], default="UPBIT")
    candles.add_argument("--ticker", default="BTC", help="Example: BTC")
    candles.add_argument("--unit", type=int, default=1)
    candles.add_argument("--from-time", required=True, help="ISO-like time, e.g. 2026-04-27T09:00:00")
    candles.add_argument("--to-time", required=True, help="ISO-like time, e.g. 2026-04-27T09:40:00")
    candles.add_argument("--output")
    candles.set_defaults(func=fetch_candles)

    for name, help_text, func in [
        ("global-news", "Crypto global news", fetch_global_news),
        ("market-updates", "Crypto market update feed", fetch_market_updates),
    ]:
        cmd = sub.add_parser(name, help=help_text)
        cmd.add_argument("--ticker", default="BTC", help="Plain ticker, e.g. BTC")
        cmd.add_argument("--page-size", type=int, default=20)
        cmd.add_argument("--offset-timestamp")
        cmd.add_argument("--output")
        cmd.set_defaults(func=func)

    profile = sub.add_parser("profile", help="Crypto profile")
    profile.add_argument("--ticker", default="BTC", help="Plain ticker, e.g. BTC")
    profile.add_argument("--output")
    profile.set_defaults(func=fetch_profile)

    categories = sub.add_parser("categories-ranking", help="Crypto category ranking")
    categories.add_argument("--exchange-type", choices=["UPBIT", "BITHUMB"], default="UPBIT")
    categories.add_argument("--page", type=int, default=1)
    categories.add_argument("--page-size", type=int, default=20)
    categories.add_argument("--output")
    categories.set_defaults(func=fetch_categories_ranking)

    prices = sub.add_parser("prices", help="Crypto prices for repeated fqnfTickers")
    prices.add_argument("--fqnf-tickers", action="append", required=True, help="Repeat for each FQNF ticker")
    prices.add_argument("--output")
    prices.set_defaults(func=fetch_prices)

    trend = sub.add_parser("global-market-trend", help="Global crypto market trend")
    trend.add_argument("--output")
    trend.set_defaults(func=fetch_global_market_trend)

    coinmacro = sub.add_parser("coinmacro-news", help="Coin macro news")
    coinmacro.add_argument("--output")
    coinmacro.set_defaults(func=fetch_coinmacro_news)

    briefing = sub.add_parser("coin-briefing", help="Security AI coin briefing")
    briefing.add_argument("--exchange-type", choices=["UPBIT", "BITHUMB"], default="UPBIT")
    briefing.add_argument("--ticker", default="BTC", help="Plain ticker, e.g. BTC")
    briefing.add_argument("--output")
    briefing.set_defaults(func=fetch_coin_briefing)

    args = parser.parse_args()
    emit_output(render_json(args.func(args)), args.output)


if __name__ == "__main__":
    main()
