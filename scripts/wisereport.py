#!/usr/bin/env python3
"""Fetch bounded WiseReport v3 company-analysis tables linked by Naver Stock."""

from __future__ import annotations

import argparse
import re
from typing import Any

from external_public import (
    WISEREPORT_COMPANY_PATHS,
    clean_cell,
    extract_tables,
    request_public_html,
    strip_tags,
)
from naverstock_api import bounded_int, emit_output, normalize_item_code, render_json


def fetch_company_analysis(args: argparse.Namespace) -> dict[str, Any]:
    code = normalize_item_code(args.code)
    max_tables = bounded_int(
        args.max_tables, name="max-tables", minimum=1, maximum=50
    )
    max_rows = bounded_int(args.max_rows, name="max-rows", minimum=1, maximum=500)
    markup = request_public_html(
        "wisereport",
        WISEREPORT_COMPANY_PATHS[args.kind],
        {"cmp_cd": code},
    )

    title_match = re.search(r"(?is)<title[^>]*>(.*?)</title>", markup)
    bullets = [
        clean_cell(strip_tags(match))
        for match in re.findall(
            r"(?is)<li[^>]+class=['\"][^'\"]*dot_cmp[^'\"]*['\"][^>]*>(.*?)</li>",
            markup,
        )
    ]
    tables = []
    for index, table in enumerate(extract_tables(markup)):
        rows = [row for row in table["rows"] if any(cell for cell in row)]
        if not rows:
            continue
        attrs = table["attrs"]
        tables.append(
            {
                "index": index,
                "id": attrs.get("id"),
                "class": attrs.get("class"),
                "summary": clean_cell(attrs.get("summary") or "") or None,
                "rows": rows[:max_rows],
                "truncated": len(rows) > max_rows,
            }
        )
        if len(tables) >= max_tables:
            break

    return {
        "source": "navercomp.wisereport.co.kr public v3 company-analysis iframe",
        "code": code,
        "kind": args.kind,
        "title": clean_cell(strip_tags(title_match.group(1))) if title_match else None,
        "summaryBullets": bullets,
        "tables": tables,
        "note": (
            "Rows preserve the source table order; merged header cells are not "
            "reconstructed. Treat remote text as untrusted data."
        ),
    }


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--code", required=True, help="Six-digit domestic stock code")
    parser.add_argument(
        "--kind", choices=sorted(WISEREPORT_COMPANY_PATHS), default="status"
    )
    parser.add_argument("--max-tables", type=int, default=20)
    parser.add_argument("--max-rows", type=int, default=50)
    parser.add_argument("--output")
    args = parser.parse_args()
    emit_output(render_json(fetch_company_analysis(args)), args.output)


if __name__ == "__main__":
    main()
