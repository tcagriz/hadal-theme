#!/usr/bin/env python3
"""Failure-path tests for the Zed extension package contract."""

from copy import deepcopy
import importlib.util
import json
from pathlib import Path
import shutil
import tempfile
import unittest


ROOT = Path(__file__).resolve().parents[1]
SPEC = importlib.util.spec_from_file_location(
    "check_zed_extension", ROOT / "tests" / "check_extension.py"
)
assert SPEC and SPEC.loader
CHECK = importlib.util.module_from_spec(SPEC)
SPEC.loader.exec_module(CHECK)


class ZedExtensionTest(unittest.TestCase):
    def setUp(self):
        self.temp = tempfile.TemporaryDirectory(prefix="hadal-zed-test-")
        self.root = Path(self.temp.name) / "zed"
        self.root.mkdir()
        for relative in ("extension.toml", "themes/hadal.json", "LICENSE", "README.md"):
            source = ROOT / relative
            target = self.root / relative
            target.parent.mkdir(parents=True, exist_ok=True)
            shutil.copy2(source, target)
        (self.root / ".github" / "workflows").mkdir(parents=True)
        (self.root / ".github" / "dependabot.yml").write_text("version: 2\nupdates: []\n")
        (self.root / ".github" / "workflows" / "check.yml").write_text(
            "name: Check\non: [push]\njobs: {}\n"
        )

    def tearDown(self):
        self.temp.cleanup()

    def assert_invalid(self, message):
        with self.assertRaisesRegex(CHECK.ZedExtensionError, message):
            manifest = CHECK.validate_manifest(self.root / "extension.toml")
            CHECK.validate_theme(self.root / "themes" / "hadal.json", manifest)
            CHECK.expected_files(self.root)

    def test_current_package_is_valid(self):
        cache = self.root / "tests" / "__pycache__"
        cache.mkdir(parents=True)
        (cache / "stale.pyc").write_bytes(b"not package content")
        manifest = CHECK.validate_manifest(self.root / "extension.toml")
        CHECK.validate_theme(self.root / "themes" / "hadal.json", manifest)
        output = Path(self.temp.name) / "hadal-zed.tar.gz"
        CHECK.package_extension(self.root, output)
        CHECK.inspect_package(self.root, output)
        self.assertNotIn(
            "tests/__pycache__/stale.pyc",
            [str(path.relative_to(self.root)) for path in CHECK.expected_files(self.root)],
        )

    def test_invalid_manifest_fails(self):
        (self.root / "extension.toml").write_text('id = "hadal\\n')
        with self.assertRaisesRegex(CHECK.ZedExtensionError, "invalid"):
            CHECK.validate_manifest(self.root / "extension.toml")

        (self.root / "extension.toml").write_text(
            (ROOT / "extension.toml").read_text().replace('version = "0.1.0"', 'version = "bad"')
        )
        self.assert_invalid("version must be semver")

    def test_missing_manifest_field_fails(self):
        manifest = (ROOT / "extension.toml").read_text()
        (self.root / "extension.toml").write_text(
            "\n".join(line for line in manifest.splitlines() if not line.startswith("repository ="))
        )
        self.assert_invalid("missing: repository")

    def test_invalid_theme_json_fails(self):
        (self.root / "themes" / "hadal.json").write_text("{")
        with self.assertRaisesRegex(CHECK.ZedExtensionError, "invalid"):
            CHECK.validate_theme(
                self.root / "themes" / "hadal.json",
                CHECK.validate_manifest(self.root / "extension.toml"),
            )

    def test_wrong_theme_schema_fails(self):
        theme = json.loads((self.root / "themes" / "hadal.json").read_text())
        theme["$schema"] = "https://example.invalid/schema.json"
        (self.root / "themes" / "hadal.json").write_text(json.dumps(theme))
        self.assert_invalid("theme schema must be")

    def test_invalid_theme_color_fails(self):
        theme = json.loads((self.root / "themes" / "hadal.json").read_text())
        theme["themes"][0]["style"]["background"] = "not-a-color"
        (self.root / "themes" / "hadal.json").write_text(json.dumps(theme))
        self.assert_invalid("must be #RRGGBB")

    def test_missing_license_fails(self):
        (self.root / "LICENSE").unlink()
        with self.assertRaisesRegex(CHECK.ZedExtensionError, "missing package files"):
            CHECK.expected_files(self.root)

    def test_missing_manifest_theme_name_match_fails(self):
        theme = json.loads((self.root / "themes" / "hadal.json").read_text())
        theme["themes"][0]["name"] = "Other"
        (self.root / "themes" / "hadal.json").write_text(json.dumps(theme))
        self.assert_invalid("theme entry name must match")


if __name__ == "__main__":
    unittest.main()
