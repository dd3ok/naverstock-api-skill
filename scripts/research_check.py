#!/usr/bin/env python3
"""Check one research category's first two pages; preview only unless --live is set."""

from __future__ import annotations

import argparse
from datetime import datetime, timezone
import time
from typing import Any

import research
from naverstock_api import NaverStockAPIError, emit_output, render_json, request_json


PAGE_SIZE = 2
REQUEST_INTERVAL = 1.0


def build_plan(category: str) -> list[dict[str, Any]]:
    if category not in research.CATEGORIES:
        raise ValueError("Unknown research category")
    return [
        {
            "page": page,
            "path": research.build_category_path(
                argparse.Namespace(
                    category=category,
                    page=page,
                    page_size=PAGE_SIZE,
                    search_text=None,
                    start_date=None,
                    end_date=None,
                    broker_code=None,
                    industry_type=None,
                    item_code=None,
                )
            ),
            "status": "not_run",
        }
        for page in (1, 2)
    ]


def check_page(payload: Any) -> tuple[set[str], bool]:
    """Validate only the fields needed for this check; allow additional fields."""
    if not isinstance(payload, dict) or not isinstance(payload.get("items"), list):
        raise ValueError("Expected an object with an items list")
    has_next = payload.get("hasNext")
    if not isinstance(has_next, bool):
        raise ValueError("Expected boolean hasNext")
    items = payload["items"]
    if len(items) > PAGE_SIZE:
        raise ValueError("Response exceeds the requested page size")
    ids = set()
    for item in items:
        nid = item.get("nid") if isinstance(item, dict) else None
        if type(nid) not in (str, int):
            raise ValueError("Expected a numeric public report nid")
        value = str(nid)
        if not value.isascii() or not value.isdigit() or not 1 <= len(value) <= 30:
            raise ValueError("Expected a numeric public report nid")
        ids.add(value)
    if len(ids) != len(items):
        raise ValueError("Duplicate report IDs within a page")
    if not items and has_next:
        raise ValueError("Empty page advertises a next page")
    return ids, has_next


def run_check(category: str, *, live: bool = False) -> dict[str, Any]:
    checks = build_plan(category)
    report: dict[str, Any] = {
        "category": category,
        "pageSize": PAGE_SIZE,
        "status": "planned",
        "pagination": "not_checked",
        "checks": checks,
    }
    if not live:
        return report

    report["status"] = "passed"
    previous_ids: set[str] = set()
    for index, check in enumerate(checks):
        if index:
            time.sleep(REQUEST_INTERVAL)
        check["checkedAt"] = datetime.now(timezone.utc).isoformat()
        try:
            payload = request_json(check["path"])
        except NaverStockAPIError as exc:
            # Keep the diagnosis category, never the remote body or exception detail.
            check.update(status="request_error", httpStatus=exc.status_code, errorKind=exc.kind)
            report["status"] = "failed"
            break
        try:
            ids, has_next = check_page(payload)
        except ValueError as exc:
            check.update(status="contract_error", reason=str(exc))
            report["status"] = "failed"
            break
        check.update(status="ok" if ids else "empty", count=len(ids), hasNext=has_next)
        if index and previous_ids & ids:
            check.update(
                status="paging_overlap",
                reason="Report IDs overlap; the live list may have changed between requests",
            )
            report.update(status="failed", pagination="overlap")
            break
        if index and ids:
            report["pagination"] = "disjoint"
        if not has_next:
            if not index:
                report["pagination"] = "terminal"
                checks[1].update(status="skipped", reason="First page hasNext is false")
            elif not ids:
                report["pagination"] = "empty_next_page"
            break
        previous_ids = ids
    return report


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--category", choices=research.CATEGORIES, default="COMPANY")
    parser.add_argument(
        "--live", action="store_true", help="Make at most two GET requests, 1s apart"
    )
    parser.add_argument(
        "--output", help="Save the bounded JSON summary instead of printing it"
    )
    args = parser.parse_args()
    report = run_check(args.category, live=args.live)
    emit_output(render_json(report), args.output)
    return 1 if report["status"] == "failed" else 0


if __name__ == "__main__":
    raise SystemExit(main())
