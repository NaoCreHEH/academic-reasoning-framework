import json
import re
import unittest
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
PLUGIN = ROOT / "implementations" / "claude-code" / "arf-academic"
SKILLS = PLUGIN / "skills"
REFERENCES = PLUGIN / "references"
EXPECTED_SKILLS = {
    "uml-analysis",
    "architecture-review",
    "pfe-review",
    "exam-generation",
    "python-teaching",
}


def skill_text(identifier: str) -> str:
    return (SKILLS / identifier / "SKILL.md").read_text(encoding="utf-8")


def compact(text: str) -> str:
    return " ".join(text.split())


def frontmatter(text: str) -> dict[str, str]:
    self = text
    if not self.startswith("---\n"):
        return {}
    end = self.find("\n---\n", 4)
    if end == -1:
        return {}
    values: dict[str, str] = {}
    for line in self[4:end].splitlines():
        if ":" in line:
            key, value = line.split(":", 1)
            values[key.strip()] = value.strip()
    return values


class ClaudeCodePluginManifestTests(unittest.TestCase):
    def test_plugin_manifest_exists_and_parses(self) -> None:
        manifest = PLUGIN / ".claude-plugin" / "plugin.json"
        self.assertTrue(manifest.exists())
        data = json.loads(manifest.read_text(encoding="utf-8"))
        self.assertEqual(data["name"], "arf-academic")
        self.assertEqual(data["version"], "0.1.0")
        self.assertTrue(data["description"].strip())
        self.assertNotIn("skills", data)

    def test_claude_plugin_directory_contains_only_manifest(self) -> None:
        entries = sorted(path.name for path in (PLUGIN / ".claude-plugin").iterdir())
        self.assertEqual(entries, ["plugin.json"])


class ClaudeCodePluginSkillTests(unittest.TestCase):
    def test_exactly_five_skill_directories_exist(self) -> None:
        directories = {path.name for path in SKILLS.iterdir() if path.is_dir()}
        self.assertEqual(directories, EXPECTED_SKILLS)

    def test_each_skill_contains_skill_markdown(self) -> None:
        for identifier in EXPECTED_SKILLS:
            with self.subTest(skill=identifier):
                self.assertTrue((SKILLS / identifier / "SKILL.md").exists())

    def test_frontmatter_description_exists(self) -> None:
        for identifier in EXPECTED_SKILLS:
            with self.subTest(skill=identifier):
                data = frontmatter(skill_text(identifier))
                self.assertIn("description", data)
                self.assertTrue(data["description"].strip())

    def test_descriptions_are_unique(self) -> None:
        descriptions = [
            frontmatter(skill_text(identifier))["description"]
            for identifier in EXPECTED_SKILLS
        ]
        self.assertEqual(len(descriptions), len(set(descriptions)))

    def test_descriptions_are_not_generic_boilerplate(self) -> None:
        descriptions = [
            frontmatter(skill_text(identifier))["description"]
            for identifier in EXPECTED_SKILLS
        ]
        self.assertTrue(all(description.startswith("Use ") for description in descriptions))
        self.assertGreater(len({description[:80] for description in descriptions}), 1)

    def test_collision_boundary_phrases(self) -> None:
        self.assertRegex(
            frontmatter(skill_text("exam-generation"))["description"],
            r"MCQ|QCM",
        )
        self.assertIn(
            "exam-generation",
            skill_text("python-teaching"),
        )
        self.assertIn(
            "Do not use for UML diagram evaluation",
            skill_text("architecture-review"),
        )
        self.assertIn(
            "Do not use this skill for repository-wide",
            skill_text("uml-analysis"),
        )
        self.assertIn(
            "Do not use for repository code review solely because the code belongs to a student",
            compact(skill_text("pfe-review")),
        )

    def test_shared_references_exist_and_are_used(self) -> None:
        self.assertTrue((REFERENCES / "arf-reasoning-contract.md").exists())
        self.assertTrue((REFERENCES / "academic-levels.md").exists())
        for identifier in EXPECTED_SKILLS:
            text = skill_text(identifier)
            with self.subTest(skill=identifier):
                self.assertIn(
                    "${CLAUDE_PLUGIN_ROOT}/references/arf-reasoning-contract.md",
                    text,
                )
                self.assertIn(
                    "${CLAUDE_PLUGIN_ROOT}/references/academic-levels.md",
                    text,
                )

    def test_no_runtime_traversal_to_repository_rfcs(self) -> None:
        for identifier in EXPECTED_SKILLS:
            text = skill_text(identifier)
            with self.subTest(skill=identifier):
                self.assertNotIn("../", text)
                self.assertNotIn("rfcs/", text.lower())

    def test_plugin_root_references_exist(self) -> None:
        pattern = re.compile(r"\$\{CLAUDE_PLUGIN_ROOT\}/([^\s`)]+)")
        for identifier in EXPECTED_SKILLS:
            for match in pattern.finditer(skill_text(identifier)):
                with self.subTest(skill=identifier, reference=match.group(1)):
                    self.assertTrue((PLUGIN / match.group(1)).exists())

    def test_expert_prudence_phrases_preserved(self) -> None:
        self.assertIn("Do not transform every noun into a class", skill_text("uml-analysis"))
        self.assertIn(
            "Do not recommend inheritance merely to factor three attributes",
            compact(skill_text("uml-analysis")),
        )
        self.assertIn(
            "Do not confuse the quality of the company's project with the quality of the student's personal work",
            compact(skill_text("pfe-review")),
        )
        self.assertIn(
            "Do not propose object-oriented programming to learners who have not studied it",
            skill_text("python-teaching"),
        )
        self.assertIn(
            "Assessment output ownership applies even when the topic is Python",
            skill_text("exam-generation"),
        )
        self.assertIn(
            "Read actual files before judging coupling or cohesion",
            skill_text("architecture-review"),
        )


if __name__ == "__main__":
    unittest.main()
