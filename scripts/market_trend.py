#!/usr/bin/env python3
"""Fetch domestic market deposit and investor-trend payloads."""

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

    args = parser.parse_args()
    emit_output(render_json(args.func(args)), args.output)


if __name__ == "__main__":
    main()
