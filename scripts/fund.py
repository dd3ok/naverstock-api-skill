#!/usr/bin/env python3
"""Fetch public read-only Naver Stock fund detail payloads."""

from __future__ import annotations

import argparse
from datetime import date
import re
from typing import Any, Callable

from naverstock_api import build_path, emit_output, render_json, request_json


_FUND_CODE = re.compile(r"^[A-Z0-9][A-Z0-9_-]{0,31}$")
_TERM = re.compile(r"^[a-z0-9][a-z0-9_-]{0,15}$")


def fund_code(value: str) -> str:
    """Normalize a public fund code while rejecting path/query separators."""

    result = value.strip().upper() if isinstance(value, str) else ""
    if not _FUND_CODE.fullmatch(result):
        raise argparse.ArgumentTypeError(
            "fund code must contain only letters, digits, underscore, or hyphen"
        )
    return result


def term_token(value: str) -> str:
    """Normalize a short chart term without guessing a closed server enum."""

    result = value.strip().lower() if isinstance(value, str) else ""
    if not _TERM.fullmatch(result):
        raise argparse.ArgumentTypeError(
            "term must be a short token containing only letters, digits, underscore, or hyphen"
        )
    return result


def iso_date(value: str) -> str:
    """Require a real calendar date in ISO YYYY-MM-DD form."""

    try:
        parsed = date.fromisoformat(value)
    except (TypeError, ValueError) as exc:
        raise argparse.ArgumentTypeError("date must be a valid ISO date (YYYY-MM-DD)") from exc
    if parsed.isoformat() != value:
        raise argparse.ArgumentTypeError("date must use ISO YYYY-MM-DD form")
    return value


def bounded_int(name: str, minimum: int, maximum: int) -> Callable[[str], int]:
    """Build an argparse integer parser with an explicit safe range."""

    def parse(value: str) -> int:
        try:
            result = int(value)
        except ValueError as exc:
            raise argparse.ArgumentTypeError(f"{name} must be an integer") from exc
        if not minimum <= result <= maximum:
            raise argparse.ArgumentTypeError(
                f"{name} must be between {minimum} and {maximum}"
            )
        return result

    return parse


def _detail_path(code: str, suffix: str) -> str:
    return f"/api/fund/funds/{code}/{suffix}"


def fetch_left_panel(args: argparse.Namespace) -> Any:
    return request_json(_detail_path(args.code, "left-panel"))


def fetch_base_price_chart(args: argparse.Namespace) -> Any:
    return request_json(
        build_path(_detail_path(args.code, "base-price/chart"), {"term": args.term})
    )


def fetch_chart_price_panel(args: argparse.Namespace) -> Any:
    return request_json(_detail_path(args.code, "chart-price-panel"))


def fetch_performance(args: argparse.Namespace) -> Any:
    return request_json(_detail_path(args.code, "fund-performance"))


def fetch_metrics(args: argparse.Namespace) -> Any:
    return request_json(
        build_path(_detail_path(args.code, "metrics/detail"), {"term": args.term})
    )


def fetch_daily_prices(args: argparse.Namespace) -> Any:
    return request_json(
        build_path(
            _detail_path(args.code, "prices/daily"),
            {"date": args.date, "size": args.size},
        )
    )


def fetch_class_returns(args: argparse.Namespace) -> Any:
    return request_json(_detail_path(args.code, "classes/returns"))


def fetch_allocation(args: argparse.Namespace) -> Any:
    return request_json(_detail_path(args.code, "fund-allocation"))


def _add_common_args(parser: argparse.ArgumentParser) -> None:
    parser.add_argument(
        "--code",
        required=True,
        type=fund_code,
        help="Public fund code, for example K55105B00244",
    )
    parser.add_argument("--output", help="Write output to a file instead of stdout")


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    sub = parser.add_subparsers(dest="command", required=True)

    for name, help_text, func in [
        ("left-panel", "Fund title and left-panel summary", fetch_left_panel),
        ("chart-price-panel", "Fund chart price summary", fetch_chart_price_panel),
        ("performance", "Fund performance summary", fetch_performance),
        ("class-returns", "Fund class return rows", fetch_class_returns),
        ("allocation", "Fund asset allocation", fetch_allocation),
    ]:
        command = sub.add_parser(name, help=help_text)
        _add_common_args(command)
        command.set_defaults(func=func)

    chart = sub.add_parser("base-price-chart", help="Fund base-price chart series")
    _add_common_args(chart)
    chart.add_argument("--term", type=term_token, default="3m")
    chart.set_defaults(func=fetch_base_price_chart)

    metrics = sub.add_parser("metrics", help="Fund detail metrics for a term")
    _add_common_args(metrics)
    metrics.add_argument("--term", type=term_token, default="1y")
    metrics.set_defaults(func=fetch_metrics)

    daily = sub.add_parser("daily-prices", help="Fund daily price rows")
    _add_common_args(daily)
    daily.add_argument("--date", type=iso_date, default=date.today().isoformat())
    daily.add_argument("--size", type=bounded_int("size", 1, 100), default=10)
    daily.set_defaults(func=fetch_daily_prices)

    args = parser.parse_args()
    emit_output(render_json(args.func(args)), args.output)


if __name__ == "__main__":
    main()
