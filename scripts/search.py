#!/usr/bin/env python3
"""Search public Naver Stock products without reading recent or personal history."""

from __future__ import annotations

import argparse
from typing import Any

from naverstock_api import bounded_int, build_path, emit_output, render_json, request_json


SEARCH_TARGETS = ("stock", "index", "marketindicator", "coin", "ipo", "fund")


def search_query(value: str) -> str:
    clean = value.strip()
    if not 1 <= len(clean) <= 100 or any(ord(char) < 32 or ord(char) == 127 for char in clean):
        raise argparse.ArgumentTypeError("query must contain 1-100 printable characters")
    return clean


def bounded(name: str, minimum: int, maximum: int):
    def parse(value: str) -> int:
        try:
            return bounded_int(value, name=name, minimum=minimum, maximum=maximum)
        except ValueError as exc:
            raise argparse.ArgumentTypeError(str(exc)) from exc

    return parse


def target_value(args: argparse.Namespace) -> str:
    return ",".join(args.target or SEARCH_TARGETS)


def fetch_autocomplete(args: argparse.Namespace) -> Any:
    return request_json(
        build_path(
            "/api/autocomplete/search/autoComplete",
            {"query": args.query, "target": target_value(args)},
        )
    )


def fetch_search(args: argparse.Namespace) -> Any:
    return request_json(
        build_path(
            "/api/autocomplete/search",
            {
                "q": args.query,
                "target": target_value(args),
                "size": args.size,
                "page": args.page,
            },
        )
    )


def add_common(parser: argparse.ArgumentParser) -> None:
    parser.add_argument("--query", required=True, type=search_query)
    parser.add_argument(
        "--target",
        choices=SEARCH_TARGETS,
        action="append",
        help="Repeat to limit product families; defaults to every public family",
    )
    parser.add_argument("--output")


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    sub = parser.add_subparsers(dest="command", required=True)

    autocomplete = sub.add_parser("autocomplete", help="Header product autocomplete")
    add_common(autocomplete)
    autocomplete.set_defaults(func=fetch_autocomplete)

    search = sub.add_parser("search", help="Full product search")
    add_common(search)
    search.add_argument("--size", type=bounded("size", 1, 100), default=30)
    search.add_argument("--page", type=bounded("page", 1, 100), default=1)
    search.set_defaults(func=fetch_search)

    args = parser.parse_args()
    emit_output(render_json(args.func(args)), args.output)


if __name__ == "__main__":
    main()
