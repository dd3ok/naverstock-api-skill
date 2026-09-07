from __future__ import annotations

import re
import unittest
from pathlib import Path
from urllib.parse import unquote, urlsplit


ROOT = Path(__file__).resolve().parents[1]


def markdown_prose(text: str) -> str:
    """Ignore fenced examples when inspecting this repo's inline links and ATX headings."""
    lines = []
    fence = None
    for line in text.splitlines():
        marker = re.match(r"^ {0,3}(`{3,}|~{3,})(.*)$", line)
        if fence is not None:
            if marker and marker[1][0] == fence[0] and len(marker[1]) >= len(fence):
                if not marker[2].strip():
                    fence = None
            continue
        if marker:
            fence = marker[1]
        else:
            lines.append(line)
    return "\n".join(lines)


def markdown_anchors(prose: str) -> set[str]:
    anchors: set[str] = set()
    for title in re.findall(r"^ {0,3}#{1,6}\s+(.+?)\s*$", prose, re.MULTILINE):
        title = re.sub(r"\s+#+\s*$", "", title)
        slug = re.sub(r"\s+", "-", re.sub(r"[^\w\- ]", "", title.strip().lower()))
        anchor = slug
        suffix = 0
        while anchor in anchors:
            suffix += 1
            anchor = f"{slug}-{suffix}"
        anchors.add(anchor)
    return anchors


class SkillPackageTests(unittest.TestCase):
    def test_local_markdown_links_and_anchors_exist(self) -> None:
        sources = [ROOT / "README.md", ROOT / "SKILL.md", *sorted(ROOT.glob("references/*.md"))]
        for source in sources:
            prose = markdown_prose(source.read_text(encoding="utf-8"))
            links = re.findall(
                r'!?\[[^\]\n]*\]\((?:<([^>\n]+)>|([^\s)]+))(?:\s+"[^\"]*")?\)', prose
            )
            for bracketed, plain in links:
                target = bracketed or plain
                parsed = urlsplit(target)
                if parsed.scheme or parsed.netloc:
                    continue
                linked = source.parent / unquote(parsed.path) if parsed.path else source
                with self.subTest(source=source.relative_to(ROOT), target=target):
                    self.assertTrue(linked.exists(), "Missing local link target")
                    if parsed.fragment:
                        self.assertTrue(linked.is_file())
                        self.assertEqual(linked.suffix.lower(), ".md")
                        self.assertIn(
                            unquote(parsed.fragment),
                            markdown_anchors(markdown_prose(linked.read_text(encoding="utf-8"))),
                            "Missing Markdown section anchor",
                        )

    def test_markdown_examples_do_not_hide_real_duplicate_or_korean_headings(self) -> None:
        prose = markdown_prose(
            "## 한글 제목\n```md\n## 숨김\n~~~\n```\n"
            "## 한글 제목\n~~~~\n## 숨김2\n~~~\n~~~~\n## Visible ###\n"
        )
        self.assertEqual(markdown_anchors(prose), {"한글-제목", "한글-제목-1", "visible"})

    def test_skill_frontmatter_and_openai_metadata(self) -> None:
        skill = (ROOT / "SKILL.md").read_text(encoding="utf-8")
        self.assertTrue(skill.startswith("---\n"))
        frontmatter = skill.split("---\n", 2)[1]
        self.assertRegex(frontmatter, r"(?m)^name: naverstock-web-api$")
        description = re.search(r"(?m)^description: (.+)$", frontmatter)
        self.assertIsNotNone(description)
        self.assertLessEqual(len(description.group(1)), 1024)
        self.assertTrue(description.group(1).startswith("Safely queries and audits "))
        self.assertIn("네이버증권", description.group(1))
        self.assertIn("Npay", description.group(1))
        self.assertIn("WiseReport v3", description.group(1))
        self.assertIn("funds", description.group(1))
        self.assertIn("mutation", description.group(1))

        metadata = (ROOT / "agents" / "openai.yaml").read_text(encoding="utf-8")
        self.assertIn('display_name: "네이버 증권 Web API"', metadata)
        self.assertIn("$naverstock-web-api", metadata)
        short_description = re.search(
            r'(?m)^  short_description: "(.+)"$', metadata
        )
        self.assertIsNotNone(short_description)
        self.assertGreaterEqual(len(short_description.group(1)), 25)
        self.assertLessEqual(len(short_description.group(1)), 64)
        for key in ("display_name", "short_description", "default_prompt"):
            self.assertRegex(metadata, rf'(?m)^  {key}: ".*"$')

    def test_references_are_directly_routed_and_long_docs_have_toc(self) -> None:
        skill = (ROOT / "SKILL.md").read_text(encoding="utf-8")
        references = sorted((ROOT / "references").glob("*.md"))
        self.assertGreaterEqual(len(references), 5)

        for path in references:
            relative = path.relative_to(ROOT).as_posix()
            self.assertIn(f"]({relative})", skill, relative)
            text = path.read_text(encoding="utf-8")
            if len(text.splitlines()) > 100:
                self.assertRegex(text, r"(?m)^## (목차|Contents)$", relative)

    def test_domain_catalogs_are_directly_routed_and_keep_index_small(self) -> None:
        skill = (ROOT / "SKILL.md").read_text(encoding="utf-8")
        index = (ROOT / "references" / "api-catalog.md").read_text(encoding="utf-8")
        domain_catalogs = sorted((ROOT / "references").glob("api-*.md"))
        domain_catalogs = [path for path in domain_catalogs if path.name != "api-catalog.md"]

        self.assertGreaterEqual(len(domain_catalogs), 5)
        self.assertLessEqual(len(index.splitlines()), 200)
        for path in domain_catalogs:
            relative = path.relative_to(ROOT).as_posix()
            self.assertIn(f"]({relative})", skill, relative)
            self.assertIn(f"]({path.name})", index, path.name)

    def test_every_script_routed_from_skill_exists(self) -> None:
        skill = (ROOT / "SKILL.md").read_text(encoding="utf-8")
        script_paths = set(re.findall(r"scripts/[A-Za-z0-9_]+\.py", skill))
        self.assertGreaterEqual(len(script_paths), 10)
        for relative in script_paths:
            self.assertTrue((ROOT / relative).is_file(), relative)

    def test_lightweight_install_resources_exist(self) -> None:
        for relative in ["SKILL.md", "LICENSE", "agents", "references", "scripts"]:
            self.assertTrue((ROOT / relative).exists(), relative)

    def test_external_source_docs_and_legacy_link_are_consistent(self) -> None:
        external = ROOT / "references" / "external-sources.md"
        self.assertTrue(external.is_file())
        combined = "\n".join(
            path.read_text(encoding="utf-8")
            for path in [ROOT / "SKILL.md", ROOT / "README.md", *ROOT.glob("references/*.md")]
        )
        self.assertNotIn("dd3ok/naverfinance-api-skills", combined)
        self.assertIn("dd3ok/naverfinance-api-skill", combined)


if __name__ == "__main__":
    unittest.main()
