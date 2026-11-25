#!/usr/bin/env python3
"""Generate the color-only theme files from palette/palette.json.

Usage:
  python3 scripts/build.py          write the generated files
  python3 scripts/build.py --check  exit 1 if a generated file is out of date
"""
import json
import re
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
PALETTE_PATH = ROOT / "palette" / "palette.json"
HEX_COLOR = re.compile(r"#[0-9a-fA-F]{6}")
PALETTE_KEYS = {"name", "core", "ansi", "ui", "syntax", "tints", "status"}
ROLE_KEYS = {
    "core": {"bg", "fg", "selection", "cursor"},
    "ui": {
        "side", "canvas", "line", "popover", "raised", "hover", "active",
        "border", "input", "dim", "comment", "accent", "focus", "solid",
    },
    "syntax": {
        "string", "number", "builtin", "func", "orange", "error", "rosewater",
        "fg_bright", "keyword", "type", "invalid", "add",
    },
    "tints": {
        "error_bg", "warn_bg", "info_bg", "hint_bg", "diff_add",
        "diff_change", "diff_delete", "diff_text",
    },
    "status": {"working", "blocked", "done", "idle", "unknown"},
}


class PaletteError(ValueError):
    """The palette is missing required roles or contains invalid values."""


def validate_palette(palette):
    if not isinstance(palette, dict):
        raise PaletteError("palette must be a JSON object")

    actual_keys = set(palette)
    missing = PALETTE_KEYS - actual_keys
    extra = actual_keys - PALETTE_KEYS
    if missing or extra:
        details = []
        if missing:
            details.append("missing " + ", ".join(sorted(missing)))
        if extra:
            details.append("unexpected " + ", ".join(sorted(extra)))
        raise PaletteError("palette keys: " + "; ".join(details))

    if not isinstance(palette["name"], str) or not palette["name"].strip():
        raise PaletteError("name must be a non-empty string")

    ansi_colors = palette["ansi"]
    if not isinstance(ansi_colors, list):
        raise PaletteError("ansi must be a list")
    if len(ansi_colors) != 16:
        raise PaletteError(f"ansi must contain exactly 16 colors, got {len(ansi_colors)}")

    for role_group, expected in ROLE_KEYS.items():
        values = palette[role_group]
        if not isinstance(values, dict):
            raise PaletteError(f"{role_group} must be a JSON object")
        actual = set(values)
        missing_roles = expected - actual
        extra_roles = actual - expected
        if missing_roles or extra_roles:
            details = []
            if missing_roles:
                details.append("missing " + ", ".join(sorted(missing_roles)))
            if extra_roles:
                details.append("unexpected " + ", ".join(sorted(extra_roles)))
            raise PaletteError(f"{role_group} roles: " + "; ".join(details))

        for role, color in values.items():
            validate_color(f"{role_group}.{role}", color)

    for index, color in enumerate(ansi_colors):
        validate_color(f"ansi[{index}]", color)

    return palette


def validate_color(name, color):
    if not isinstance(color, str) or HEX_COLOR.fullmatch(color) is None:
        raise PaletteError(f"{name} must be a #RRGGBB color, got {color!r}")


def set_palette(palette):
    global P, core, ansi, ui, syn, status
    global BG, FG, BLACK, RED, GREEN, YELLOW, BLUE, MAGENTA, CYAN, WHITE
    global B_BLACK, B_RED, B_GREEN, B_YELLOW, B_BLUE, B_MAGENTA, B_CYAN, B_WHITE

    P = validate_palette(palette)
    core, ansi, ui, syn, status = (
        P["core"], P["ansi"], P["ui"], P["syntax"], P["status"]
    )
    BG, FG = core["bg"], core["fg"]
    (
        BLACK, RED, GREEN, YELLOW, BLUE, MAGENTA, CYAN, WHITE,
        B_BLACK, B_RED, B_GREEN, B_YELLOW, B_BLUE, B_MAGENTA, B_CYAN, B_WHITE,
    ) = ansi


def load_palette(path=PALETTE_PATH):
    palette = json.loads(Path(path).read_text())
    set_palette(palette)
    return palette


load_palette()


def rgb(hex_color):
    h = hex_color.lstrip("#")
    return "rgb_({},{},{})".format(*(int(h[i:i + 2], 16) for i in (0, 2, 4)))


def herdr_app():
    data = {
        "background": BG,
        "foreground": FG,
        "selection": core["selection"],
        "cursor": core["cursor"],
        "ansi": ansi,
        "colors": {
            "background": BG,
            "canvas": ui["canvas"],
            "chrome": ui["side"],
            "surface": ui["line"],
            "popover": ui["popover"],
            "raised": ui["raised"],
            "hover": ui["hover"],
            "selected": ui["active"],
            "border": ui["border"],
            "input": ui["input"],
            "foreground": FG,
            "muted": FG,
            "dim": ui["dim"],
            "accent": ui["accent"],
            "accent_foreground": B_WHITE,
            "solid": ui["solid"],
            "solid_foreground": B_WHITE,
            "selection": core["selection"],
            **status,
        },
    }
    return json.dumps(data, indent=2) + "\n"


def wezterm():
    q = lambda xs: "{ " + ", ".join(f'"{x}"' for x in xs) + " }"
    return f'''-- Generated by scripts/build.py from palette/palette.json. Do not edit by hand.
-- Usage in ~/.wezterm.lua: config.colors = require("hadal") (adjust package.path) or paste the table.
return {{
	foreground = "{FG}",
	background = "{BG}",
	cursor_bg = "{core["cursor"]}",
	cursor_border = "{core["cursor"]}",
	cursor_fg = "{BG}",
	selection_bg = "{core["selection"]}",
	selection_fg = "{FG}",
	ansi = {q(ansi[:8])},
	brights = {q(ansi[8:])},
}}
'''


def ghostty():
    pal = "\n".join(f"palette = {i}={c}" for i, c in enumerate(ansi))
    return f"""# Generated by scripts/build.py from palette/palette.json. Do not edit by hand.
{pal}
background = {BG}
foreground = {FG}
cursor-color = {core["cursor"]}
cursor-text = {BG}
selection-background = {core["selection"]}
selection-foreground = {FG}
"""


def cmux():
    data = {
        "app": {"accentColor": ui["accent"]},
        "paneBorderColor": ui["border"],
        "activePaneBorderColor": ui["focus"],
        "notifications": {"paneFlashColor": syn["func"]},
        "sidebar": {
            "selectionColor": ui["active"],
            "notificationBadgeColor": syn["func"],
        },
        "workspaceColors": {
            "colors": {
                "Red": syn["error"],
                "Crimson": syn["invalid"],
                "Orange": syn["orange"],
                "Amber": syn["func"],
                "Olive": syn["rosewater"],
                "Green": syn["string"],
                "Teal": syn["add"],
                "Aqua": ui["dim"],
                "Blue": ui["accent"],
                "Navy": ui["active"],
                "Indigo": ui["comment"],
                "Purple": syn["builtin"],
                "Magenta": syn["number"],
                "Rose": syn["keyword"],
                "Brown": ui["solid"],
                "Charcoal": ui["border"],
            }
        },
    }
    return json.dumps(data, indent=2) + "\n"


def opencode():
    def mix(a, b, t):
        ca = [int(a[i:i + 2], 16) for i in (1, 3, 5)]
        cb = [int(b[i:i + 2], 16) for i in (1, 3, 5)]
        return "#" + "".join(f"{round(x * t + y * (1 - t)):02x}" for x, y in zip(ca, cb))

    def ramp(c):
        steps = (mix(c, "#ffffff", 0.15), mix(c, "#ffffff", 0.5), mix(c, BG, 0.55), c,
                 mix(c, BG, 0.5), mix(c, BG, 0.3), mix(c, BG, 0.18), mix(c, BG, 0.1),
                 mix(c, BG, 0.04))
        return {str(100 * (i + 1)): v for i, v in enumerate(steps)}

    tint = P["tints"]
    neutral = dict(zip(
        (str(100 * i) for i in range(1, 10)),
        (FG, mix(FG, ui["dim"], 0.5), ui["dim"], ui["solid"], ui["popover"],
         ui["raised"], ui["line"], ui["side"], BG)))
    hue = {
        "gray": neutral,
        "blue": ramp(ui["accent"]),
        "orange": ramp(syn["orange"]),
        "purple": ramp(syn["builtin"]),
        "red": ramp(syn["error"]),
        "green": ramp(syn["string"]),
        "accent": "$hue.blue",
        "interactive": "$hue.blue",
        "neutral": "$hue.gray",
    }
    base = {
        "categorical": ["blue", "purple", "green", "orange", "red"],
        "text": {
            "base": "$hue.neutral.100",
            "muted": "$hue.neutral.300",
            "action": {
                "primary": {"base": "$text.base", "$disabled": "$text.muted",
                            "$focused": "$text.base", "$selected": "$hue.interactive.400"},
                "secondary": {"base": "$text.muted", "$hovered": "$text.base",
                              "$focused": "$hue.interactive.200"},
                "destructive": {"base": "$hue.neutral.900", "$disabled": "$text.muted"},
            },
            "formfield": {"base": "$text.base", "$hovered": "$hue.interactive.400",
                          "$focused": "$hue.interactive.400", "$pressed": "$hue.interactive.400",
                          "$disabled": "$text.muted", "$selected": "$hue.interactive.400"},
            "feedback": {
                "error": {"base": "$hue.red.400"},
                "warning": {"base": "$hue.orange.400"},
                "success": {"base": "$hue.green.400"},
                "info": {"base": "$hue.blue.400"},
            },
        },
        "background": {
            "base": "$hue.neutral.900",
            "raised": {"base": "$hue.neutral.700", "high": "$hue.neutral.600",
                       "max": "$hue.neutral.500"},
            "action": {
                "primary": {"base": "transparent", "$hovered": "$hue.neutral.700",
                            "$focused": "$hue.interactive.600", "$selected": "transparent"},
                "secondary": {"base": "transparent"},
                "destructive": {"base": "$hue.red.400"},
            },
            "formfield": {"base": "$background.base"},
            "feedback": {k: {"base": "$background.base"}
                         for k in ("error", "warning", "success", "info")},
        },
        "border": {"base": ui["border"]},
        "scrollbar": {"base": ui["solid"]},
        "diff": {
            "text": {"added": syn["string"], "removed": syn["error"],
                     "context": ui["dim"], "hunkHeader": ui["dim"]},
            "background": {"added": tint["diff_add"], "removed": tint["diff_delete"],
                           "context": "$hue.neutral.700"},
            "highlight": {"added": syn["string"], "removed": syn["error"]},
            "lineNumber": {"text": ui["comment"],
                           "background": {"added": tint["diff_add"],
                                          "removed": tint["diff_delete"]}},
        },
        "syntax": {"comment": ui["comment"], "keyword": syn["keyword"], "function": syn["func"],
                   "variable": FG, "string": syn["string"], "number": syn["number"],
                   "type": syn["type"], "operator": syn["fg_bright"], "punctuation": ui["dim"]},
        "markdown": {"text": FG, "heading": syn["func"], "link": ui["accent"],
                     "linkText": syn["fg_bright"], "code": syn["string"],
                     "blockQuote": ui["dim"], "emphasis": syn["rosewater"],
                     "strong": syn["fg_bright"], "horizontalRule": ui["comment"],
                     "listItem": ui["accent"], "listEnumeration": syn["func"],
                     "image": ui["accent"], "imageText": syn["fg_bright"], "codeBlock": FG},
        "@dialog": {
            "background": {"base": "$background.raised.base",
                           "action": {"primary": {"$hovered": "$background.raised.max"},
                                      "secondary": {"$hovered": "$background.raised.max"}}},
            "@footer": {"text": {"muted": "$hue.neutral.200"}},
        },
    }
    data = {"$schema": "https://opencode.ai/theme.json", "base": base, "dark": {"hue": hue}}
    return json.dumps(data, indent=2) + "\n"


def opencode_v1():
    tint = P["tints"]
    both = lambda c: {"dark": c, "light": c}
    colors = {
        "primary": ui["accent"],
        "secondary": syn["fg_bright"],
        "accent": syn["func"],
        "error": syn["error"],
        "warning": syn["orange"],
        "success": syn["string"],
        "info": syn["add"],
        "text": FG,
        "textMuted": ui["dim"],
        "background": BG,
        "backgroundPanel": ui["side"],
        "backgroundElement": ui["raised"],
        "backgroundMenu": ui["popover"],
        "border": ui["border"],
        "borderActive": ui["focus"],
        "borderSubtle": ui["line"],
        "diffAdded": syn["string"],
        "diffRemoved": syn["error"],
        "diffContext": ui["dim"],
        "diffHunkHeader": ui["dim"],
        "diffHighlightAdded": syn["string"],
        "diffHighlightRemoved": syn["error"],
        "diffAddedBg": tint["diff_add"],
        "diffRemovedBg": tint["diff_delete"],
        "diffContextBg": BG,
        "diffLineNumber": ui["comment"],
        "diffAddedLineNumberBg": tint["diff_add"],
        "diffRemovedLineNumberBg": tint["diff_delete"],
        "markdownText": FG,
        "markdownHeading": syn["func"],
        "markdownLink": ui["accent"],
        "markdownLinkText": syn["fg_bright"],
        "markdownCode": syn["string"],
        "markdownBlockQuote": ui["dim"],
        "markdownEmph": syn["rosewater"],
        "markdownStrong": syn["fg_bright"],
        "markdownHorizontalRule": ui["comment"],
        "markdownListItem": ui["accent"],
        "markdownListEnumeration": syn["func"],
        "markdownImage": ui["accent"],
        "markdownImageText": syn["fg_bright"],
        "markdownCodeBlock": FG,
        "syntaxComment": ui["comment"],
        "syntaxKeyword": syn["keyword"],
        "syntaxFunction": syn["func"],
        "syntaxVariable": FG,
        "syntaxString": syn["string"],
        "syntaxNumber": syn["number"],
        "syntaxType": syn["type"],
        "syntaxOperator": syn["fg_bright"],
        "syntaxPunctuation": ui["dim"],
    }
    data = {
        "$schema": "https://opencode.ai/theme.json",
        "theme": {k: both(v) for k, v in colors.items()},
    }
    return json.dumps(data, indent=2) + "\n"


def tmux():
    m = {
        "bg": BG, "fg": FG, "rosewater": syn["rosewater"], "flamingo": RED, "pink": MAGENTA,
        "mauve": B_MAGENTA, "red": RED, "maroon": B_RED, "peach": syn["func"], "yellow": YELLOW,
        "green": GREEN, "teal": CYAN, "sky": B_CYAN, "sapphire": B_BLUE, "blue": B_BLUE,
        "lavender": BLUE, "subtext_1": FG, "subtext_0": FG, "overlay_2": ui["dim"],
        "overlay_1": ui["dim"], "overlay_0": ui["comment"], "surface_2": ui["border"],
        "surface_1": ui["input"], "surface_0": ui["line"], "mantle": ui["side"], "crust": BG,
    }
    lines = "\n".join(f'set -g @thm_{k} "{v}"' for k, v in m.items())
    return f"""# Generated by scripts/build.py from palette/palette.json. Do not edit by hand.
# Hadal for catppuccin/tmux.
# catppuccin reads @thm_* with `set -ogq`, so source this file BEFORE the plugin loads.
{lines}
"""


def starship():
    m = {
        "rosewater": syn["rosewater"], "flamingo": RED, "pink": MAGENTA, "orange": syn["orange"],
        "red": RED, "maroon": B_RED, "peach": syn["func"], "yellow": YELLOW, "green": GREEN,
        "teal": CYAN, "sky": B_CYAN, "sapphire": B_BLUE, "blue": B_BLUE, "purple": MAGENTA,
        "lavender": BLUE, "text": FG, "subtext1": FG, "subtext0": ui["dim"],
        "overlay2": ui["dim"], "overlay1": ui["comment"], "overlay0": ui["comment"],
        "surface2": ui["border"], "surface1": ui["input"], "surface0": ui["line"],
        "base": BG, "mantle": BG, "crust": BG,
    }
    lines = "\n".join(f'{k} = "{v}"' for k, v in m.items())
    return f"""# Generated by scripts/build.py from palette/palette.json. Do not edit by hand.
# Hadal palette for starship.
# Paste into ~/.config/starship.toml and set `palette = 'hadal'`.
# The color names follow the Catppuccin naming used by many starship presets.
palette = 'hadal'

[palettes.hadal]
{lines}
"""


def zsh():
    s = {
        "command": syn["func"], "alias": syn["func"], "function": syn["func"],
        "builtin": syn["builtin"], "reserved-word": ui["accent"],
        "precommand": syn["builtin"] + ",underline", "commandseparator": FG,
        "path": FG + ",underline", "globbing": syn["number"],
        "single-hyphen-option": B_BLUE, "double-hyphen-option": B_BLUE,
        "single-quoted-argument": syn["string"], "double-quoted-argument": syn["string"],
        "dollar-quoted-argument": syn["string"], "back-quoted-argument": syn["builtin"],
        "redirection": syn["func"], "comment": ui["comment"], "unknown-token": syn["error"],
        "arg0": syn["func"],
    }
    styles = "\n".join(f'ZSH_HIGHLIGHT_STYLES[{k}]="fg={v}"' for k, v in s.items())
    fzf = (f"--color=fg:{FG},fg+:{syn['fg_bright']},bg+:{ui['active']},hl:{syn['func']},"
           f"hl+:{YELLOW},info:{ui['dim']},prompt:{ui['accent']},pointer:{syn['func']},"
           f"marker:{syn['string']},spinner:{syn['builtin']},header:{ui['dim']},"
           f"border:{ui['border']},gutter:-1")
    return f"""# Generated by scripts/build.py from palette/palette.json. Do not edit by hand.
# Hadal: zsh-syntax-highlighting, zsh-autosuggestions and fzf
# Add `source /path/to/hadal.zsh` to ~/.zshrc, after the plugins are loaded.
ZSH_AUTOSUGGEST_HIGHLIGHT_STYLE="fg={ui["dim"]}"
typeset -A ZSH_HIGHLIGHT_STYLES
{styles}

export FZF_DEFAULT_OPTS="{fzf}"
"""


def herdr_tui():
    m = {
        "panel_bg": BG, "sidebar_bg": ui["side"], "active_row_bg": ui["active"],
        "selection_bg": ui["raised"], "surface0": ui["line"], "surface1": ui["input"],
        "surface_dim": ui["side"], "overlay0": ui["comment"], "overlay1": ui["dim"],
        "text": FG, "subtext0": ui["dim"], "accent": ui["accent"], "mauve": B_MAGENTA,
        "green": syn["string"], "yellow": syn["func"], "red": syn["error"], "blue": B_BLUE,
        "teal": CYAN, "peach": syn["orange"],
    }
    lines = "\n".join(f'{k} = "{v}"' for k, v in m.items())
    return f"""# Generated by scripts/build.py from palette/palette.json. Do not edit by hand.
# Hadal for the Herdr TUI. Merge into ~/.config/herdr/config.toml.
[theme]
name = "catppuccin"
auto_switch = false

[theme.custom]
{lines}
"""


def lsd():
    c = lambda x: rgb(x)
    return f"""# Generated by scripts/build.py from palette/palette.json. Do not edit by hand.
user: {c(FG)}
group: {c(ui["dim"])}
permission:
  read: {c(syn["string"])}
  write: {c(syn["func"])}
  exec: {c(RED)}
  exec-sticky: {c(MAGENTA)}
  no-access: {c(ui["comment"])}
  octal: {c(B_BLUE)}
  acl: {c(syn["builtin"])}
  context: {c(ui["dim"])}
date:
  hour-old: {c(CYAN)}
  day-old: {c(B_BLUE)}
  older: {c(ui["dim"])}
size:
  none: {c(ui["comment"])}
  small: {c(GREEN)}
  medium: {c(YELLOW)}
  large: {c(RED)}
inode:
  valid: {c(MAGENTA)}
  invalid: {c(ui["comment"])}
links:
  valid: {c(MAGENTA)}
  invalid: {c(ui["comment"])}
tree-edge: {c(ui["border"])}
git-status:
  default: {c(FG)}
  unmodified: {c(ui["comment"])}
  ignored: {c(ui["comment"])}
  new-in-index: {c(syn["string"])}
  new-in-workdir: {c(syn["string"])}
  typechange: {c(syn["func"])}
  deleted: {c(syn["error"])}
  renamed: {c(CYAN)}
  modified: {c(syn["orange"])}
  conflicted: {c(RED)}
"""


def lazygit():
    items = [
        ("activeBorderColor", [ui["accent"], "bold"]),
        ("inactiveBorderColor", [ui["border"]]),
        ("searchingActiveBorderColor", [syn["func"], "bold"]),
        ("optionsTextColor", [ui["accent"]]),
        ("selectedLineBgColor", [ui["active"]]),
        ("inactiveViewSelectedLineBgColor", [ui["raised"]]),
        ("cherryPickedCommitFgColor", [ui["accent"]]),
        ("cherryPickedCommitBgColor", [ui["active"]]),
        ("markedBaseCommitFgColor", [syn["func"]]),
        ("markedBaseCommitBgColor", [ui["active"]]),
        ("unstagedChangesColor", [syn["error"]]),
        ("defaultFgColor", [FG]),
    ]
    body = ""
    for key, vals in items:
        body += f"    {key}:\n"
        for v in vals:
            body += f'      - "{v}"\n' if v.startswith("#") else f"      - {v}\n"
    return f"# Generated by scripts/build.py from palette/palette.json. Do not edit by hand.\ngui:\n  theme:\n{body}"


def nvim_palette():
    m = {
        "bg": BG, "fg": FG, "sel": core["selection"], "cursor": core["cursor"],
        "side": ui["side"], "line": ui["line"], "border": ui["border"],
        "linenr": ui["dim"], "comment": ui["comment"], "string": syn["string"],
        "keyword": syn["keyword"], "func": syn["func"], "const": syn["builtin"],
        "type": syn["type"], "err": syn["error"], "hover": ui["hover"], "active": ui["active"],
        "number": syn["number"], "param": ui["accent"], "builtin": syn["builtin"],
        "invalid": syn["invalid"], "add": syn["add"], "change": syn["orange"],
        "input": ui["input"], "float": ui["popover"], "warn": syn["orange"],
        "info": ui["accent"], "hint": syn["string"],
        **P["tints"],
    }
    lines = "\n".join(f'  {k} = "{v}",' for k, v in m.items())
    ansi_lua = "\n".join(
        "  " + ", ".join(f'"{x}"' for x in ansi[i:i + 8]) + "," for i in (0, 8)
    )
    return f"""-- Generated by scripts/build.py from palette/palette.json. Do not edit by hand.
return {{
{lines}
  ansi = {{
{ansi_lua}
  }},
}}
"""


def zed():
    T = "#00000000"
    a = lambda color, alpha: color + alpha
    t = P["tints"]
    names = ["black", "red", "green", "yellow", "blue", "magenta", "cyan", "white"]
    term = {f"terminal.ansi.{n}": ansi[i] for i, n in enumerate(names)}
    term.update({f"terminal.ansi.bright_{n}": ansi[i + 8] for i, n in enumerate(names)})

    def status_group(name, color, bg):
        return {name: color, f"{name}.background": bg, f"{name}.border": color}

    def tone(name, fg_color, bg_color):
        return {name: fg_color, f"{name}.background": bg_color, f"{name}.border": ui["border"]}

    sx = lambda color, **kw: {"color": color, **kw}
    style = {
        "border": ui["border"], "border.variant": ui["border"],
        "border.focused": ui["focus"], "border.selected": ui["focus"],
        "border.transparent": T, "border.disabled": ui["border"],
        "elevated_surface.background": ui["popover"],
        "surface.background": ui["side"], "background": ui["side"],
        "element.background": ui["line"], "element.hover": ui["hover"],
        "element.active": ui["active"], "element.selected": ui["active"],
        "element.disabled": ui["line"], "drop_target.background": a(ui["active"], "80"),
        "ghost_element.background": T, "ghost_element.hover": ui["hover"],
        "ghost_element.active": ui["active"], "ghost_element.selected": ui["active"],
        "ghost_element.disabled": T,
        "text": FG, "text.muted": ui["dim"], "text.placeholder": ui["comment"],
        "text.disabled": ui["comment"], "text.accent": ui["accent"],
        "icon": FG, "icon.muted": ui["dim"], "icon.disabled": ui["comment"],
        "icon.placeholder": ui["dim"], "icon.accent": ui["accent"],
        "status_bar.background": ui["line"], "title_bar.background": ui["line"],
        "title_bar.inactive_background": ui["side"], "toolbar.background": BG,
        "tab_bar.background": ui["canvas"], "tab.inactive_background": ui["line"],
        "tab.active_background": BG, "search.match_background": a(syn["func"], "60"),
        "panel.background": ui["side"], "panel.focused_border": ui["focus"],
        "pane.focused_border": ui["focus"],
        "scrollbar.thumb.background": a(ui["border"], "80"),
        "scrollbar.thumb.hover_background": ui["dim"],
        "scrollbar.thumb.border": ui["border"], "scrollbar.track.background": T,
        "scrollbar.track.border": ui["border"],
        "editor.foreground": FG, "editor.background": BG, "editor.gutter.background": BG,
        "editor.subheader.background": ui["side"],
        "editor.active_line.background": ui["hover"],
        "editor.highlighted_line.background": ui["hover"],
        "editor.line_number": ui["dim"], "editor.active_line_number": syn["func"],
        "editor.invisible": ui["border"], "editor.wrap_guide": ui["border"],
        "editor.active_wrap_guide": ui["dim"],
        "editor.document_highlight.read_background": a(ui["active"], "80"),
        "editor.document_highlight.write_background": a(ui["active"], "80"),
        "terminal.background": BG, "terminal.foreground": FG,
        "terminal.bright_foreground": B_WHITE, "terminal.dim_foreground": ui["dim"],
        **term,
        "link_text.hover": ui["accent"],
        **status_group("conflict", syn["orange"], t["warn_bg"]),
        **status_group("created", syn["string"], t["hint_bg"]),
        **status_group("deleted", syn["error"], t["error_bg"]),
        **status_group("modified", syn["orange"], t["warn_bg"]),
        **status_group("error", syn["error"], t["error_bg"]),
        **status_group("warning", syn["orange"], t["warn_bg"]),
        **status_group("info", ui["accent"], t["info_bg"]),
        **status_group("hint", syn["string"], t["hint_bg"]),
        **status_group("success", syn["string"], t["hint_bg"]),
        **tone("hidden", ui["dim"], ui["line"]),
        **tone("ignored", ui["comment"], ui["line"]),
        **tone("predictive", ui["dim"], ui["line"]),
        **tone("unreachable", ui["comment"], ui["line"]),
        "players": [
            {"cursor": core["cursor"], "background": core["cursor"], "selection": a(core["selection"], "80")},
            {"cursor": ui["accent"], "background": ui["accent"], "selection": a(ui["accent"], "40")},
            {"cursor": syn["string"], "background": syn["string"], "selection": a(syn["string"], "40")},
            {"cursor": B_MAGENTA, "background": B_MAGENTA, "selection": a(B_MAGENTA, "40")},
        ],
        "syntax": {
            "attribute": sx(syn["func"]), "boolean": sx(syn["number"]),
            "comment": sx(ui["comment"]), "comment.doc": sx(ui["comment"]),
            "constant": sx(syn["number"]), "constructor": sx(syn["type"]),
            "embedded": sx(FG), "emphasis": sx(syn["string"], font_style="italic"),
            "emphasis.strong": sx(syn["string"], font_weight=700),
            "enum": sx(syn["type"]), "function": sx(syn["func"]), "hint": sx(syn["string"]),
            "keyword": sx(syn["keyword"]), "label": sx(ui["accent"]),
            "link_text": sx(ui["accent"]), "link_uri": sx(ui["accent"]),
            "number": sx(syn["number"]), "operator": sx(FG), "predictive": sx(ui["dim"]),
            "preproc": sx(syn["keyword"]), "primary": sx(FG), "property": sx(FG),
            "punctuation": sx(FG), "punctuation.bracket": sx(FG),
            "punctuation.delimiter": sx(FG), "punctuation.list_marker": sx(syn["func"]),
            "punctuation.special": sx(syn["func"]), "string": sx(syn["string"]),
            "string.escape": sx(syn["number"]), "string.regex": sx(syn["string"]),
            "string.special": sx(syn["string"]), "string.special.symbol": sx(syn["string"]),
            "tag": sx(syn["keyword"]), "text.literal": sx(syn["builtin"]),
            "title": sx(syn["func"], font_weight=700), "type": sx(syn["type"]),
            "variable": sx(FG), "variable.special": sx(syn["builtin"]),
            "variant": sx(syn["builtin"]),
        },
    }
    data = {
        "$schema": "https://zed.dev/schema/themes/v0.2.0.json",
        "name": "Hadal",
        "author": "tcagriz",
        "themes": [{"name": "Hadal", "appearance": "dark", "style": style}],
    }
    return json.dumps(data, indent=2) + "\n"


def vscode():
    t = P["tints"]
    names = ["Black", "Red", "Green", "Yellow", "Blue", "Magenta", "Cyan", "White"]
    term = {f"terminal.ansi{n}": ansi[i] for i, n in enumerate(names)}
    term.update({f"terminal.ansiBright{n}": ansi[i + 8] for i, n in enumerate(names)})
    a = lambda color, alpha: color + alpha
    colors = {
        "foreground": FG,
        "descriptionForeground": ui["dim"],
        "errorForeground": syn["error"],
        "focusBorder": ui["focus"],
        "widget.shadow": a(BG, "99"),
        "selection.background": ui["focus"],
        "icon.foreground": ui["dim"],
        "sash.hoverBorder": ui["focus"],
        "textLink.foreground": ui["accent"],
        "textLink.activeForeground": syn["fg_bright"],
        "textCodeBlock.background": ui["line"],
        "textBlockQuote.background": ui["side"],
        "textBlockQuote.border": ui["border"],
        "textSeparator.foreground": ui["border"],
        "badge.background": ui["accent"],
        "badge.foreground": B_WHITE,
        "progressBar.background": ui["accent"],
        "button.background": ui["solid"],
        "button.foreground": B_WHITE,
        "button.hoverBackground": ui["focus"],
        "button.secondaryBackground": ui["raised"],
        "button.secondaryForeground": FG,
        "button.secondaryHoverBackground": ui["active"],
        "checkbox.background": ui["input"],
        "checkbox.border": ui["border"],
        "dropdown.background": ui["input"],
        "dropdown.border": ui["border"],
        "dropdown.foreground": FG,
        "input.background": ui["input"],
        "input.border": ui["border"],
        "input.foreground": FG,
        "input.placeholderForeground": ui["dim"],
        "inputOption.activeBorder": ui["accent"],
        "inputOption.activeBackground": ui["active"],
        "inputValidation.infoBackground": t["info_bg"],
        "inputValidation.infoBorder": ui["accent"],
        "inputValidation.warningBackground": t["warn_bg"],
        "inputValidation.warningBorder": syn["orange"],
        "inputValidation.errorBackground": t["error_bg"],
        "inputValidation.errorBorder": syn["error"],
        "scrollbar.shadow": a(BG, "aa"),
        "scrollbarSlider.background": a(ui["solid"], "88"),
        "scrollbarSlider.hoverBackground": a(ui["focus"], "88"),
        "scrollbarSlider.activeBackground": a(ui["focus"], "bb"),
        "list.activeSelectionBackground": ui["active"],
        "list.activeSelectionForeground": B_WHITE,
        "list.inactiveSelectionBackground": ui["raised"],
        "list.hoverBackground": ui["hover"],
        "list.focusBackground": ui["active"],
        "list.dropBackground": ui["hover"],
        "list.highlightForeground": ui["accent"],
        "list.errorForeground": syn["error"],
        "list.warningForeground": syn["orange"],
        "tree.indentGuidesStroke": ui["border"],
        "menu.background": ui["popover"],
        "menu.foreground": FG,
        "menu.selectionBackground": ui["active"],
        "menu.selectionForeground": B_WHITE,
        "menu.separatorBackground": ui["border"],
        "menu.border": ui["border"],
        "activityBar.background": ui["side"],
        "activityBar.foreground": syn["fg_bright"],
        "activityBar.inactiveForeground": ui["dim"],
        "activityBar.border": ui["border"],
        "activityBar.activeBorder": ui["accent"],
        "activityBarBadge.background": ui["accent"],
        "activityBarBadge.foreground": B_WHITE,
        "sideBar.background": ui["side"],
        "sideBar.foreground": FG,
        "sideBar.border": ui["border"],
        "sideBarTitle.foreground": syn["fg_bright"],
        "sideBarSectionHeader.background": ui["line"],
        "sideBarSectionHeader.foreground": syn["fg_bright"],
        "sideBarSectionHeader.border": ui["border"],
        "editorGroup.border": ui["border"],
        "editorGroup.dropBackground": a(ui["solid"], "aa"),
        "editorGroupHeader.tabsBackground": ui["canvas"],
        "editorGroupHeader.noTabsBackground": BG,
        "tab.activeBackground": BG,
        "tab.activeForeground": syn["fg_bright"],
        "tab.activeBorderTop": ui["accent"],
        "tab.inactiveBackground": ui["line"],
        "tab.inactiveForeground": ui["dim"],
        "tab.border": ui["border"],
        "tab.hoverBackground": ui["hover"],
        "tab.lastPinnedBorder": ui["solid"],
        "tab.unfocusedActiveForeground": ui["dim"],
        "breadcrumb.foreground": ui["dim"],
        "breadcrumb.focusForeground": syn["fg_bright"],
        "breadcrumb.activeSelectionForeground": B_WHITE,
        "breadcrumbPicker.background": ui["popover"],
        "editor.background": BG,
        "editor.foreground": FG,
        "editorLineNumber.foreground": ui["dim"],
        "editorLineNumber.activeForeground": syn["fg_bright"],
        "editorCursor.foreground": core["cursor"],
        "editor.selectionBackground": core["selection"],
        "editor.inactiveSelectionBackground": a(core["selection"], "77"),
        "editor.selectionHighlightBackground": a(core["selection"], "55"),
        "editor.wordHighlightBackground": a(ui["solid"], "88"),
        "editor.wordHighlightStrongBackground": a(ui["active"], "aa"),
        "editor.findMatchBackground": a(syn["orange"], "77"),
        "editor.findMatchHighlightBackground": a(syn["fg_bright"], "33"),
        "editor.findRangeHighlightBackground": a(ui["solid"], "55"),
        "editor.hoverHighlightBackground": a(ui["solid"], "66"),
        "editor.lineHighlightBackground": ui["line"],
        "editor.rangeHighlightBackground": a(ui["solid"], "44"),
        "editor.foldBackground": a(ui["solid"], "44"),
        "editorLink.activeForeground": ui["accent"],
        "editorWhitespace.foreground": ui["border"],
        "editorIndentGuide.background1": ui["line"],
        "editorIndentGuide.activeBackground1": ui["solid"],
        "editorRuler.foreground": ui["line"],
        "editorBracketMatch.background": a(ui["solid"], "88"),
        "editorBracketMatch.border": ui["focus"],
        "editorGutter.background": BG,
        "editorGutter.addedBackground": syn["add"],
        "editorGutter.modifiedBackground": syn["orange"],
        "editorGutter.deletedBackground": syn["error"],
        "editorError.foreground": syn["error"],
        "editorWarning.foreground": syn["orange"],
        "editorInfo.foreground": ui["accent"],
        "editorHint.foreground": ui["dim"],
        "editorOverviewRuler.border": ui["border"],
        "editorOverviewRuler.errorForeground": syn["error"],
        "editorOverviewRuler.warningForeground": syn["orange"],
        "editorOverviewRuler.infoForeground": ui["accent"],
        "editorOverviewRuler.addedForeground": syn["add"],
        "editorOverviewRuler.modifiedForeground": syn["orange"],
        "editorOverviewRuler.deletedForeground": syn["error"],
        "editorWidget.background": ui["popover"],
        "editorWidget.border": ui["border"],
        "editorSuggestWidget.background": ui["popover"],
        "editorSuggestWidget.border": ui["border"],
        "editorSuggestWidget.selectedBackground": ui["active"],
        "editorSuggestWidget.highlightForeground": ui["accent"],
        "editorHoverWidget.background": ui["popover"],
        "editorHoverWidget.border": ui["border"],
        "editorMarkerNavigation.background": ui["side"],
        "peekView.border": ui["border"],
        "peekViewEditor.background": ui["line"],
        "peekViewEditor.matchHighlightBackground": a(syn["fg_bright"], "33"),
        "peekViewResult.background": ui["side"],
        "peekViewResult.matchHighlightBackground": a(syn["fg_bright"], "44"),
        "peekViewResult.selectionBackground": ui["active"],
        "peekViewTitle.background": ui["line"],
        "peekViewTitleLabel.foreground": syn["fg_bright"],
        "diffEditor.insertedTextBackground": a(syn["add"], "33"),
        "diffEditor.insertedLineBackground": t["diff_add"],
        "diffEditor.removedTextBackground": a(syn["error"], "44"),
        "diffEditor.removedLineBackground": t["diff_delete"],
        "diffEditor.diagonalFill": ui["line"],
        "merge.currentHeaderBackground": a(syn["add"], "55"),
        "merge.incomingHeaderBackground": a(ui["accent"], "55"),
        "minimap.selectionHighlight": core["selection"],
        "minimap.findMatchHighlight": syn["orange"],
        "minimap.errorHighlight": syn["error"],
        "minimap.warningHighlight": syn["orange"],
        "minimapGutter.addedBackground": syn["add"],
        "minimapGutter.modifiedBackground": syn["orange"],
        "minimapGutter.deletedBackground": syn["error"],
        "panel.background": ui["side"],
        "panel.border": ui["border"],
        "panelTitle.activeForeground": syn["fg_bright"],
        "panelTitle.activeBorder": ui["accent"],
        "panelTitle.inactiveForeground": ui["dim"],
        "panelSection.border": ui["border"],
        "panelSectionHeader.border": ui["border"],
        "statusBar.background": ui["line"],
        "statusBar.foreground": FG,
        "statusBar.border": ui["border"],
        "statusBar.noFolderBackground": ui["line"],
        "statusBar.debuggingBackground": syn["orange"],
        "statusBar.debuggingForeground": B_WHITE,
        "statusBarItem.hoverBackground": ui["hover"],
        "statusBarItem.remoteBackground": ui["accent"],
        "statusBarItem.remoteForeground": B_WHITE,
        "statusBarItem.prominentBackground": ui["active"],
        "statusBarItem.errorBackground": syn["invalid"],
        "titleBar.activeBackground": ui["line"],
        "titleBar.activeForeground": FG,
        "titleBar.inactiveBackground": ui["side"],
        "titleBar.inactiveForeground": ui["dim"],
        "titleBar.border": ui["border"],
        "notifications.background": ui["popover"],
        "notifications.foreground": FG,
        "notifications.border": ui["border"],
        "notificationCenterHeader.background": ui["raised"],
        "notificationLink.foreground": ui["accent"],
        "pickerGroup.border": ui["focus"],
        "pickerGroup.foreground": ui["focus"],
        "quickInputList.focusBackground": ui["active"],
        "quickInputTitle.background": ui["raised"],
        "gitDecoration.addedResourceForeground": syn["add"],
        "gitDecoration.modifiedResourceForeground": syn["orange"],
        "gitDecoration.deletedResourceForeground": syn["error"],
        "gitDecoration.untrackedResourceForeground": syn["string"],
        "gitDecoration.ignoredResourceForeground": ui["comment"],
        "gitDecoration.conflictingResourceForeground": syn["number"],
        "gitDecoration.stageModifiedResourceForeground": syn["orange"],
        "gitDecoration.stageDeletedResourceForeground": syn["error"],
        "debugToolBar.background": ui["raised"],
        "debugExceptionWidget.background": ui["raised"],
        "debugExceptionWidget.border": syn["error"],
        "debugIcon.breakpointForeground": syn["error"],
        "extensionButton.prominentBackground": syn["string"],
        "extensionButton.prominentHoverBackground": a(syn["string"], "bb"),
        "settings.headerForeground": syn["fg_bright"],
        "settings.modifiedItemIndicator": ui["accent"],
        "terminal.background": BG,
        "terminal.foreground": FG,
        "terminal.selectionBackground": core["selection"],
        "terminalCursor.foreground": core["cursor"],
        "terminal.border": ui["border"],
        **term,
        "charts.red": syn["error"],
        "charts.blue": ui["accent"],
        "charts.yellow": syn["func"],
        "charts.orange": syn["orange"],
        "charts.green": syn["string"],
        "charts.purple": syn["builtin"],
    }

    def rule(scope, fg=None, style=None, name=None):
        settings = {}
        if fg:
            settings["foreground"] = fg
        if style is not None:
            settings["fontStyle"] = style
        entry = {"scope": scope, "settings": settings}
        if name:
            entry = {"name": name, **entry}
        return entry

    token_colors = [
        {"settings": {"foreground": FG}},
        rule(["meta.embedded", "source.groovy.embedded", "string meta.image.inline.markdown"], FG),
        rule("comment", ui["comment"], name="Comment"),
        rule("string", syn["string"], name="String"),
        rule(["constant.numeric", "constant.language", "constant.character", "constant.other"],
             syn["number"], name="Constants"),
        rule("variable", style=""),
        rule("keyword", syn["keyword"], name="Keyword"),
        rule("storage", syn["keyword"], "", name="Storage"),
        rule("storage.type", syn["builtin"], "italic", name="Storage type"),
        rule(["entity.name.class", "entity.name.type", "entity.name.namespace",
              "entity.name.scope-resolution"], syn["type"], "underline", name="Type"),
        rule("entity.other.inherited-class", syn["func"], "italic underline"),
        rule("entity.name.function", syn["func"], "", name="Function"),
        rule("variable.parameter", ui["accent"], "italic", name="Parameter"),
        rule("entity.name.tag", syn["keyword"], ""),
        rule("entity.other.attribute-name", syn["func"], ""),
        rule(["support.function", "support.constant"], syn["builtin"], ""),
        rule(["support.type", "support.class"], syn["builtin"], "italic"),
        rule("support.other.variable", style=""),
        rule(["invalid", "invalid.deprecated"], syn["invalid"], ""),
        rule(["meta.diff", "meta.diff.header"], syn["fg_bright"], "italic"),
        rule("markup.deleted", syn["error"], ""),
        rule("markup.changed", syn["orange"], ""),
        rule("markup.inserted", syn["add"]),
        rule("markup.quote", syn["string"]),
        rule(["markup.bold", "markup.italic"], syn["string"]),
        rule("markup.bold", style="bold"),
        rule("markup.italic", style="italic"),
        rule("markup.strikethrough", style="strikethrough"),
        rule("markup.inline.raw", syn["builtin"], ""),
        rule(["markup.heading", "markup.heading.setext"], syn["func"], "bold"),
    ]
    data = {
        "$schema": "vscode://schemas/color-theme",
        "name": P["name"],
        "type": "dark",
        "semanticHighlighting": True,
        "colors": colors,
        "tokenColors": token_colors,
    }
    return json.dumps(data, indent=2) + "\n"


def inkdrop_palette():
    names = ["black", "red", "green", "yellow", "blue", "magenta", "cyan", "white"]
    lines = [
        f"--hadal-bg: {BG};",
        f"--hadal-fg: {FG};",
        f"--hadal-selection: {core['selection']};",
        f"--hadal-cursor: {core['cursor']};",
    ]
    for group, prefix in ((ui, "ui"), (syn, "syn"), (P["tints"], "tint"), (status, "status")):
        lines += [f"--hadal-{prefix}-{k.replace('_', '-')}: {v};" for k, v in group.items()]
    for i, v in enumerate(ansi):
        name = ("bright-" if i >= 8 else "") + names[i % 8]
        lines.append(f"--hadal-ansi-{name}: {v};")
    body = "\n".join(f"    {l}" for l in lines)
    return (
        "/* Generated by scripts/build.py from palette/palette.json. Do not edit. */\n"
        f"@layer theme {{\n  :root {{\n{body}\n  }}\n}}\n"
    )


OUTPUTS = {
    "inkdrop/styles/palette.css": inkdrop_palette,
    "vscode/themes/hadal-color-theme.json": vscode,
    "zed/themes/hadal.json": zed,
    "neovim/lua/hadal/palette.lua": nvim_palette,
    "herdr-app/hadal.json": herdr_app,
    "wezterm/hadal.lua": wezterm,
    "ghostty/hadal": ghostty,
    "cmux/hadal.json": cmux,
    "opencode/hadal.json": opencode,
    "opencode/v1/hadal.json": opencode_v1,
    "tmux/hadal.conf": tmux,
    "starship/hadal.toml": starship,
    "zsh/hadal.zsh": zsh,
    "herdr-tui/theme.toml": herdr_tui,
    "lsd/colors.yaml": lsd,
    "lazygit/config.yml": lazygit,
}


def main():
    check = "--check" in sys.argv
    stale = []
    for rel, fn in OUTPUTS.items():
        path = ROOT / rel
        content = fn()
        if check:
            if not path.exists() or path.read_text() != content:
                stale.append(rel)
        else:
            path.parent.mkdir(parents=True, exist_ok=True)
            path.write_text(content)
            print("wrote", rel)
    if stale:
        print("out of date:", *stale, sep="\n  ")
        sys.exit(1)


if __name__ == "__main__":
    main()
