#!/usr/bin/env python3
"""Fetch Naver Stock market index, indicator, and exchange payloads."""

from __future__ import annotations

import argparse
import datetime as dt
import re
from typing import Any, Callable

from naverstock_api import bounded_int, build_path, emit_output, render_json, request_json


_MARKET_CODE = re.compile(r"^(?:\.?[A-Za-z0-9][A-Za-z0-9._=-]{0,31})$")
_SHORT_TOKEN = re.compile(r"^[A-Za-z0-9_-]{1,32}$")
_QUERY_TOKEN = re.compile(r"^[A-Za-z0-9._~,:+=/-]{1,128}$")
_CURRENCY = re.compile(r"^[A-Z]{3}$")
_NATION_TYPES = ["KOR", "USA", "CHN", "JPN", "EUR"]


def _bounded_integer(name: str, minimum: int, maximum: int) -> Callable[[str], int]:
    def parse(value: str) -> int:
        try:
            return bounded_int(value, name=name, minimum=minimum, maximum=maximum)
        except ValueError as exc:
            raise argparse.ArgumentTypeError(str(exc)) from exc

    return parse


def _market_code(value: str) -> str:
    clean = value.strip()
    if not _MARKET_CODE.fullmatch(clean):
        raise argparse.ArgumentTypeError("market code contains an unsupported character or path separator")
    return clean


def _market_codes(value: str) -> str:
    codes = value.split(",")
    if not 1 <= len(codes) <= 30 or any(not _MARKET_CODE.fullmatch(code) for code in codes):
        raise argparse.ArgumentTypeError("codes must contain 1-30 comma-separated market codes")
    return ",".join(codes)


def _short_token(value: str) -> str:
    clean = value.strip()
    if not _SHORT_TOKEN.fullmatch(clean):
        raise argparse.ArgumentTypeError("value must be a short alphanumeric token")
    return clean


def _query_token(value: str) -> str:
    clean = value.strip()
    if not _QUERY_TOKEN.fullmatch(clean):
        raise argparse.ArgumentTypeError("value must be a bounded URL-safe query token")
    return clean


def _currency(value: str) -> str:
    clean = value.strip().upper()
    if not _CURRENCY.fullmatch(clean):
        raise argparse.ArgumentTypeError("currency must be a three-letter code")
    return clean


def _currencies(value: str) -> str:
    codes = value.split(",")
    if not 1 <= len(codes) <= 20:
        raise argparse.ArgumentTypeError("currencies must contain 1-20 comma-separated codes")
    return ",".join(_currency(code) for code in codes)


def _iso_date(value: str) -> str:
    try:
        return dt.date.fromisoformat(value).strftime("%Y%m%d")
    except (TypeError, ValueError) as exc:
        raise argparse.ArgumentTypeError("release-date must be a valid YYYY-MM-DD date") from exc


def fetch_majors(args: argparse.Namespace) -> Any:
    return request_json("/api/securityFe/api/index/majors")


def fetch_major_block(args: argparse.Namespace) -> Any:
    return request_json(f"/api/securityService/marketindex/majors/{args.block_type}")


def fetch_polling(args: argparse.Namespace) -> Any:
    return request_json(build_path("/api/polling/domestic/index", {"itemCodes": args.codes}))


def fetch_chart(args: argparse.Namespace) -> Any:
    return request_json(
        build_path(
            f"/api/securityService/chart/domestic/index/{args.code}",
            {"periodType": args.period_type, "range": args.range},
        )
    )


def fetch_foreign_chart(args: argparse.Namespace) -> Any:
    return request_json(
        build_path(
            f"/api/securityService/chart/foreign/{args.asset_type}/{args.code}",
            {"periodType": args.period_type, "range": args.range},
        )
    )


def fetch_market_polling(args: argparse.Namespace) -> Any:
    return request_json(f"/api/polling/marketindex/{args.category}/{args.codes}")


def fetch_category(args: argparse.Namespace) -> Any:
    return request_json(f"/api/securityService/marketindex/{args.category}")


def fetch_detail(args: argparse.Namespace) -> Any:
    if args.category == "bond":
        return request_json(build_path(f"/api/securityService/marketindex/bond/nation/{args.code}", {"sortType": args.sort_type}))
    return request_json(f"/api/securityService/marketindex/{args.category}/{args.code}")


def fetch_prices(args: argparse.Namespace) -> Any:
    return request_json(
        build_path(
            f"/api/securityService/marketindex/{args.category}/{args.code}/prices",
            {"page": args.page, "pageSize": args.page_size},
        )
    )


def fetch_economic_upcoming(args: argparse.Namespace) -> Any:
    return request_json(
        build_path(
            "/api/securityService/economic/indicator/nations/upcoming",
            {"limit": args.limit, "nationTypeList": args.nation_type},
        )
    )


def fetch_economic_release(args: argparse.Namespace) -> Any:
    return request_json(
        build_path(
            "/api/securityService/economic/indicator/nations/releaseDate",
            {"page": args.page, "pageSize": args.page_size, "releaseDate": args.release_date, "nationTypeList": args.nation_type},
        )
    )


def fetch_exchange_rates(args: argparse.Namespace) -> Any:
    return request_json(build_path("/api/stockDomestic/exchangeRates/list", {"currencies": args.currencies}))


def fetch_exchange_list(args: argparse.Namespace) -> Any:
    return request_json("/api/domestic/exchange/List")


def fetch_exchange_prices(args: argparse.Namespace) -> Any:
    return request_json(
        build_path(
            f"/api/domestic/exchange/{args.currency}/list",
            {"startIdx": args.start_idx, "pageSize": args.page_size},
        )
    )


def fetch_standard_interest_calendars(args: argparse.Namespace) -> Any:
    return request_json(
        build_path(
            f"/api/securityService/marketindex/standardInterest/{args.nation_type}/calendars",
            {"page": args.page, "pageSize": args.page_size},
        )
    )


def fetch_krx_gold(args: argparse.Namespace) -> Any:
    return request_json("/api/stockDomestic/gold/sise/krx")


def fetch_bank_exchanges(args: argparse.Namespace) -> Any:
    return request_json(
        build_path(
            "/api/securityService/marketindex/exchange/banksExchanges",
            {"bankType": args.bank_type},
        )
    )


def fetch_bank_round_chart(args: argparse.Namespace) -> Any:
    return request_json(
        build_path(
            f"/api/stockSecurity/exchange-rates/v2/{args.currency}/charts/round",
            {"bankType": args.bank_type},
        )
    )


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    sub = parser.add_subparsers(dest="command", required=True)

    majors = sub.add_parser("majors", help="Major Korean indices")
    majors.add_argument("--output")
    majors.set_defaults(func=fetch_majors)

    major_block = sub.add_parser("major-block", help="Market-index major block by type")
    major_block.add_argument(
        "--block-type",
        choices=["exchange", "exchangeWorld", "domesticInterest", "bond", "rpc"],
        default="exchange",
    )
    major_block.add_argument("--output")
    major_block.set_defaults(func=fetch_major_block)

    polling = sub.add_parser("polling", help="Domestic index polling")
    polling.add_argument("--codes", type=_market_codes, default="KOSPI,KOSDAQ,KPI200")
    polling.add_argument("--output")
    polling.set_defaults(func=fetch_polling)

    chart = sub.add_parser("chart", help="Index chart")
    chart.add_argument("--code", type=_market_code, default="KOSPI")
    chart.add_argument("--period-type", type=_short_token, default="day")
    chart.add_argument("--range", type=_query_token)
    chart.add_argument("--output")
    chart.set_defaults(func=fetch_chart)

    foreign_chart = sub.add_parser("foreign-chart", help="Foreign index or futures chart")
    foreign_chart.add_argument("--asset-type", choices=["index", "futures"], default="index")
    foreign_chart.add_argument("--code", type=_market_code, default=".DJI")
    foreign_chart.add_argument("--period-type", type=_short_token, default="day")
    foreign_chart.add_argument("--range", type=_query_token)
    foreign_chart.add_argument("--output")
    foreign_chart.set_defaults(func=fetch_foreign_chart)

    market_polling = sub.add_parser("market-polling", help="Market-indicator polling by category and codes")
    market_polling.add_argument("--category", choices=["energy", "metals", "exchange"], required=True)
    market_polling.add_argument(
        "--codes",
        type=_market_codes,
        required=True,
        help="Observed example: GCcv1 or CLcv1",
    )
    market_polling.add_argument("--output")
    market_polling.set_defaults(func=fetch_market_polling)

    category = sub.add_parser("category", help="Market indicator category")
    category.add_argument(
        "--category",
        choices=["energy", "metals", "agricultural", "transport", "domesticInterest", "exchange", "bond", "standardInterest"],
        required=True,
    )
    category.add_argument("--output")
    category.set_defaults(func=fetch_category)

    detail = sub.add_parser("detail", help="Market indicator detail")
    detail.add_argument(
        "--category",
        choices=[
            "energy",
            "metals",
            "agricultural",
            "transport",
            "domesticInterest",
            "exchange",
            "standardInterest",
            "bond",
        ],
        required=True,
    )
    detail.add_argument(
        "--code",
        type=_market_code,
        required=True,
        help="Reuters code or nation code for bond/standardInterest",
    )
    detail.add_argument("--sort-type", type=_short_token)
    detail.add_argument("--output")
    detail.set_defaults(func=fetch_detail)

    prices = sub.add_parser("prices", help="Market indicator price history")
    prices.add_argument(
        "--category",
        choices=["energy", "metals", "agricultural", "transport", "exchange"],
        required=True,
    )
    prices.add_argument("--code", type=_market_code, required=True)
    prices.add_argument("--page", type=_bounded_integer("page", 1, 10_000), default=1)
    prices.add_argument("--page-size", type=_bounded_integer("page-size", 1, 100), default=20)
    prices.add_argument("--output")
    prices.set_defaults(func=fetch_prices)

    calendars = sub.add_parser("standard-interest-calendars", help="Standard-interest calendar rows")
    calendars.add_argument("--nation-type", choices=_NATION_TYPES, required=True)
    calendars.add_argument("--page", type=_bounded_integer("page", 1, 10_000), default=1)
    calendars.add_argument("--page-size", type=_bounded_integer("page-size", 1, 100), default=20)
    calendars.add_argument("--output")
    calendars.set_defaults(func=fetch_standard_interest_calendars)

    upcoming = sub.add_parser("economic-upcoming", help="Upcoming economic indicators")
    upcoming.add_argument("--limit", type=_bounded_integer("limit", 1, 100))
    upcoming.add_argument("--nation-type", choices=_NATION_TYPES, action="append")
    upcoming.add_argument("--output")
    upcoming.set_defaults(func=fetch_economic_upcoming)

    release = sub.add_parser("economic-release", help="Economic indicators by release date")
    release.add_argument("--page", type=_bounded_integer("page", 1, 10_000), default=1)
    release.add_argument("--page-size", type=_bounded_integer("page-size", 1, 100), default=20)
    release.add_argument("--release-date", type=_iso_date)
    release.add_argument("--nation-type", choices=_NATION_TYPES, action="append")
    release.add_argument("--output")
    release.set_defaults(func=fetch_economic_release)

    rates = sub.add_parser("exchange-rates", help="Exchange-rate helper list")
    rates.add_argument("--currencies", type=_currencies, default="USD,JPY,EUR,CNY")
    rates.add_argument("--output")
    rates.set_defaults(func=fetch_exchange_rates)

    exchange_list = sub.add_parser("exchange-list", help="Available domestic exchange currencies")
    exchange_list.add_argument("--output")
    exchange_list.set_defaults(func=fetch_exchange_list)

    exchange_prices = sub.add_parser("exchange-prices", help="Domestic exchange price list by currency")
    exchange_prices.add_argument("--currency", type=_currency, default="USD")
    exchange_prices.add_argument("--start-idx", type=_bounded_integer("start-idx", 0, 100_000), default=0)
    exchange_prices.add_argument("--page-size", type=_bounded_integer("page-size", 1, 100), default=20)
    exchange_prices.add_argument("--output")
    exchange_prices.set_defaults(func=fetch_exchange_prices)

    gold = sub.add_parser("krx-gold", help="KRX domestic gold spot price")
    gold.add_argument("--output")
    gold.set_defaults(func=fetch_krx_gold)

    bank_exchanges = sub.add_parser("bank-exchanges", help="Bank exchange-rate summary")
    bank_exchanges.add_argument("--bank-type", type=_short_token, default="HNB", help="Observed value: HNB")
    bank_exchanges.add_argument("--output")
    bank_exchanges.set_defaults(func=fetch_bank_exchanges)

    bank_chart = sub.add_parser("bank-round-chart", help="Bank exchange-rate round chart")
    bank_chart.add_argument("--currency", type=_currency, default="USD")
    bank_chart.add_argument("--bank-type", type=_short_token, default="hana", help="Observed value: hana")
    bank_chart.add_argument("--output")
    bank_chart.set_defaults(func=fetch_bank_round_chart)

    args = parser.parse_args()
    if args.command in {"economic-upcoming", "economic-release"} and args.nation_type:
        if len(args.nation_type) > 10:
            parser.error(f"{args.command} accepts at most 10 --nation-type values")
    emit_output(render_json(args.func(args)), args.output)


if __name__ == "__main__":
    main()
