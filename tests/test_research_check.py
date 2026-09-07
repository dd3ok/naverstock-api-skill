from __future__ import annotations

import json
from io import StringIO
from pathlib import Path
import subprocess
import sys
import unittest
from unittest.mock import call, patch

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "scripts"))

import research_check  # noqa: E402
from naverstock_api import NaverStockAPIError  # noqa: E402


def page(*ids: int | str, has_next: bool = True) -> dict:
    return {
        "items": [{"nid": nid, "title": "not included in the summary"} for nid in ids],
        "hasNext": has_next,
        "extra": "allowed",
    }


class ResearchCheckTests(unittest.TestCase):
    def test_failure_summary_distinguishes_local_error_kinds_without_remote_text(self) -> None:
        for kind in ("timeout", "network", "transport", "encoding", "invalid_json",
                     "response_too_large", "api", "http", "unknown"):
            with self.subTest(kind=kind), patch.object(
                research_check, "request_json",
                side_effect=NaverStockAPIError("remote secret", path="remote path",
                                              detail="remote body", kind=kind),
            ) as request:
                report = research_check.run_check("COMPANY", live=True)
                self.assertEqual(report["checks"][0]["errorKind"], kind)
                self.assertEqual(report["checks"][1]["status"], "not_run")
                self.assertNotIn("remote", json.dumps(report))
                request.assert_called_once()

    def test_preview_uses_existing_category_contract_without_network_or_sleep(
        self,
    ) -> None:
        with (
            patch.object(research_check, "request_json") as request,
            patch.object(research_check.time, "sleep") as sleep,
        ):
            report = research_check.run_check("MARKET")
        request.assert_not_called()
        sleep.assert_not_called()
        self.assertEqual(report["status"], "planned")
        self.assertEqual(
            [row["path"] for row in report["checks"]],
            [
                "/api/stockSecurity/researches/v2/market?index=0&size=2",
                "/api/stockSecurity/researches/v2/market?index=1&size=2",
            ],
        )
        self.assertTrue(all(row["status"] == "not_run" for row in report["checks"]))

    def test_two_pages_have_a_gap_and_only_sanitized_summary_is_returned(self) -> None:
        events = []

        def fetch(path):
            events.append(path)
            return page(1, "2") if len(events) == 1 else page(3, 4)

        with (
            patch.object(research_check, "request_json", side_effect=fetch) as request,
            patch.object(research_check.time, "sleep", side_effect=events.append),
        ):
            report = research_check.run_check("COMPANY", live=True)
        self.assertEqual(
            events,
            [
                "/api/stockSecurity/researches/v2/company?index=0&size=2",
                1.0,
                "/api/stockSecurity/researches/v2/company?index=1&size=2",
            ],
        )
        self.assertEqual(request.call_count, 2)
        self.assertEqual(report["status"], "passed")
        self.assertEqual(report["pagination"], "disjoint")
        self.assertEqual([row["count"] for row in report["checks"]], [2, 2])
        self.assertTrue(
            all(row["checkedAt"].endswith("+00:00") for row in report["checks"])
        )
        self.assertNotIn("title", json.dumps(report))
        self.assertNotIn("nid", json.dumps(report))

    def test_terminal_first_page_skips_second_request_even_when_empty(self) -> None:
        for payload in (page(has_next=False), page(1, has_next=False)):
            with (
                self.subTest(payload=payload),
                patch.object(
                    research_check, "request_json", return_value=payload
                ) as request,
                patch.object(research_check.time, "sleep") as sleep,
            ):
                report = research_check.run_check("COMPANY", live=True)
                self.assertEqual(report["pagination"], "terminal")
                self.assertEqual(report["status"], "passed")
                self.assertEqual(report["checks"][1]["status"], "skipped")
                request.assert_called_once()
                sleep.assert_not_called()

    def test_overlap_is_reported_without_retrying_or_claiming_endpoint_removal(
        self,
    ) -> None:
        with (
            patch.object(
                research_check, "request_json", side_effect=[page(1, 2), page("2", 3)]
            ) as request,
            patch.object(research_check.time, "sleep"),
        ):
            report = research_check.run_check("COMPANY", live=True)
        self.assertEqual(report["status"], "failed")
        self.assertEqual(report["pagination"], "overlap")
        self.assertEqual(request.call_count, 2)

    def test_empty_second_page_does_not_claim_disjoint_nonempty_paging(self) -> None:
        with (
            patch.object(
                research_check,
                "request_json",
                side_effect=[page(1), page(has_next=False)],
            ),
            patch.object(research_check.time, "sleep"),
        ):
            report = research_check.run_check("COMPANY", live=True)
        self.assertEqual(report["pagination"], "empty_next_page")
        self.assertEqual(report["checks"][1]["status"], "empty")

    def test_contract_changes_stop_before_the_second_request(self) -> None:
        invalid = [
            [],
            {},
            {"items": [], "hasNext": 0},
            page(),
            page(True),
            page(1, "1"),
            page(1, 2, 3),
            page("secret"),
            {"items": [{}], "hasNext": True},
            {"items": [None], "hasNext": False},
        ]
        for payload in invalid:
            with (
                self.subTest(payload=payload),
                patch.object(
                    research_check, "request_json", return_value=payload
                ) as request,
                patch.object(research_check.time, "sleep") as sleep,
            ):
                report = research_check.run_check("COMPANY", live=True)
                self.assertEqual(report["status"], "failed")
                self.assertEqual(report["checks"][0]["status"], "contract_error")
                self.assertEqual(report["checks"][1]["status"], "not_run")
                request.assert_called_once()
                sleep.assert_not_called()
                self.assertNotIn("secret", json.dumps(report))

    def test_remote_errors_stop_and_preserve_prior_results_without_remote_detail(
        self,
    ) -> None:
        for status in (None, 302, 403, 404, 429, 500):
            for position in (0, 1):
                error = NaverStockAPIError(
                    "remote secret",
                    path="secret",
                    status_code=status,
                    detail="remote body secret",
                )
                responses = [error] if not position else [page(1, 2), error]
                with (
                    self.subTest(status=status, position=position),
                    patch.object(
                        research_check, "request_json", side_effect=responses
                    ) as request,
                    patch.object(research_check.time, "sleep") as sleep,
                ):
                    report = research_check.run_check("COMPANY", live=True)
                    self.assertEqual(report["status"], "failed")
                    self.assertEqual(report["checks"][position]["httpStatus"], status)
                    self.assertEqual(request.call_count, position + 1)
                    self.assertEqual(
                        sleep.call_args_list, [call(1.0)] if position else []
                    )
                    self.assertEqual(
                        report["checks"][1 - position]["status"],
                        "ok" if position else "not_run",
                    )
                    self.assertNotIn("secret", json.dumps(report))

    def test_cli_failure_emits_summary_and_nonzero_status(self) -> None:
        with (
            patch.object(sys, "argv", ["research_check.py", "--live"]),
            patch.object(sys, "stdout", new_callable=StringIO) as output,
            patch.object(research_check, "request_json", return_value={}),
        ):
            self.assertEqual(research_check.main(), 1)
        self.assertEqual(json.loads(output.getvalue())["status"], "failed")

    def test_real_cli_defaults_to_preview_and_rejects_unknown_category(self) -> None:
        command = [sys.executable, "-B", str(ROOT / "scripts" / "research_check.py")]
        result = subprocess.run(
            command, capture_output=True, text=True, check=True, timeout=10
        )
        self.assertEqual(json.loads(result.stdout)["status"], "planned")
        result = subprocess.run(
            command + ["--category", "UNKNOWN", "--live"],
            capture_output=True,
            text=True,
            timeout=10,
        )
        self.assertEqual(result.returncode, 2)
        self.assertNotIn("Traceback", result.stderr)


if __name__ == "__main__":
    unittest.main()
