from __future__ import annotations

from io import StringIO
from pathlib import Path
import sys
import unittest
from unittest.mock import patch


SCRIPTS_DIR = Path(__file__).resolve().parents[1] / "scripts"
sys.path.insert(0, str(SCRIPTS_DIR))

import news  # noqa: E402
import research  # noqa: E402
import stock_detail_pages  # noqa: E402


class PathIdentifierTests(unittest.TestCase):
    def test_path_ids_accept_observed_numeric_shapes(self) -> None:
        self.assertEqual(news._numeric_id("2580641"), "2580641")
        self.assertEqual(research._numeric_id("91965"), "91965")
        self.assertEqual(stock_detail_pages._numeric_article_id("123"), "123")

    def test_path_ids_reject_separators_and_query_injection(self) -> None:
        cases = [
            (news, ["news.py", "world-detail", "--article-id", "../auth"]),
            (research, ["research.py", "detail", "--research-id", "1?userId=2"]),
            (
                stock_detail_pages,
                [
                    "stock_detail_pages.py",
                    "ir-detail",
                    "--code",
                    "005930",
                    "--article-id",
                    "1/../../auth",
                ],
            ),
        ]
        for module, argv in cases:
            with self.subTest(argv=argv):
                with patch.object(sys, "argv", argv), patch("sys.stderr", new_callable=StringIO):
                    with self.assertRaises(SystemExit):
                        module.main()


if __name__ == "__main__":
    unittest.main()
