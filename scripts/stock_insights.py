#!/usr/bin/env python3
"""Fetch public aggregate investor insights for domestic or foreign stocks."""

from __future__ import annotations

import argparse
import re
from typing import Any

from naverstock_api import (
    build_path,
    emit_output,
    normalize_item_code,
    render_json,
    request_json,
)


_FOREIGN_CODE = re.compile(r"^[A-Za-z0-9][A-Za-z0-9._=-]{0,31}$")


def _asset_code(asset_type: str, value: str) -> str:
    if asset_type == "domestic":
        return normalize_item_code(value)
    clean = value.strip().upper() if isinstance(value, str) else ""
    if not _FOREIGN_CODE.fullmatch(clean):
        raise ValueError("foreign code contains an unsupported character or path separator")
    return clean


def fetch_holder_ranking(args: argparse.Namespace) -> Any:
    code = _asset_code(args.asset_type, args.code)
    return request_json(f"/api/securityService/home/v3/mystock/ranking/{code}")


def fetch_what_if(args: argparse.Namespace) -> Any:
    code = _asset_code(args.asset_type, args.code)
    return request_json(
        build_path(
            f"/api/securityService/home/v3/whatIf/{args.asset_type}/{code}",
            {"periodType": "year", "range": 5},
        )
    )


def _add_stock_arguments(parser: argparse.ArgumentParser) -> None:
    parser.add_argument("--asset-type", choices=["domestic", "worldstock"], default="domestic")
    parser.add_argument("--code", required=True, help="Domestic item code or foreign Reuters code")
    parser.add_argument("--output")


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    sub = parser.add_subparsers(dest="command", required=True)

    ranking = sub.add_parser(
        "holder-ranking",
        help="Public all-user holding rank shown on the stock insight page",
    )
    _add_stock_arguments(ranking)
    ranking.set_defaults(func=fetch_holder_ranking)

    what_if = sub.add_parser(
        "what-if",
        help="Five-year hypothetical return series shown on the stock insight page",
    )
    _add_stock_arguments(what_if)
    what_if.set_defaults(func=fetch_what_if)

    args = parser.parse_args()
    try:
        payload = args.func(args)
    except ValueError as exc:
        parser.error(str(exc))
    emit_output(render_json(payload), args.output)


if __name__ == "__main__":
    main()
