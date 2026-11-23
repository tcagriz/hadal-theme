#!/usr/bin/env python3
"""Regression checks for the Inkdrop publishing security boundary."""

from pathlib import Path
import re


ROOT = Path(__file__).resolve().parents[1]
PUBLISH = (ROOT / ".github" / "workflows" / "publish.yml").read_text()
CHECK = (ROOT / ".github" / "workflows" / "check.yml").read_text()
SECRET_NAMES = {"INKDROP_ACCESS_KEY_ID", "INKDROP_SECRET_ACCESS_KEY"}


def jobs(workflow: str) -> dict[str, str]:
    result = {}
    current = None
    in_jobs = False

    for line in workflow.splitlines(keepends=True):
        if line.rstrip() == "jobs:":
            in_jobs = True
            continue
        if not in_jobs:
            continue
        if not line.strip():
            if current is not None:
                result[current] += line
            continue
        if line and not line.startswith(" "):
            break
        match = re.match(r"^  ([A-Za-z0-9_-]+):\s*$", line)
        if match:
            current = match.group(1)
            result[current] = line
        elif current is not None:
            result[current] += line

    return result


def main() -> None:
    workflow_jobs = jobs(PUBLISH)
    assert {"validate", "publish"} <= set(workflow_jobs), workflow_jobs

    validate = workflow_jobs["validate"]
    publish = workflow_jobs["publish"]

    assert "if: github.ref == 'refs/heads/main'" in validate
    assert "python3 tests/publish_workflow_test.py" in validate
    assert "npm ci" in validate
    assert "npx generate-palette" in validate
    assert "npm pack --dry-run" in validate
    assert "environment:" not in validate
    assert "secrets." not in validate

    assert "needs: validate" in publish
    assert "if: github.ref == 'refs/heads/main'" in publish
    assert "environment: production" in publish

    secret_names = set(re.findall(r"secrets\.([A-Z0-9_]+)", PUBLISH))
    assert secret_names == SECRET_NAMES, secret_names
    assert all(
        "secrets." not in block
        for name, block in workflow_jobs.items()
        if name != "publish"
    )
    assert "protected production environment" in publish
    assert PUBLISH.count("environment: production") == 1

    assert "workflow_dispatch:" in PUBLISH
    assert not re.search(r"^\s{2}pull_request:", PUBLISH, re.MULTILINE)
    assert "secrets." not in CHECK
    assert all("environment:" not in job for job in jobs(CHECK).values())
    assert "python3 tests/publish_workflow_test.py" in CHECK


if __name__ == "__main__":
    main()
