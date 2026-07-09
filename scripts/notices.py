#!/usr/bin/env python3
"""Fetch read-only Naver Stock service notice payloads."""

from __future__ import annotations

import argparse
from typing import Any

from naverstock_api import build_path, emit_output, render_json, request_json


def fetch_list(args: argparse.Namespace) -> Any:
    return request_json(build_path("/api/stockSecurity/notices/v1", {"size": args.size, "cursor": args.cursor}))


def fetch_detail(args: argparse.Namespace) -> Any:
    return request_json(f"/api/stockSecurity/notices/v1/{args.notice_id}")


def fetch_banners(args: argparse.Namespace) -> Any:
    return request_json(
        build_path("/api/stockSecurity/notices/v1/banners", {"size": args.size, "type": args.banner_type})
    )


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    sub = parser.add_subparsers(dest="command", required=True)

    list_cmd = sub.add_parser("list", help="Service notice list")
    list_cmd.add_argument("--size", type=int, default=20)
    list_cmd.add_argument("--cursor")
    list_cmd.add_argument("--output")
    list_cmd.set_defaults(func=fetch_list)

    detail = sub.add_parser("detail", help="Service notice detail")
    detail.add_argument("--notice-id", required=True)
    detail.add_argument("--output")
    detail.set_defaults(func=fetch_detail)

    banners = sub.add_parser("banners", help="Service notice banners")
    banners.add_argument("--size", type=int, default=2)
    banners.add_argument("--banner-type", default="PC_TOP")
    banners.add_argument("--output")
    banners.set_defaults(func=fetch_banners)

    args = parser.parse_args()
    emit_output(render_json(args.func(args)), args.output)


if __name__ == "__main__":
    main()
