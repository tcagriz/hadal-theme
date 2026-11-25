#!/usr/bin/env python3
"""Regression tests for the palette schema and generated theme outputs."""

from copy import deepcopy
import importlib.util
import json
from pathlib import Path
import unittest


ROOT = Path(__file__).resolve().parents[1]
SPEC = importlib.util.spec_from_file_location("hadal_build", ROOT / "scripts" / "build.py")
assert SPEC and SPEC.loader
BUILD = importlib.util.module_from_spec(SPEC)
SPEC.loader.exec_module(BUILD)

EXPECTED_OUTPUTS = {
    "inkdrop/styles/palette.css",
    "vscode/themes/hadal-color-theme.json",
    "zed/themes/hadal.json",
    "neovim/lua/hadal/palette.lua",
    "herdr-app/hadal.json",
    "wezterm/hadal.lua",
    "ghostty/hadal",
    "cmux/hadal.json",
    "opencode/hadal.json",
    "opencode/v1/hadal.json",
    "tmux/hadal.conf",
    "starship/hadal.toml",
    "zsh/hadal.zsh",
    "herdr-tui/theme.toml",
    "lsd/colors.yaml",
    "lazygit/config.yml",
}


def valid_palette():
    return deepcopy(json.loads(BUILD.PALETTE_PATH.read_text()))


def normalized_palette():
    palette = valid_palette()
    index = 0

    def normalize(value):
        nonlocal index
        if isinstance(value, dict):
            return {key: normalize(item) for key, item in value.items()}
        if isinstance(value, list):
            return [normalize(item) for item in value]
        if isinstance(value, str) and value.startswith("#"):
            index += 1
            return f"#{(0x102030 + index * 0x010101) & 0xFFFFFF:06x}"
        return value

    return normalize(palette)


class PaletteSchemaTest(unittest.TestCase):
    def assert_invalid(self, palette, message):
        with self.assertRaisesRegex(BUILD.PaletteError, message):
            BUILD.validate_palette(palette)

    def test_current_palette_is_valid(self):
        palette = valid_palette()
        self.assertIs(BUILD.validate_palette(palette), palette)

    def test_top_level_keys_are_exact(self):
        palette = valid_palette()
        del palette["status"]
        self.assert_invalid(palette, "missing status")

        palette = valid_palette()
        palette["custom"] = {}
        self.assert_invalid(palette, "unexpected custom")

    def test_role_keys_are_exact(self):
        palette = valid_palette()
        del palette["core"]["cursor"]
        self.assert_invalid(palette, r"core roles: missing cursor")

        palette = valid_palette()
        palette["syntax"]["custom"] = "#123456"
        self.assert_invalid(palette, r"syntax roles: unexpected custom")

    def test_ansi_has_exactly_sixteen_colors(self):
        palette = valid_palette()
        palette["ansi"].pop()
        self.assert_invalid(palette, r"ansi must contain exactly 16 colors, got 15")

        palette = valid_palette()
        palette["ansi"].append("#123456")
        self.assert_invalid(palette, r"ansi must contain exactly 16 colors, got 17")

        palette = valid_palette()
        palette["ansi"] = "not-a-list"
        self.assert_invalid(palette, "ansi must be a list")

    def test_colors_are_six_digit_hex(self):
        for invalid in ("123456", "#12345", "#1234567", "#gggggg", 123456, None):
            with self.subTest(invalid=invalid):
                palette = valid_palette()
                palette["ui"]["accent"] = invalid
                self.assert_invalid(palette, r"ui\.accent must be a #RRGGBB color")

    def test_name_is_non_empty(self):
        for invalid in ("", "   ", None, 42):
            with self.subTest(invalid=invalid):
                palette = valid_palette()
                palette["name"] = invalid
                self.assert_invalid(palette, "name must be a non-empty string")


class GeneratorTest(unittest.TestCase):
    def setUp(self):
        self.original = valid_palette()

    def tearDown(self):
        BUILD.set_palette(self.original)

    def test_output_map_coverage_is_explicit(self):
        self.assertEqual(set(BUILD.OUTPUTS), EXPECTED_OUTPUTS)
        self.assertEqual(len(BUILD.OUTPUTS), len(EXPECTED_OUTPUTS))

    def test_every_generator_is_deterministic_and_byte_stable(self):
        BUILD.set_palette(normalized_palette())

        for relative_path, generator in BUILD.OUTPUTS.items():
            with self.subTest(output=relative_path):
                first = generator()
                second = generator()
                self.assertIsInstance(first, str)
                self.assertEqual(first, second)
                self.assertTrue(first.endswith("\n"))
                self.assertEqual(first.encode("utf-8"), second.encode("utf-8"))

    def test_current_outputs_match_every_generator(self):
        for relative_path, generator in BUILD.OUTPUTS.items():
            with self.subTest(output=relative_path):
                path = ROOT / relative_path
                self.assertTrue(path.is_file(), f"missing generated file: {relative_path}")
                self.assertEqual(path.read_text(), generator())


if __name__ == "__main__":
    unittest.main()
