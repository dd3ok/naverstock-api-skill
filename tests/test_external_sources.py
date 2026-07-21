from __future__ import annotations

import argparse
from email.message import Message
from io import BytesIO, StringIO
import sys
import unittest
from pathlib import Path
from unittest.mock import MagicMock, patch
from urllib.error import HTTPError


ROOT = Path(__file__).resolve().parents[1]
SCRIPTS = ROOT / "scripts"
sys.path.insert(0, str(SCRIPTS))

import external_public  # noqa: E402
import legacy_screeners  # noqa: E402
import wisereport  # noqa: E402


class ExternalPublicBoundaryTests(unittest.TestCase):
    def test_wisereport_url_is_narrow_and_normalizes_code(self) -> None:
        url = external_public.build_external_url(
            "wisereport",
            external_public.WISEREPORT_COMPANY_PATHS["status"],
            {"cmp_cd": "A005930"},
        )

        self.assertEqual(
            url,
            "https://navercomp.wisereport.co.kr/v3/company/c1010001.aspx?cmp_cd=005930",
        )

    def test_rejects_unknown_host_path_and_query(self) -> None:
        cases = (
            ("unknown", "/v3/company/c1010001.aspx", {"cmp_cd": "005930"}),
            ("wisereport", "/v3/company/private.aspx", {"cmp_cd": "005930"}),
            (
                "wisereport",
                external_public.WISEREPORT_COMPANY_PATHS["status"],
                {"account": "123"},
            ),
        )
        for source, path, params in cases:
            with self.subTest(source=source, path=path), self.assertRaises(
                external_public.ExternalRequestValidationError
            ):
                external_public.build_external_url(source, path, params)

    def test_finance_screener_url_accepts_only_page_and_market(self) -> None:
        url = external_public.build_external_url(
            "finance",
            external_public.FINANCE_PRICE_POSITION_PATHS["low-up"],
            {"page": 2, "sosok": "1"},
        )

        self.assertEqual(
            url,
            "https://finance.naver.com/sise/sise_low_up.naver?page=2&sosok=1",
        )
        with self.assertRaises(external_public.ExternalRequestValidationError):
            external_public.build_external_url(
                "finance",
                external_public.FINANCE_PRICE_POSITION_PATHS["low-up"],
                {"market": "KOSDAQ"},
            )

    def test_rejects_redirect(self) -> None:
        response = MagicMock()
        response.__enter__.return_value = response
        response.geturl.return_value = "https://login.naver.com/"
        response.headers = Message()

        with (
            patch.object(external_public.urllib.request, "urlopen", return_value=response),
            self.assertRaises(external_public.ExternalPublicError),
        ):
            external_public.request_public_html(
                "wisereport",
                external_public.WISEREPORT_COMPANY_PATHS["status"],
                {"cmp_cd": "005930"},
            )

    def test_rejects_oversized_response(self) -> None:
        requested_url = (
            "https://navercomp.wisereport.co.kr/v3/company/"
            "c1010001.aspx?cmp_cd=005930"
        )
        response = MagicMock()
        response.__enter__.return_value = response
        response.geturl.return_value = requested_url
        response.read.return_value = b"x" * (external_public.MAX_RESPONSE_BYTES + 1)
        response.headers = Message()

        with (
            patch.object(external_public.urllib.request, "urlopen", return_value=response),
            self.assertRaises(external_public.ExternalPublicError),
        ):
            external_public.request_public_html(
                "wisereport",
                external_public.WISEREPORT_COMPANY_PATHS["status"],
                {"cmp_cd": "005930"},
            )

    def test_stops_on_rate_limit(self) -> None:
        error = HTTPError(
            "https://navercomp.wisereport.co.kr/v3/company/c1010001.aspx",
            429,
            "Too Many Requests",
            hdrs=None,
            fp=BytesIO(b"rate limited"),
        )

        with (
            patch.object(external_public.urllib.request, "urlopen", side_effect=error),
            self.assertRaisesRegex(
                external_public.ExternalPublicError,
                "Stop; do not retry automatically",
            ),
        ):
            external_public.request_public_html(
                "wisereport",
                external_public.WISEREPORT_COMPANY_PATHS["status"],
                {"cmp_cd": "005930"},
            )

    def test_rejects_non_html_response(self) -> None:
        requested_url = (
            "https://navercomp.wisereport.co.kr/v3/company/"
            "c1010001.aspx?cmp_cd=005930"
        )
        response = MagicMock()
        response.__enter__.return_value = response
        response.geturl.return_value = requested_url
        response.read.return_value = b"{}"
        response.headers = Message()
        response.headers["Content-Type"] = "application/json"

        with (
            patch.object(external_public.urllib.request, "urlopen", return_value=response),
            self.assertRaisesRegex(
                external_public.ExternalPublicError, "unexpected content type"
            ),
        ):
            external_public.request_public_html(
                "wisereport",
                external_public.WISEREPORT_COMPANY_PATHS["status"],
                {"cmp_cd": "005930"},
            )

    def test_nested_tables_are_bounded_and_preserved_separately(self) -> None:
        markup = "<table id='outer'><tr><td>A<table id='inner'><tr><td>B</td></tr></table></td></tr></table>"

        tables = external_public.extract_tables(markup)

        self.assertEqual([table["attrs"]["id"] for table in tables], ["inner", "outer"])
        self.assertEqual(tables[0]["rows"], [["B"]])
        self.assertEqual(tables[1]["rows"], [["A"]])


class WiseReportTests(unittest.TestCase):
    def test_company_analysis_uses_v3_and_preserves_raw_rows(self) -> None:
        args = argparse.Namespace(
            code="A005930",
            kind="status",
            max_tables=2,
            max_rows=2,
        )
        markup = """
        <html><head><title>기업개요(삼성전자)</title></head><body>
        <li class="dot_cmp">요약 문장</li>
        <table id="first" class="gHead"><tr><th>항목</th><th>값</th></tr><tr><td>주가</td><td>100</td></tr></table>
        <table id="second"><tr><td>A</td></tr><tr><td>B</td></tr><tr><td>C</td></tr></table>
        </body></html>
        """

        with patch.object(wisereport, "request_public_html", return_value=markup) as request_html:
            result = wisereport.fetch_company_analysis(args)

        request_html.assert_called_once_with(
            "wisereport",
            "/v3/company/c1010001.aspx",
            {"cmp_cd": "005930"},
        )
        self.assertEqual(result["title"], "기업개요(삼성전자)")
        self.assertEqual(result["summaryBullets"], ["요약 문장"])
        self.assertEqual(result["tables"][0]["rows"][1], ["주가", "100"])
        self.assertEqual(result["tables"][1]["rows"], [["A"], ["B"]])
        self.assertTrue(result["tables"][1]["truncated"])


class LegacyScreenerTests(unittest.TestCase):
    PRICE_MARKUP = """
    <table class="type_2">
      <tr><th>N</th><th>등락률</th><th>종목명</th><th>현재가</th><th>등락률</th></tr>
      <tr><td>1</td><td>41.11%</td><td><a href="/item/main.naver?code=123456">테스트</a></td><td>127</td><td>+29.59%</td></tr>
    </table>
    """

    def test_price_position_preserves_both_change_rate_columns(self) -> None:
        args = argparse.Namespace(
            kind="low-up", market="KOSDAQ", page=2, limit=20
        )

        with patch.object(
            legacy_screeners, "request_public_html", return_value=self.PRICE_MARKUP
        ) as request_html:
            result = legacy_screeners.fetch_price_position(args)

        request_html.assert_called_once_with(
            "finance", "/sise/sise_low_up.naver", {"page": 2, "sosok": "1"}
        )
        self.assertEqual(result["market"], "KOSDAQ")
        self.assertEqual(result["rows"][0]["저가대비등락률"], "41.11%")
        self.assertEqual(result["rows"][0]["등락률"], "+29.59%")
        self.assertEqual(result["rows"][0]["종목코드"], "123456")

    def test_technical_does_not_send_silently_ignored_market(self) -> None:
        args = argparse.Namespace(kind="golden-cross", page=1, limit=20)
        markup = """
        <table class="type_5">
          <tr><th>N</th><th>종목명</th><th>현재가</th></tr>
          <tr><td>1</td><td>테스트</td><td>100</td></tr>
        </table>
        """

        with patch.object(
            legacy_screeners, "request_public_html", return_value=markup
        ) as request_html:
            result = legacy_screeners.fetch_technical(args)

        request_html.assert_called_once_with(
            "finance", "/sise/item_gold.naver", {"page": 1}
        )
        self.assertNotIn("market", result)

    def test_technical_cli_rejects_market_argument(self) -> None:
        with (
            patch.object(
                sys,
                "argv",
                [
                    "legacy_screeners.py",
                    "technical",
                    "golden-cross",
                    "--market",
                    "KOSPI",
                ],
            ),
            patch("sys.stderr", new_callable=StringIO),
            self.assertRaises(SystemExit),
        ):
            legacy_screeners.main()


if __name__ == "__main__":
    unittest.main()
