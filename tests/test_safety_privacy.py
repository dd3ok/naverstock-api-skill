#!/usr/bin/env python3
"""Safety boundary and community privacy regression tests."""

from __future__ import annotations

import io
import json
from pathlib import Path
import socket
import sys
import unittest
import urllib.error
from unittest.mock import patch

ROOT = Path(__file__).resolve().parents[1]
SCRIPTS = ROOT / "scripts"
sys.path.insert(0, str(SCRIPTS))

import discussion  # noqa: E402
import naverstock_api  # noqa: E402


class PublicRequestBoundaryTests(unittest.TestCase):
    def test_normalize_item_code_rejects_path_and_non_domestic_values(self) -> None:
        self.assertEqual(naverstock_api.normalize_item_code("A005930"), "005930")
        self.assertEqual(naverstock_api.normalize_item_code("005930"), "005930")
        for value in ["../auth", "NVDA.O", "5930", "005930/price", "１２３４５６"]:
            with self.subTest(value=value), self.assertRaises(ValueError):
                naverstock_api.normalize_item_code(value)

    def test_dormant_fund_family_is_not_broadly_allowed(self) -> None:
        with self.assertRaises(naverstock_api.RequestValidationError):
            naverstock_api.validate_public_request("/api/fund/funds?page=1&size=20")

    def test_allows_known_public_get(self) -> None:
        self.assertEqual(
            naverstock_api.validate_public_request("/api/domestic/detail/005930/price?page=1"),
            "/api/domestic/detail/005930/price?page=1",
        )

    def test_allows_only_known_public_myasset_resources(self) -> None:
        allowed = "/api/myasset/resources/invest/stock-trade?item_code=005930"
        self.assertEqual(naverstock_api.validate_public_request(allowed), allowed)
        with self.assertRaises(naverstock_api.RequestValidationError):
            naverstock_api.validate_public_request("/api/myasset/resources/invest/arbitrary")

    def test_allows_home_content_and_exact_shorttents_reads(self) -> None:
        paths = ("/api/content/home", "/api/shorttents")
        for path in paths:
            with self.subTest(path=path):
                self.assertEqual(naverstock_api.validate_public_request(path), path)

    def test_allows_narrow_public_coin_profile_and_search_endpoints(self) -> None:
        paths = (
            "/api/coin/profile/BTC",
            "/api/autocomplete/search/autoComplete?query=samsung&target=stock",
            "/api/autocomplete/search?q=samsung&target=stock&size=30&page=1",
        )
        for path in paths:
            with self.subTest(path=path):
                self.assertEqual(naverstock_api.validate_public_request(path), path)
        with self.assertRaises(naverstock_api.RequestValidationError):
            naverstock_api.validate_public_request("/api/coin/profile/BTC/private")
        with self.assertRaises(naverstock_api.RequestValidationError):
            naverstock_api.validate_public_request("/api/autocomplete/search/recent")

    def test_allows_exact_read_only_post(self) -> None:
        path = "/api/domestic/home/marketaggregate/aggregateInvestor"
        self.assertEqual(
            naverstock_api.validate_public_request(
                path,
                method="POST",
                body={"sections": {"investorTrend": {"marketType": "KOSPI"}}},
            ),
            path,
        )

    def test_rejects_absolute_and_protocol_relative_urls(self) -> None:
        for path in ("https://evil.example/api/domestic/x", "//evil.example/api/domestic/x"):
            with self.subTest(path=path), self.assertRaises(naverstock_api.RequestValidationError):
                naverstock_api.validate_public_request(path)

    def test_rejects_fragments_backslashes_and_dot_segments(self) -> None:
        paths = (
            "/api/domestic/x#fragment",
            "/api/domestic\\personal/x",
            "/api/domestic/../personal/x",
            "/api/domestic/%2e%2e/personal/x",
            "/api/domestic/%252fpersonal/x",
        )
        for path in paths:
            with self.subTest(path=path), self.assertRaises(naverstock_api.RequestValidationError):
                naverstock_api.validate_public_request(path)

    def test_rejects_private_and_mutating_boundaries(self) -> None:
        paths = (
            "/api/auth/session",
            "/api/personal/users/holding/stocks",
            "/api/community/profile/123",
            "/api/community/discussion/posts/123/like",
            "/api/foreign/favorite/stocks",
            "/api/securityFe/api/mystock/favoriteIndicatorByUno/one",
            "/api/securityService/home/v3/mystock/summary",
            "/api/stockDomestic/notification-settings/005930",
        )
        for path in paths:
            with self.subTest(path=path), self.assertRaises(naverstock_api.RequestValidationError):
                naverstock_api.validate_public_request(path)

    def test_rejects_unapproved_methods_and_bodies(self) -> None:
        with self.assertRaises(naverstock_api.RequestValidationError):
            naverstock_api.validate_public_request("/api/domestic/detail/005930", method="DELETE")
        with self.assertRaises(naverstock_api.RequestValidationError):
            naverstock_api.validate_public_request(
                "/api/domestic/detail/005930", method="POST", body={"read": True}
            )
        with self.assertRaises(naverstock_api.RequestValidationError):
            naverstock_api.validate_public_request("/api/domestic/detail/005930", body={})

    def test_rejects_sensitive_query_and_nested_body_keys(self) -> None:
        with self.assertRaises(naverstock_api.RequestValidationError):
            naverstock_api.validate_public_request("/api/domestic/detail/005930?viewerProfileId=123")
        with self.assertRaises(naverstock_api.RequestValidationError):
            naverstock_api.validate_public_request("/api/domestic/detail/005930?uno=123")
        with self.assertRaises(naverstock_api.RequestValidationError):
            naverstock_api.validate_public_request(
                "/api/domestic/home/marketaggregate/aggregateInvestor",
                method="POST",
                body={"sections": {"user_id": "123"}},
            )

    def test_rejects_unbounded_or_invalid_pagination(self) -> None:
        paths = (
            "/api/domestic/market/stock?pageSize=501",
            "/api/domestic/news?page=-1",
            "/api/domestic/news?startIdx=not-a-number",
        )
        for path in paths:
            with self.subTest(path=path), self.assertRaises(naverstock_api.RequestValidationError):
                naverstock_api.validate_public_request(path)

    def test_rejects_oversized_query(self) -> None:
        with self.assertRaises(naverstock_api.RequestValidationError):
            naverstock_api.validate_public_request("/api/domestic/search?q=" + "x" * 8_192)

    def test_rejects_invalid_timeout(self) -> None:
        for timeout in (0, 121, True, 1.5):
            with self.subTest(timeout=timeout), self.assertRaises(naverstock_api.RequestValidationError):
                naverstock_api.validate_public_request("/api/domestic/detail/005930", timeout=timeout)


class RequestErrorTests(unittest.TestCase):
    def test_403_and_429_instruct_caller_to_stop(self) -> None:
        for status in (403, 429):
            error = urllib.error.HTTPError(
                "https://stock.naver.com/api/domestic/detail/005930",
                status,
                "blocked",
                {},
                io.BytesIO(b"blocked"),
            )
            with (
                self.subTest(status=status),
                patch("urllib.request.urlopen", side_effect=error),
                self.assertRaisesRegex(RuntimeError, "Stop; do not retry automatically"),
            ):
                naverstock_api.request_json("/api/domestic/detail/005930")

    def test_wraps_url_and_timeout_errors(self) -> None:
        errors = (urllib.error.URLError("DNS failed"), socket.timeout("slow"))
        for error in errors:
            with (
                self.subTest(error=type(error).__name__),
                patch("urllib.request.urlopen", side_effect=error),
                self.assertRaises(RuntimeError),
            ):
                naverstock_api.request_json("/api/domestic/detail/005930")

    def test_wraps_invalid_json(self) -> None:
        response = unittest.mock.MagicMock()
        response.__enter__.return_value.read.return_value = b"not json"
        with (
            patch("urllib.request.urlopen", return_value=response),
            self.assertRaisesRegex(RuntimeError, "invalid JSON"),
        ):
            naverstock_api.request_json("/api/domestic/detail/005930")


class CommunityPrivacyTests(unittest.TestCase):
    def test_removes_profile_identifiers_and_redacts_contacts(self) -> None:
        payload = {
            "postId": "42",
            "author": {
                "nickname": "공개별명",
                "profileId": "private-123",
                "profileUrl": "https://example.test/profile/private-123",
                "authorProfileUuid": "also-private",
                "user_id": "private-user",
                "uuid": "nested-private",
                "uno": "nested-private-number",
                "image": "https://example.test/avatar.png",
            },
            "content": "연락: test@example.com, 010-1234-5678, https://example.test/me",
        }

        sanitized = discussion.sanitize_community_payload(payload)

        self.assertEqual(sanitized["postId"], "42")
        self.assertEqual(sanitized["author"], {"nickname": "공개별명"})
        self.assertEqual(
            sanitized["content"],
            "연락: [redacted-email], [redacted-phone], [redacted-url]",
        )

    def test_bounds_lists_depth_and_text(self) -> None:
        payload = {
            "items": list(range(discussion.MAX_COMMUNITY_ITEMS + 5)),
            "text": "x" * (discussion.MAX_COMMUNITY_TEXT_LENGTH + 1),
        }
        nested: dict[str, object] = payload
        for _ in range(discussion.MAX_COMMUNITY_DEPTH + 2):
            child: dict[str, object] = {}
            nested["nested"] = child
            nested = child

        sanitized = discussion.sanitize_community_payload(payload)

        self.assertEqual(len(sanitized["items"]), discussion.MAX_COMMUNITY_ITEMS)
        self.assertTrue(sanitized["text"].endswith("…[truncated]"))
        cursor = sanitized
        for _ in range(discussion.MAX_COMMUNITY_DEPTH):
            cursor = cursor["nested"]
        self.assertEqual(cursor, "[truncated]")

    def test_cli_sanitizes_output_and_rejects_oversized_page(self) -> None:
        payload = {"posts": [{"nickname": "공개별명", "profileId": "private"}]}
        stdout = io.StringIO()
        with (
            patch.object(sys, "argv", ["discussion.py", "popular-hot"]),
            patch.object(discussion, "request_json", return_value=payload),
            patch.object(sys, "stdout", stdout),
        ):
            discussion.main()
        self.assertEqual(json.loads(stdout.getvalue()), {"posts": [{"nickname": "공개별명"}]})

        with (
            patch.object(sys, "argv", ["discussion.py", "feed", "--page-size", "101"]),
            patch.object(sys, "stderr", io.StringIO()),
            self.assertRaises(SystemExit),
        ):
            discussion.main()

    def test_cli_rejects_path_like_post_identifier(self) -> None:
        with (
            patch.object(sys, "argv", ["discussion.py", "post", "--post-id", "../personal"]),
            patch.object(sys, "stderr", io.StringIO()),
            self.assertRaises(SystemExit),
        ):
            discussion.main()

    def test_cli_rejects_unsafe_cursor_and_invalid_date(self) -> None:
        argv_sets = (
            ["discussion.py", "feed", "--offset", "unsafe cursor"],
            ["discussion.py", "stats-by-items", "--start-date", "2026-02-30"],
        )
        for argv in argv_sets:
            with (
                self.subTest(argv=argv),
                patch.object(sys, "argv", argv),
                patch.object(sys, "stderr", io.StringIO()),
                self.assertRaises(SystemExit),
            ):
                discussion.main()


if __name__ == "__main__":
    unittest.main()
