#!/usr/bin/env python3
"""Safety boundary and community privacy regression tests."""

from __future__ import annotations

import io
import json
from email.message import Message
from pathlib import Path
import socket
import sys
import unittest
import urllib.error
import urllib.request
import urllib.response
from unittest.mock import patch

ROOT = Path(__file__).resolve().parents[1]
SCRIPTS = ROOT / "scripts"
sys.path.insert(0, str(SCRIPTS))

import discussion  # noqa: E402
import naverstock_api  # noqa: E402
import external_public  # noqa: E402


class PublicRequestBoundaryTests(unittest.TestCase):
    def test_normalize_item_code_accepts_ascii_etf_and_existing_stock_codes(self) -> None:
        cases = {
            "005930": "005930",
            "A005930": "005930",
            "a005930": "005930",
            "0193W0": "0193W0",
            " 0193w0 ": "0193W0",
            "0162z0": "0162Z0",
            "0177n0": "0177N0",
        }
        for value, expected in cases.items():
            with self.subTest(value=value):
                self.assertEqual(naverstock_api.normalize_item_code(value), expected)

    def test_normalize_item_code_rejects_path_and_non_domestic_values(self) -> None:
        self.assertEqual(naverstock_api.normalize_item_code("A005930"), "005930")
        self.assertEqual(naverstock_api.normalize_item_code("005930"), "005930")
        for value in [
            "../auth", "NVDA.O", "5930", "005930/price", "１２３４５６",
            "0193ß", "0193ﬀ", "0193ｗ0", "0193W0/../auth", "A0193W0", None,
        ]:
            with self.subTest(value=value), self.assertRaises(ValueError):
                naverstock_api.normalize_item_code(value)

    def test_allows_only_current_public_fund_detail_paths(self) -> None:
        allowed = (
            "/api/fund/funds/K55105B00244/left-panel",
            "/api/fund/funds/K55105B00244/base-price/chart?term=3m",
            "/api/fund/funds/K55105B00244/prices/daily?date=2026-08-13&size=10",
        )
        for path in allowed:
            with self.subTest(path=path):
                self.assertEqual(naverstock_api.validate_public_request(path), path)

        denied = (
            "/api/fund/funds?page=1&size=20",
            "/api/fund/funds/K55105B00244/arbitrary",
            "/api/fund/funds/K55105B00244/classes/fees",
        )
        for path in denied:
            with self.subTest(path=path), self.assertRaises(
                naverstock_api.RequestValidationError
            ):
                naverstock_api.validate_public_request(path)

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

    def test_allows_only_the_public_aggregate_mystock_ranking_shape(self) -> None:
        allowed = "/api/securityService/home/v3/mystock/ranking/005930"
        self.assertEqual(naverstock_api.validate_public_request(allowed), allowed)
        denied = (
            "/api/securityService/home/v3/mystock/summary",
            "/api/securityService/home/v3/mystock/ranking/005930/private",
        )
        for path in denied:
            with self.subTest(path=path), self.assertRaises(
                naverstock_api.RequestValidationError
            ):
                naverstock_api.validate_public_request(path)

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
            "/api/domestic//detail/005930",
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

    def test_rejects_research_view_tracking_get(self) -> None:
        paths = (
            "/api/stockSecurity/researches/v2/company/95415/view",
            "/api/stockSecurity/researches/v2/company/95415/view?recentNid=95301",
            "/api/stockSecurity/researches/v2/company/95415/view/",
            "/api/stockSecurity/researches/v2/company/95415//view",
            "/api/stockSecurity/researches/v2/company/95415/view//",
        )
        for path in paths:
            with self.subTest(path=path), self.assertRaises(
                naverstock_api.RequestValidationError
            ):
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


class RedirectTransportTests(unittest.TestCase):
    def test_redirects_never_send_a_destination_request(self) -> None:
        build_opener = urllib.request.build_opener

        class FakeHTTPS(urllib.request.HTTPSHandler):
            def __init__(self, status, destination):
                super().__init__()
                self.status = status
                self.destination = destination
                self.requests = []
                self.streams = []

            def https_open(self, request):
                self.requests.append(request.full_url)
                headers = Message()
                headers["Location"] = self.destination
                stream = io.BytesIO(b"moved")
                self.streams.append(stream)
                response = urllib.response.addinfourl(
                    stream, headers, request.full_url, self.status
                )
                response.msg = "Moved"
                return response

        for status in (301, 302, 303, 307, 308):
            for source in ("json-get", "json-post", "html"):
                transport = FakeHTTPS(
                    status,
                    "https://login.naver.com/"
                    if source == "html"
                    else "https://stock.naver.com/api/personal/users/holding/stocks",
                )

                def fake_opener(*handlers):
                    return build_opener(
                        *handlers, urllib.request.ProxyHandler({}), transport
                    )

                with (
                    self.subTest(status=status, source=source),
                    patch("socket.create_connection", side_effect=AssertionError("Network forbidden")),
                    patch("socket.getaddrinfo", side_effect=AssertionError("DNS forbidden")),
                    patch("urllib.request.build_opener", side_effect=fake_opener),
                    self.assertRaisesRegex(RuntimeError, "redirect") as raised,
                ):
                    if source == "html":
                        external_public.request_public_html(
                            "finance", "/sise/item_gold.naver", {"page": 1}
                        )
                    elif source == "json-post":
                        naverstock_api.request_json(
                            "/api/domestic/home/marketaggregate/aggregateInvestor",
                            method="POST",
                            body={"sections": {}},
                        )
                    else:
                        naverstock_api.request_json("/api/domestic/market/KRX/info")

                self.assertEqual(len(transport.requests), 1)
                self.assertTrue(all(stream.closed for stream in transport.streams))
                if source != "html":
                    self.assertEqual(raised.exception.status_code, status)


class RequestErrorTests(unittest.TestCase):
    def test_json_response_size_limit_and_stream_cleanup(self) -> None:
        class Response(io.BytesIO):
            def __init__(self, payload):
                super().__init__(payload)
                self.read_sizes = []

            def read(self, size=-1):
                self.read_sizes.append(size)
                return super().read(size)

        limit = naverstock_api.MAX_RESPONSE_BYTES
        for size in (limit, limit + 1):
            response = Response(b'{"value":"' + b"x" * (size - 12) + b'"}')
            with (
                self.subTest(size=size),
                patch.object(naverstock_api, "open_public_url", return_value=response),
            ):
                if size == limit:
                    result = naverstock_api.request_json("/api/domestic/market/KRX/info")
                    self.assertEqual(len(result["value"]), size - 12)
                else:
                    with self.assertRaisesRegex(naverstock_api.NaverStockAPIError, "response bytes") as raised:
                        naverstock_api.request_json("/api/domestic/market/KRX/info")
                    self.assertEqual(raised.exception.path, "/api/domestic/market/KRX/info")
            self.assertEqual(response.read_sizes, [limit + 1])
            self.assertTrue(response.closed)

    def test_http_error_diagnostic_is_bounded_and_closed(self) -> None:
        stream = io.BytesIO(b"x" * 4096)
        error = urllib.error.HTTPError("https://stock.naver.com/", 404, "missing", {}, stream)
        with (
            patch.object(naverstock_api, "open_public_url", side_effect=error),
            self.assertRaises(naverstock_api.NaverStockAPIError) as raised,
        ):
            naverstock_api.request_json("/api/domestic/market/KRX/info")
        self.assertEqual(raised.exception.status_code, 404)
        self.assertEqual(len(raised.exception.detail), naverstock_api.MAX_ERROR_BYTES)
        self.assertTrue(stream.closed)

    def test_http_error_read_failure_keeps_status_and_closes_stream(self) -> None:
        class FailedBody(io.BytesIO):
            def read(self, size=-1):
                raise OSError("response connection failed")

        stream = FailedBody()
        error = urllib.error.HTTPError("https://stock.naver.com/", 429, "blocked", {}, stream)
        with (
            patch.object(naverstock_api, "open_public_url", side_effect=error),
            self.assertRaises(naverstock_api.NaverStockAPIError) as raised,
        ):
            naverstock_api.request_json("/api/domestic/market/KRX/info")
        self.assertEqual(raised.exception.status_code, 429)
        self.assertIn("Stop; do not retry automatically", str(raised.exception))
        self.assertTrue(stream.closed)

    def test_json_error_payload_has_bounded_diagnostic(self) -> None:
        response = io.BytesIO(json.dumps({"error": "x" * 4096, "statusCode": 400}).encode())
        with (
            patch.object(naverstock_api, "open_public_url", return_value=response),
            self.assertRaises(naverstock_api.NaverStockAPIError) as raised,
        ):
            naverstock_api.request_json("/api/domestic/market/KRX/info")
        self.assertEqual(raised.exception.status_code, 400)
        self.assertEqual(len(raised.exception.detail), naverstock_api.MAX_ERROR_BYTES)
        self.assertTrue(response.closed)

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
                patch("naverstock_api.open_public_url", side_effect=error),
                self.assertRaisesRegex(RuntimeError, "Stop; do not retry automatically"),
            ):
                naverstock_api.request_json("/api/domestic/detail/005930")

    def test_wraps_url_and_timeout_errors(self) -> None:
        errors = (urllib.error.URLError("DNS failed"), socket.timeout("slow"))
        for error in errors:
            with (
                self.subTest(error=type(error).__name__),
                patch("naverstock_api.open_public_url", side_effect=error),
                self.assertRaises(RuntimeError),
            ):
                naverstock_api.request_json("/api/domestic/detail/005930")

    def test_wraps_invalid_json(self) -> None:
        response = unittest.mock.MagicMock()
        response.__enter__.return_value.read.return_value = b"not json"
        with (
            patch("naverstock_api.open_public_url", return_value=response),
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
            "content": (
                "연락: test@example.com, 010-1234-5678, +1 415-555-2671, "
                "https://example.test/me"
            ),
        }

        sanitized = discussion.sanitize_community_payload(payload)

        self.assertEqual(sanitized["postId"], "42")
        self.assertEqual(sanitized["author"], {"nickname": "공개별명"})
        self.assertEqual(
            sanitized["content"],
            (
                "연락: [redacted-email], [redacted-phone], [redacted-phone], "
                "[redacted-url]"
            ),
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
