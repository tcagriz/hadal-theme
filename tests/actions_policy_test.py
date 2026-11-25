#!/usr/bin/env python3
"""Verify that workflow actions are pinned to reviewed Node 24 revisions."""

from pathlib import Path
import re
import unittest


ROOT = Path(__file__).resolve().parents[1]
WORKFLOWS = sorted(
    path
    for path in ROOT.rglob("*.yml")
    if ".github/workflows" in path.as_posix()
)
APPROVED = {
    "actions/checkout": (
        "3d3c42e5aac5ba805825da76410c181273ba90b1",
        "v7.0.1",
    ),
    "actions/setup-python": (
        "6d4fd22b20465ccc0f7354476588e8df7c9ca0e0",
        "v7.1.0",
    ),
    "actions/setup-node": (
        "949feb2413d6458794dcd2491c4babbbce0c15c1",
        "v7.1.0",
    ),
    "actions/upload-artifact": (
        "cf430e030ddbb5b0abf93d22962f4752f3646cd9",
        "v7.0.2",
    ),
    "actions/download-artifact": (
        "9000827ccba6bdab643e8b6fd33ac0654aef8333",
        "v8.0.2",
    ),
}
DEPENDABOT = {
    ROOT / ".github" / "dependabot.yml": {
        ("github-actions", "/"),
        ("npm", "/inkdrop"),
    },
    ROOT / "vscode" / ".github" / "dependabot.yml": {
        ("github-actions", "/"),
    },
    ROOT / "inkdrop" / ".github" / "dependabot.yml": {
        ("github-actions", "/"),
        ("npm", "/"),
    },
    ROOT / "zed" / ".github" / "dependabot.yml": {
        ("github-actions", "/"),
    },
    ROOT / "neovim" / ".github" / "dependabot.yml": {
        ("github-actions", "/"),
    },
}


class ActionsPolicyTest(unittest.TestCase):
    def test_every_workflow_action_is_an_approved_full_sha(self):
        refs = []
        for workflow in WORKFLOWS:
            text = workflow.read_text()
            for action, revision, comment in re.findall(
                r"uses:\s*([A-Za-z0-9_.-]+/[A-Za-z0-9_.-]+)@([A-Za-z0-9_.-]+)"
                r"(?:\s+#\s*([^\s]+))?",
                text,
            ):
                refs.append((workflow, action, revision, comment))

        self.assertTrue(refs, "no workflow actions found")
        for workflow, action, revision, comment in refs:
            with self.subTest(workflow=workflow, action=action):
                self.assertIn(action, APPROVED)
                approved_sha, version = APPROVED[action]
                self.assertRegex(revision, r"^[0-9a-f]{40}$")
                self.assertEqual(revision, approved_sha)
                self.assertEqual(comment, version)

    def test_all_current_workflows_use_the_latest_approved_runtime(self):
        used = {
            action
            for workflow in WORKFLOWS
            for action in re.findall(
                r"uses:\s*([A-Za-z0-9_.-]+/[A-Za-z0-9_.-]+)@",
                workflow.read_text(),
            )
        }
        self.assertEqual(used, set(APPROVED))

    def test_dependabot_covers_every_supported_tree(self):
        for path, expected in DEPENDABOT.items():
            with self.subTest(path=path):
                self.assertTrue(path.is_file(), f"missing {path.relative_to(ROOT)}")
                text = path.read_text()
                ecosystems = re.findall(
                    r"- package-ecosystem:\s*([^\s]+)\s*\n"
                    r"\s+directory:\s*([^\s]+)",
                    text,
                )
                self.assertEqual(set(ecosystems), expected)
                self.assertTrue(text.startswith("version: 2\nupdates:\n"))
                self.assertIn("interval: weekly", text)


if __name__ == "__main__":
    unittest.main()
