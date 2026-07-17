from __future__ import annotations

import argparse
from io import StringIO
import sys
import unittest
from pathlib import Path
from unittest.mock import patch


SCRIPTS_DIR = Path(__file__).resolve().parents[1] / "scripts"
sys.path.insert(0, str(SCRIPTS_DIR))

import search  # noqa: E402


class SearchTests(unittest.TestCase):
    def test_autocomplete_uses_all_public_targets_by_default(self) -> None:
        args = argparse.Namespace(query="삼성전자", target=None)

        with patch.object(search, "request_json", return_value={}) as request_json:
            search.fetch_autocomplete(args)

        request_json.assert_called_once_with(
            "/api/autocomplete/search/autoComplete?query=%EC%82%BC%EC%84%B1%EC%A0%84%EC%9E%90&target=stock%2Cindex%2Cmarketindicator%2Ccoin%2Cipo%2Cfund"
        )

    def test_full_search_is_one_based_and_bounded(self) -> None:
        args = argparse.Namespace(query="삼성전자", target=["stock"], size=30, page=1)

        with patch.object(search, "request_json", return_value={}) as request_json:
            search.fetch_search(args)

        request_json.assert_called_once_with(
            "/api/autocomplete/search?q=%EC%82%BC%EC%84%B1%EC%A0%84%EC%9E%90&target=stock&size=30&page=1"
        )

    def test_cli_rejects_recent_history_command(self) -> None:
        with (
            patch.object(sys, "argv", ["search.py", "recent"]),
            patch("sys.stderr", new_callable=StringIO),
        ):
            with self.assertRaises(SystemExit):
                search.main()

    def test_cli_rejects_oversized_page(self) -> None:
        with (
            patch.object(sys, "argv", ["search.py", "search", "--query", "삼성", "--page", "1000"]),
            patch("sys.stderr", new_callable=StringIO),
        ):
            with self.assertRaises(SystemExit):
                search.main()


if __name__ == "__main__":
    unittest.main()
