#!/usr/bin/env python3
"""Fetch domestic market deposit, investor-trend, and program-trend payloads."""

from __future__ import annotations

import argparse
from typing import Any

from naverstock_api import build_path, emit_output, render_json, request_json


def fetch_deposit(args: argparse.Namespace) -> Any:
    return request_json(
        build_path("/api/domestic/market/trendDeposit", {"startIdx": args.start_idx, "pageSize": args.page_size})
    )


def fetch_deposit_chart(args: argparse.Namespace) -> Any:
    return request_json(
        build_path("/api/domestic/market/trendDeposit/chart", {"startDate": args.start_date, "endDate": args.end_date})
    )


def fetch_aggregate(args: argparse.Namespace) -> Any:
    body = {
        "sections": {
            "investorTrend": {
                "tradeType": args.trade_type,
                "marketType": args.market_type,
                "periodType": args.period_type,
                **({"startDate": args.start_date, "endDate": args.end_date} if args.start_date and args.end_date else {}),
            }
        }
    }
    return request_json("/api/domestic/home/marketaggregate/aggregateInvestor", method="POST", body=body)


def fetch_trend_foreign_org(args: argparse.Namespace) -> Any:
    return request_json(
        build_path(
            "/api/domestic/market/trend/trendForeignOrg",
            {
                "investorType": args.investor_type,
                "tradeType": args.trade_type,
                "marketType": args.market_type,
                "startIdx": args.start_idx,
                "pageSize": args.page_size,
                "periodType": args.period_type,
            },
        )
    )


def fetch_trend_daily(args: argparse.Namespace) -> Any:
    return request_json(
        build_path(
            "/api/domestic/market/trend/daily",
            {
                "tradeType": args.trade_type,
                "marketType": args.market_type,
                "bizdate": args.bizdate,
                "startIdx": args.start_idx,
                "pageSize": args.page_size,
            },
        )
    )


def fetch_trend_time_chart(args: argparse.Namespace) -> Any:
    return request_json(
        build_path(
            "/api/domestic/market/trend/chart/time",
            {
                "tradeType": args.trade_type,
                "marketType": args.market_type,
                "selectedRange": args.selected_range,
                "bizdate": args.bizdate,
                "startDate": args.start_date,
                "endDate": args.end_date,
            },
        )
    )


def fetch_trend_program(args: argparse.Namespace) -> Any:
    return request_json(
        build_path(
            "/api/domestic/market/trendProgram",
            {
                "tradeType": args.trade_type,
                "krxMarketType": args.krx_market_type,
                "bizdate": args.bizdate,
                "startIdx": args.start_idx,
                "pageSize": args.page_size,
                "periodType": args.period_type,
            },
        )
    )


def fetch_trend_program_chart(args: argparse.Namespace) -> Any:
    return request_json(
        build_path(
            "/api/domestic/market/trendProgram/chart",
            {
                "tradeType": args.trade_type,
                "krxMarketType": args.krx_market_type,
                "bizdate": args.bizdate,
                "startDate": args.start_date,
                "endDate": args.end_date,
                "periodType": args.period_type,
            },
        )
    )


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    sub = parser.add_subparsers(dest="command", required=True)

    deposit = sub.add_parser("deposit", help="Investor deposit trend list")
    deposit.add_argument("--start-idx", type=int, default=0)
    deposit.add_argument("--page-size", type=int, default=20)
    deposit.add_argument("--output")
    deposit.set_defaults(func=fetch_deposit)

    chart = sub.add_parser("deposit-chart", help="Investor deposit chart")
    chart.add_argument("--start-date", required=True, help="YYYYMMDD")
    chart.add_argument("--end-date", required=True, help="YYYYMMDD")
    chart.add_argument("--output")
    chart.set_defaults(func=fetch_deposit_chart)

    aggregate = sub.add_parser("aggregate", help="Market aggregate investor trend")
    aggregate.add_argument("--trade-type", choices=["KRX", "NXT"], default="KRX")
    aggregate.add_argument("--market-type", choices=["ALL", "KOSPI", "KOSDAQ", "FUT"], default="ALL")
    aggregate.add_argument("--period-type", choices=["TIME", "WEEK", "MONTH", "THREE_MONTH"], default="TIME")
    aggregate.add_argument("--start-date")
    aggregate.add_argument("--end-date")
    aggregate.add_argument("--output")
    aggregate.set_defaults(func=fetch_aggregate)

    trend_foreign_org = sub.add_parser("trend-foreign-org", help="Foreign and institution market trend rankings")
    trend_foreign_org.add_argument("--investor-type", default="FOREIGNER")
    trend_foreign_org.add_argument("--market-type", choices=["ALL", "KOSPI", "KOSDAQ"], default="ALL")
    trend_foreign_org.add_argument("--trade-type", choices=["KRX", "NXT"], default="KRX")
    trend_foreign_org.add_argument("--start-idx", type=int, default=0)
    trend_foreign_org.add_argument("--page-size", type=int, default=20)
    trend_foreign_org.add_argument("--period-type", default="DAY")
    trend_foreign_org.add_argument("--output")
    trend_foreign_org.set_defaults(func=fetch_trend_foreign_org)

    daily = sub.add_parser("trend-daily", help="Daily investor trend rows")
    daily.add_argument("--trade-type", choices=["KRX", "NXT"], default="KRX")
    daily.add_argument("--market-type", choices=["ALL", "KOSPI", "KOSDAQ"], default="ALL")
    daily.add_argument("--bizdate", required=True, help="YYYYMMDD")
    daily.add_argument("--start-idx", type=int, default=0)
    daily.add_argument("--page-size", type=int, default=20)
    daily.add_argument("--output")
    daily.set_defaults(func=fetch_trend_daily)

    time_chart = sub.add_parser("trend-time-chart", help="Investor trend time chart")
    time_chart.add_argument("--trade-type", choices=["KRX", "NXT"], default="KRX")
    time_chart.add_argument("--market-type", choices=["ALL", "KOSPI", "KOSDAQ"], default="ALL")
    time_chart.add_argument("--selected-range", default="1일")
    time_chart.add_argument("--bizdate", required=True, help="YYYYMMDD")
    time_chart.add_argument("--start-date", required=True, help="YYYYMMDD")
    time_chart.add_argument("--end-date", required=True, help="YYYYMMDD")
    time_chart.add_argument("--output")
    time_chart.set_defaults(func=fetch_trend_time_chart)

    program = sub.add_parser("trend-program", help="Program trading trend rows")
    program.add_argument("--trade-type", choices=["KRX", "NXT"], default="KRX")
    program.add_argument("--krx-market-type", choices=["ALL", "KOSPI", "KOSDAQ"], default="ALL")
    program.add_argument("--bizdate", required=True, help="YYYYMMDD")
    program.add_argument("--start-idx", type=int, default=0)
    program.add_argument("--page-size", type=int, default=20)
    program.add_argument("--period-type", default="TIME")
    program.add_argument("--output")
    program.set_defaults(func=fetch_trend_program)

    program_chart = sub.add_parser("trend-program-chart", help="Program trading trend chart")
    program_chart.add_argument("--trade-type", choices=["KRX", "NXT"], default="KRX")
    program_chart.add_argument("--krx-market-type", choices=["ALL", "KOSPI", "KOSDAQ"], default="ALL")
    program_chart.add_argument("--bizdate", required=True, help="YYYYMMDD")
    program_chart.add_argument("--start-date", required=True, help="YYYYMMDD")
    program_chart.add_argument("--end-date", required=True, help="YYYYMMDD")
    program_chart.add_argument("--period-type", default="TIME")
    program_chart.add_argument("--output")
    program_chart.set_defaults(func=fetch_trend_program_chart)

    args = parser.parse_args()
    emit_output(render_json(args.func(args)), args.output)


if __name__ == "__main__":
    main()
