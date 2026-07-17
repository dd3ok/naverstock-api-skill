#!/usr/bin/env python3
"""Fetch Naver Stock crypto ranking, polling, candle, news, and profile payloads."""

from __future__ import annotations

import argparse
import datetime as dt
import re
from typing import Any, Callable

from naverstock_api import bounded_int, build_path, emit_output, render_json, request_json, validate_identifier


_TICKER = re.compile(r"^[A-Z0-9][A-Z0-9._-]{0,31}$")
_MARKET_CODE = re.compile(r"^\.?[A-Za-z0-9][A-Za-z0-9._=-]{0,31}$")
_FQNF_TICKER = re.compile(r"^[A-Z0-9.-]+_[A-Z]{3}_(?:UPBIT|BITHUMB)$")
_DATE_TIME = re.compile(r"^\d{14}$")
_OFFSET = re.compile(r"^[A-Za-z0-9._~+=:-]{1,128}$")


def _bounded_integer(name: str, minimum: int, maximum: int) -> Callable[[str], int]:
    def parse(value: str) -> int:
        try:
            return bounded_int(value, name=name, minimum=minimum, maximum=maximum)
        except ValueError as exc:
            raise argparse.ArgumentTypeError(str(exc)) from exc

    return parse


def _ticker(value: str) -> str:
    clean = value.strip().upper()
    if not _TICKER.fullmatch(clean):
        raise argparse.ArgumentTypeError("ticker contains an unsupported character or path separator")
    return clean


def _market_code(value: str) -> str:
    clean = value.strip()
    if not _MARKET_CODE.fullmatch(clean):
        raise argparse.ArgumentTypeError("market code contains an unsupported character or path separator")
    return clean


def _fqnf_tickers(value: str) -> str:
    tickers = value.split(",")
    if not 1 <= len(tickers) <= 50 or any(not _FQNF_TICKER.fullmatch(ticker) for ticker in tickers):
        raise argparse.ArgumentTypeError("fqnf-tickers must contain 1-50 valid exchange tickers")
    return ",".join(tickers)


def _iso_datetime(value: str) -> str:
    try:
        return dt.datetime.fromisoformat(value).isoformat()
    except (TypeError, ValueError) as exc:
        raise argparse.ArgumentTypeError("time must be a valid ISO date-time") from exc


def _compact_datetime(value: str) -> str:
    if not _DATE_TIME.fullmatch(value):
        raise argparse.ArgumentTypeError("date-time must use YYYYMMDDhhmmss")
    try:
        dt.datetime.strptime(value, "%Y%m%d%H%M%S")
    except ValueError as exc:
        raise argparse.ArgumentTypeError("date-time must be a valid YYYYMMDDhhmmss value") from exc
    return value


def _iso_date(value: str) -> str:
    try:
        return dt.date.fromisoformat(value).isoformat()
    except (TypeError, ValueError) as exc:
        raise argparse.ArgumentTypeError("date must use YYYY-MM-DD") from exc


def _offset(value: str) -> str:
    clean = value.strip()
    if not _OFFSET.fullmatch(clean):
        raise argparse.ArgumentTypeError("offset/page token must be a bounded URL-safe value")
    return clean


def _public_id(value: str) -> str:
    try:
        return validate_identifier(value, name="id")
    except ValueError as exc:
        raise argparse.ArgumentTypeError(str(exc)) from exc


def _validate_iso_range(parser: argparse.ArgumentParser, args: argparse.Namespace) -> None:
    start = dt.datetime.fromisoformat(args.from_time)
    end = dt.datetime.fromisoformat(args.to_time)
    if (start.tzinfo is None) != (end.tzinfo is None):
        parser.error("--from-time and --to-time must use the same timezone style")
    if start > end:
        parser.error("--from-time must be earlier than or equal to --to-time")


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


def fetch_daily_candles(args: argparse.Namespace) -> Any:
    return request_json(
        build_path(
            f"/api/coin/candle/{args.market}/KRW/{args.ticker}/days",
            {"from": args.from_time, "to": args.to_time},
        )
    )


def fetch_period_candles(args: argparse.Namespace) -> Any:
    return request_json(
        build_path(
            f"/api/coin/candle/{args.market}/KRW/{args.ticker}/{args.period}",
            {"from": args.from_time, "to": args.to_time},
        )
    )


def fetch_minute_candles(args: argparse.Namespace) -> Any:
    return request_json(
        build_path(
            f"/api/coin/candle/{args.market}/KRW/{args.ticker}/minutes/{args.unit}",
            {"from": args.from_time, "to": args.to_time},
        )
    )


def fetch_compare_chart(args: argparse.Namespace) -> Any:
    return request_json(
        build_path(
            f"/api/securityService/chart/compare/{args.nation}/{args.asset_type}/{args.code}/{args.period}",
            {"startDateTime": args.start_date_time, "endDateTime": args.end_date_time},
        )
    )


def fetch_foreign_interval_chart(args: argparse.Namespace) -> Any:
    return request_json(
        build_path(
            f"/api/securityService/chart/foreign/{args.asset_type}/{args.exchange}/{args.code}/interval/{args.interval}",
            {
                "startDateTime": args.start_date_time,
                "endDateTime": args.end_date_time,
                "utc": args.utc,
            },
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


def fetch_market_updates_overview(args: argparse.Namespace) -> Any:
    return request_json(
        build_path(
            "/api/coin/marketUpdates",
            {"pageSize": args.page_size, "offsetTimestamp": getattr(args, "offset_timestamp", None)},
        )
    )


def fetch_market_update_detail(args: argparse.Namespace) -> Any:
    return request_json(f"/api/coin/marketUpdates/detail/{args.content_id}")


def fetch_expert_contents(args: argparse.Namespace) -> Any:
    return request_json(
        build_path(
            "/api/coin/expertContents",
            {"pageSize": args.page_size, "offsetTimestamp": getattr(args, "offset_timestamp", None)},
        )
    )


def fetch_ticker_expert_contents(args: argparse.Namespace) -> Any:
    return request_json(
        build_path(
            f"/api/coin/{args.ticker}/expertContents",
            {"pageSize": args.page_size, "offsetTimestamp": args.offset_timestamp},
        )
    )


def fetch_expert_content_detail(args: argparse.Namespace) -> Any:
    return request_json(f"/api/coin/expertContents/{args.content_id}")


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
    return request_json(
        build_path(
            "/api/securityFe/api/news/coinmacro",
            {"page": args.page, "pageSize": args.page_size},
        )
    )


def fetch_category_detail(args: argparse.Namespace) -> Any:
    return request_json(
        build_path(
            f"/api/coin/categories/{args.category_id}",
            {"exchangeType": args.exchange_type},
        )
    )


def fetch_ticker_categories(args: argparse.Namespace) -> Any:
    return request_json(
        build_path(
            f"/api/coin/{args.ticker}/categories",
            {"exchangeType": args.exchange_type},
        )
    )


def fetch_etf_exposure(args: argparse.Namespace) -> Any:
    return request_json(
        build_path(
            f"/api/coin/etf/{args.ticker}",
            {
                "sortType": "holdingWeight",
                "size": args.size,
                "page": args.page,
                "pageToken": args.page_token,
            },
        )
    )


def fetch_coin_briefing(args: argparse.Namespace) -> Any:
    return request_json(
        build_path(
            "/api/securityAi/coinBriefing/current",
            {"exchangeType": args.exchange_type, "nfTicker": args.ticker.upper()},
        )
    )


def fetch_coin_briefing_history(args: argparse.Namespace) -> Any:
    return request_json(
        build_path(
            "/api/securityAi/coinBriefings",
            {
                "exchangeType": args.exchange_type,
                "nfTicker": args.ticker,
                "size": args.size,
                "date": args.date,
                "pageToken": args.page_token,
            },
        )
    )


def fetch_coin_briefing_detail(args: argparse.Namespace) -> Any:
    return request_json(f"/api/securityAi/coinBriefing/{args.briefing_id}")


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    sub = parser.add_subparsers(dest="command", required=True)

    rank = sub.add_parser("rank", help="Crypto ranking list")
    rank.add_argument("--market", choices=["UPBIT", "BITHUMB"], default="UPBIT")
    rank.add_argument("--sort-type", choices=["top", "marketValue"], default="marketValue")
    rank.add_argument("--page", type=_bounded_integer("page", 1, 1_000), default=1)
    rank.add_argument("--page-size", type=_bounded_integer("page-size", 1, 100), default=20)
    rank.add_argument("--output")
    rank.set_defaults(func=fetch_rank)

    majors = sub.add_parser("majors", help="Major crypto list")
    majors.add_argument("--market", choices=["UPBIT", "BITHUMB"], default="UPBIT")
    majors.add_argument("--output")
    majors.set_defaults(func=fetch_majors)

    price = sub.add_parser("price", help="Single or multi-exchange crypto price")
    price.add_argument("--ticker", type=_ticker, default="BTC", help="Example: BTC")
    price.add_argument("--market", choices=["UPBIT", "BITHUMB"])
    price.add_argument("--exclude-exchange", choices=["UPBIT", "BITHUMB"])
    price.add_argument("--output")
    price.set_defaults(func=fetch_price)

    polling = sub.add_parser("polling", help="Crypto polling prices")
    polling.add_argument("--fqnf-tickers", type=_fqnf_tickers, required=True, help="Example: BTC_KRW_UPBIT")
    polling.add_argument("--output")
    polling.set_defaults(func=fetch_polling)

    candles = sub.add_parser("candles", help="Minute candles")
    candles.add_argument("--market", choices=["UPBIT", "BITHUMB"], default="UPBIT")
    candles.add_argument("--ticker", type=_ticker, default="BTC", help="Example: BTC")
    candles.add_argument("--unit", type=int, choices=[1, 3, 5, 10, 15, 30, 60, 240], default=1)
    candles.add_argument("--from-time", type=_iso_datetime, required=True, help="ISO-like time")
    candles.add_argument("--to-time", type=_iso_datetime, required=True, help="ISO-like time")
    candles.add_argument("--output")
    candles.set_defaults(func=fetch_candles)

    daily_candles = sub.add_parser("daily-candles", help="Daily candles used by the crypto market comparison")
    daily_candles.add_argument("--market", choices=["UPBIT", "BITHUMB"], default="UPBIT")
    daily_candles.add_argument("--ticker", type=_ticker, default="BTC", help="Example: BTC")
    daily_candles.add_argument("--from-time", type=_iso_datetime, required=True, help="ISO-like time")
    daily_candles.add_argument("--to-time", type=_iso_datetime, required=True, help="ISO-like time")
    daily_candles.add_argument("--output")
    daily_candles.set_defaults(func=fetch_daily_candles)

    period_candles = sub.add_parser("period-candles", help="Year, week, quarter, month, or day candles")
    period_candles.add_argument("--market", choices=["UPBIT", "BITHUMB"], default="UPBIT")
    period_candles.add_argument("--ticker", type=_ticker, default="BTC")
    period_candles.add_argument("--period", choices=["year", "weeks", "quarter", "months", "days"], required=True)
    period_candles.add_argument("--from-time", type=_iso_datetime, required=True)
    period_candles.add_argument("--to-time", type=_iso_datetime, required=True)
    period_candles.add_argument("--output")
    period_candles.set_defaults(func=fetch_period_candles)

    minute_candles = sub.add_parser("minute-candles", help="Detail-page minute candles")
    minute_candles.add_argument("--market", choices=["UPBIT", "BITHUMB"], default="UPBIT")
    minute_candles.add_argument("--ticker", type=_ticker, default="BTC")
    minute_candles.add_argument("--unit", type=int, choices=[1, 3, 5, 10, 15, 30, 60, 240], default=1)
    minute_candles.add_argument("--from-time", type=_iso_datetime, required=True)
    minute_candles.add_argument("--to-time", type=_iso_datetime, required=True)
    minute_candles.add_argument("--output")
    minute_candles.set_defaults(func=fetch_minute_candles)

    compare = sub.add_parser("compare-chart", help="Domestic or foreign benchmark comparison chart")
    compare.add_argument("--nation", choices=["domestic", "foreign"], required=True)
    compare.add_argument("--asset-type", choices=["index", "futures"], default="index")
    compare.add_argument("--code", type=_market_code, required=True, help="Example: KOSPI, .INX, or GCcv1")
    compare.add_argument("--period", choices=["day", "week"], default="day")
    compare.add_argument("--start-date-time", type=_compact_datetime, required=True)
    compare.add_argument("--end-date-time", type=_compact_datetime, required=True)
    compare.add_argument("--output")
    compare.set_defaults(func=fetch_compare_chart)

    interval = sub.add_parser("foreign-interval-chart", help="Foreign benchmark intraday comparison chart")
    interval.add_argument("--asset-type", choices=["INDEX", "FUTURES"], required=True)
    interval.add_argument(
        "--exchange",
        choices=["NASDAQ", "NYSE", "COMEX", "ICE_US"],
        required=True,
        help="Exchange segment used by the public chart endpoint",
    )
    interval.add_argument("--code", type=_market_code, required=True)
    interval.add_argument("--interval", type=int, choices=[1, 5], default=5)
    interval.add_argument("--start-date-time", type=_compact_datetime, required=True)
    interval.add_argument("--end-date-time", type=_compact_datetime, required=True)
    interval.add_argument("--utc", action=argparse.BooleanOptionalAction, default=True)
    interval.add_argument("--output")
    interval.set_defaults(func=fetch_foreign_interval_chart)

    for name, help_text, func in [
        ("global-news", "Crypto global news", fetch_global_news),
        ("market-updates", "Crypto market update feed", fetch_market_updates),
    ]:
        cmd = sub.add_parser(name, help=help_text)
        cmd.add_argument("--ticker", type=_ticker, default="BTC", help="Plain ticker, e.g. BTC")
        cmd.add_argument("--page-size", type=_bounded_integer("page-size", 1, 100), default=20)
        cmd.add_argument("--offset-timestamp", type=_offset)
        cmd.add_argument("--output")
        cmd.set_defaults(func=func)

    profile = sub.add_parser("profile", help="Crypto profile")
    profile.add_argument("--ticker", type=_ticker, default="BTC", help="Plain ticker, e.g. BTC")
    profile.add_argument("--output")
    profile.set_defaults(func=fetch_profile)

    overview = sub.add_parser("market-updates-overview", help="Crypto-wide market update feed")
    overview.add_argument("--page-size", type=_bounded_integer("page-size", 1, 100), default=9)
    overview.add_argument("--offset-timestamp", type=_offset)
    overview.add_argument("--output")
    overview.set_defaults(func=fetch_market_updates_overview)

    update_detail = sub.add_parser("market-update-detail", help="Crypto market update detail")
    update_detail.add_argument("--content-id", type=_public_id, required=True)
    update_detail.add_argument("--output")
    update_detail.set_defaults(func=fetch_market_update_detail)

    expert = sub.add_parser("expert-contents", help="Public crypto expert content feed")
    expert.add_argument("--page-size", type=_bounded_integer("page-size", 1, 100), default=10)
    expert.add_argument("--offset-timestamp", type=_offset)
    expert.add_argument("--output")
    expert.set_defaults(func=fetch_expert_contents)

    ticker_expert = sub.add_parser("ticker-expert-contents", help="Expert content for one ticker")
    ticker_expert.add_argument("--ticker", type=_ticker, required=True)
    ticker_expert.add_argument("--page-size", type=_bounded_integer("page-size", 1, 100), default=10)
    ticker_expert.add_argument("--offset-timestamp", type=_offset)
    ticker_expert.add_argument("--output")
    ticker_expert.set_defaults(func=fetch_ticker_expert_contents)

    expert_detail = sub.add_parser("expert-content-detail", help="Crypto expert content detail")
    expert_detail.add_argument("--content-id", type=_public_id, required=True)
    expert_detail.add_argument("--output")
    expert_detail.set_defaults(func=fetch_expert_content_detail)

    categories = sub.add_parser("categories-ranking", help="Crypto category ranking")
    categories.add_argument("--exchange-type", choices=["UPBIT", "BITHUMB"], default="UPBIT")
    categories.add_argument("--page", type=_bounded_integer("page", 1, 1_000), default=1)
    categories.add_argument("--page-size", type=_bounded_integer("page-size", 1, 100), default=20)
    categories.add_argument("--output")
    categories.set_defaults(func=fetch_categories_ranking)

    category_detail = sub.add_parser("category-detail", help="Crypto sector/category detail")
    category_detail.add_argument("--category-id", type=_public_id, required=True)
    category_detail.add_argument("--exchange-type", choices=["UPBIT", "BITHUMB"], default="UPBIT")
    category_detail.add_argument("--output")
    category_detail.set_defaults(func=fetch_category_detail)

    ticker_categories = sub.add_parser("ticker-categories", help="Categories containing one ticker")
    ticker_categories.add_argument("--ticker", type=_ticker, required=True)
    ticker_categories.add_argument("--exchange-type", choices=["UPBIT", "BITHUMB"], default="UPBIT")
    ticker_categories.add_argument("--output")
    ticker_categories.set_defaults(func=fetch_ticker_categories)

    exposure = sub.add_parser("etf-exposure", help="ETF exposure to one crypto ticker")
    exposure.add_argument("--ticker", type=_ticker, required=True)
    exposure.add_argument("--size", type=_bounded_integer("size", 1, 100), default=20)
    exposure.add_argument("--page", type=_bounded_integer("page", 1, 1_000))
    exposure.add_argument("--page-token", type=_offset)
    exposure.add_argument("--output")
    exposure.set_defaults(func=fetch_etf_exposure)

    prices = sub.add_parser("prices", help="Crypto prices for repeated fqnfTickers")
    prices.add_argument(
        "--fqnf-tickers",
        action="append",
        type=_fqnf_tickers,
        required=True,
        help="Repeat for each FQNF ticker",
    )
    prices.add_argument("--output")
    prices.set_defaults(func=fetch_prices)

    trend = sub.add_parser("global-market-trend", help="Global crypto market trend")
    trend.add_argument("--output")
    trend.set_defaults(func=fetch_global_market_trend)

    coinmacro = sub.add_parser("coinmacro-news", help="Coin macro news")
    coinmacro.add_argument("--page", type=_bounded_integer("page", 1, 1_000), default=1)
    coinmacro.add_argument("--page-size", type=_bounded_integer("page-size", 1, 100), default=10)
    coinmacro.add_argument("--output")
    coinmacro.set_defaults(func=fetch_coinmacro_news)

    briefing = sub.add_parser("coin-briefing", help="Security AI coin briefing")
    briefing.add_argument("--exchange-type", choices=["UPBIT", "BITHUMB"], default="UPBIT")
    briefing.add_argument("--ticker", type=_ticker, default="BTC", help="Plain ticker, e.g. BTC")
    briefing.add_argument("--output")
    briefing.set_defaults(func=fetch_coin_briefing)

    briefing_history = sub.add_parser("coin-briefing-history", help="Historical AI coin briefings")
    briefing_history.add_argument("--exchange-type", choices=["UPBIT", "BITHUMB"], default="UPBIT")
    briefing_history.add_argument("--ticker", type=_ticker, default="BTC")
    briefing_history.add_argument("--size", type=_bounded_integer("size", 1, 100), default=20)
    briefing_history.add_argument("--date", type=_iso_date)
    briefing_history.add_argument("--page-token", type=_offset)
    briefing_history.add_argument("--output")
    briefing_history.set_defaults(func=fetch_coin_briefing_history)

    briefing_detail = sub.add_parser("coin-briefing-detail", help="AI coin briefing detail")
    briefing_detail.add_argument("--briefing-id", type=_public_id, required=True)
    briefing_detail.add_argument("--output")
    briefing_detail.set_defaults(func=fetch_coin_briefing_detail)

    args = parser.parse_args()
    if args.command == "prices" and len(args.fqnf_tickers) > 50:
        parser.error("prices accepts at most 50 --fqnf-tickers values")
    if args.command == "price" and args.market and args.exclude_exchange:
        parser.error("price accepts either --market or --exclude-exchange, not both")
    if args.command == "etf-exposure" and args.page is not None and args.page_token is not None:
        parser.error("etf-exposure accepts either --page or --page-token, not both")
    if (
        args.command == "compare-chart"
        and args.nation == "domestic"
        and args.asset_type != "index"
    ):
        parser.error("domestic compare-chart supports only --asset-type index")
    if args.command in {"compare-chart", "foreign-interval-chart"}:
        if args.start_date_time > args.end_date_time:
            parser.error("--start-date-time must be earlier than or equal to --end-date-time")
    if args.command in {"candles", "daily-candles", "period-candles", "minute-candles"}:
        _validate_iso_range(parser, args)
    emit_output(render_json(args.func(args)), args.output)


if __name__ == "__main__":
    main()
