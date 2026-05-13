#!/usr/bin/env python3
"""Fetch Naver Stock market index and indicator payloads."""

from __future__ import annotations

import argparse
from typing import Any

from naverstock_api import build_path, emit_output, render_json, request_json


def fetch_majors(args: argparse.Namespace) -> Any:
    return request_json("/api/securityFe/api/index/majors")


def fetch_polling(args: argparse.Namespace) -> Any:
    return request_json(build_path("/api/polling/domestic/index", {"itemCodes": args.codes}))


def fetch_chart(args: argparse.Namespace) -> Any:
    return request_json(
        build_path(
            f"/api/securityService/chart/domestic/index/{args.code}",
            {"periodType": args.period_type, "range": args.range},
        )
    )


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


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    sub = parser.add_subparsers(dest="command", required=True)

    majors = sub.add_parser("majors", help="Major Korean indices")
    majors.add_argument("--output")
    majors.set_defaults(func=fetch_majors)

    polling = sub.add_parser("polling", help="Domestic index polling")
    polling.add_argument("--codes", default="KOSPI,KOSDAQ,KPI200")
    polling.add_argument("--output")
    polling.set_defaults(func=fetch_polling)

    chart = sub.add_parser("chart", help="Index chart")
    chart.add_argument("--code", default="KOSPI")
    chart.add_argument("--period-type", default="day")
    chart.add_argument("--range")
    chart.add_argument("--output")
    chart.set_defaults(func=fetch_chart)

    category = sub.add_parser("category", help="Market indicator category")
    category.add_argument(
        "--category",
        choices=["energy", "metals", "agricultural", "transport", "domesticInterest"],
        required=True,
    )
    category.add_argument("--output")
    category.set_defaults(func=fetch_category)

    detail = sub.add_parser("detail", help="Market indicator detail")
    detail.add_argument("--category", choices=["energy", "metals", "agricultural", "exchange", "standardInterest", "bond"], required=True)
    detail.add_argument("--code", required=True, help="Reuters code or nation code for bond/standardInterest")
    detail.add_argument("--sort-type")
    detail.add_argument("--output")
    detail.set_defaults(func=fetch_detail)

    prices = sub.add_parser("prices", help="Market indicator price history")
    prices.add_argument("--category", choices=["energy", "metals", "agricultural", "exchange"], required=True)
    prices.add_argument("--code", required=True)
    prices.add_argument("--page", type=int, default=1)
    prices.add_argument("--page-size", type=int, default=20)
    prices.add_argument("--output")
    prices.set_defaults(func=fetch_prices)

    upcoming = sub.add_parser("economic-upcoming", help="Upcoming economic indicators")
    upcoming.add_argument("--limit", type=int)
    upcoming.add_argument("--nation-type", action="append")
    upcoming.add_argument("--output")
    upcoming.set_defaults(func=fetch_economic_upcoming)

    release = sub.add_parser("economic-release", help="Economic indicators by release date")
    release.add_argument("--page", type=int, default=1)
    release.add_argument("--page-size", type=int, default=20)
    release.add_argument("--release-date")
    release.add_argument("--nation-type", action="append")
    release.add_argument("--output")
    release.set_defaults(func=fetch_economic_release)

    rates = sub.add_parser("exchange-rates", help="Exchange-rate helper list")
    rates.add_argument("--currencies", default="USD,JPY,EUR,CNY")
    rates.add_argument("--output")
    rates.set_defaults(func=fetch_exchange_rates)

    args = parser.parse_args()
    emit_output(render_json(args.func(args)), args.output)


if __name__ == "__main__":
    main()
