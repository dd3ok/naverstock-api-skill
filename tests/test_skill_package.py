from __future__ import annotations

import re
import unittest
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]


class SkillPackageTests(unittest.TestCase):
    def test_skill_frontmatter_and_openai_metadata(self) -> None:
        skill = (ROOT / "SKILL.md").read_text(encoding="utf-8")
        self.assertTrue(skill.startswith("---\n"))
        frontmatter = skill.split("---\n", 2)[1]
        self.assertRegex(frontmatter, r"(?m)^name: naverstock-web-api$")
        description = re.search(r"(?m)^description: (.+)$", frontmatter)
        self.assertIsNotNone(description)
        self.assertLessEqual(len(description.group(1)), 1024)

        metadata = (ROOT / "agents" / "openai.yaml").read_text(encoding="utf-8")
        self.assertIn('display_name: "Npay 증권 Web API"', metadata)
        self.assertIn("$naverstock-web-api", metadata)

    def test_every_script_routed_from_skill_exists(self) -> None:
        skill = (ROOT / "SKILL.md").read_text(encoding="utf-8")
        script_paths = set(re.findall(r"scripts/[A-Za-z0-9_]+\.py", skill))
        self.assertGreaterEqual(len(script_paths), 10)
        for relative in script_paths:
            self.assertTrue((ROOT / relative).is_file(), relative)

    def test_lightweight_install_resources_exist(self) -> None:
        for relative in ["SKILL.md", "LICENSE", "agents", "references", "scripts"]:
            self.assertTrue((ROOT / relative).exists(), relative)


if __name__ == "__main__":
    unittest.main()
