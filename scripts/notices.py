#!/usr/bin/env python3
"""Fetch read-only Naver Stock service notice payloads."""

from __future__ import annotations

import argparse
import re
from typing import Any

from naverstock_api import bounded_int, build_path, emit_output, render_json, request_json


_NOTICE_ID = re.compile(r"^[0-9]{1,20}$")
_CURSOR = re.compile(r"^[A-Za-z0-9_=-]{1,512}$")
_BANNER_TYPE = re.compile(r"^[A-Z][A-Z0-9_]{0,31}$")


def _bounded_size(value: str) -> int:
    try:
        return bounded_int(value, name="size", minimum=1, maximum=100)
    except ValueError as exc:
        raise argparse.ArgumentTypeError(str(exc)) from exc


def _notice_id(value: str) -> str:
    clean = value.strip()
    if not _NOTICE_ID.fullmatch(clean):
        raise argparse.ArgumentTypeError("notice-id must contain 1-20 digits")
    return clean


def _cursor(value: str) -> str:
    clean = value.strip()
    if not _CURSOR.fullmatch(clean):
        raise argparse.ArgumentTypeError("cursor must be a bounded opaque token")
    return clean


def _banner_type(value: str) -> str:
    clean = value.strip().upper()
    if not _BANNER_TYPE.fullmatch(clean):
        raise argparse.ArgumentTypeError("banner-type must be a short uppercase token")
    return clean


def fetch_list(args: argparse.Namespace) -> Any:
    return request_json(build_path("/api/stockSecurity/notices/v2", {"size": args.size, "cursor": args.cursor}))


def fetch_detail(args: argparse.Namespace) -> Any:
    return request_json(f"/api/stockSecurity/notices/v2/{args.notice_id}")


def fetch_banners(args: argparse.Namespace) -> Any:
    return request_json(
        build_path("/api/stockSecurity/notices/v2/banners", {"size": args.size, "type": args.banner_type})
    )


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    sub = parser.add_subparsers(dest="command", required=True)

    list_cmd = sub.add_parser("list", help="Service notice list")
    list_cmd.add_argument("--size", type=_bounded_size, default=20)
    list_cmd.add_argument("--cursor", type=_cursor)
    list_cmd.add_argument("--output")
    list_cmd.set_defaults(func=fetch_list)

    detail = sub.add_parser("detail", help="Service notice detail")
    detail.add_argument("--notice-id", required=True, type=_notice_id)
    detail.add_argument("--output")
    detail.set_defaults(func=fetch_detail)

    banners = sub.add_parser("banners", help="Service notice banners")
    banners.add_argument("--size", type=_bounded_size, default=2)
    banners.add_argument("--banner-type", type=_banner_type, default="PC_TOP")
    banners.add_argument("--output")
    banners.set_defaults(func=fetch_banners)

    args = parser.parse_args()
    emit_output(render_json(args.func(args)), args.output)


if __name__ == "__main__":
    main()
