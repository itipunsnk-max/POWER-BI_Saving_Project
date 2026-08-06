"""Fail CI when public repository contents violate the publication contract."""

from __future__ import annotations

import json
import os
import re
import shutil
import subprocess
import sys
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
BLOCKED_EXTENSIONS = {".xlsx", ".xls", ".pbix", ".pbit", ".docx", ".pdf"}
PRIVATE_KEYS = {
    "site_name",
    "technician_name",
    "call_detail",
    "update_by_user_name",
    "resolved_by_user_name",
    "service_address",
    "email",
    "phone",
}
REQUIRED_FILES = {
    "index.html",
    "styles.css",
    "app.js",
    "data/dashboard-data.json",
    "powerbi/measures-v2.dax",
    "powerbi/model-implementation-guide-v2.md",
    "docs/08-rev1-strategy-and-roadmap.md",
}


def tracked_files() -> list[str]:
    git_executable = shutil.which("git")
    if not git_executable and os.name == "nt":
        candidates = [
            Path(os.environ.get("LOCALAPPDATA", "")) / "Programs/Git/cmd/git.exe",
            Path(os.environ.get("ProgramFiles", "")) / "Git/cmd/git.exe",
        ]
        git_executable = next((str(path) for path in candidates if path.is_file()), None)
    if not git_executable:
        raise RuntimeError("git executable was not found")

    result = subprocess.run(
        [git_executable, "ls-files"],
        cwd=ROOT,
        check=True,
        capture_output=True,
        text=True,
        encoding="utf-8",
    )
    return [line.strip() for line in result.stdout.splitlines() if line.strip()]


def walk_keys(value: object, path: str = "$") -> list[str]:
    failures: list[str] = []
    if isinstance(value, dict):
        for key, child in value.items():
            normalized = re.sub(r"[^a-z0-9]+", "_", str(key).lower()).strip("_")
            if normalized in PRIVATE_KEYS:
                failures.append(f"private key {key!r} at {path}")
            failures.extend(walk_keys(child, f"{path}.{key}"))
    elif isinstance(value, list):
        for index, child in enumerate(value):
            failures.extend(walk_keys(child, f"{path}[{index}]"))
    return failures


def main() -> int:
    failures: list[str] = []
    files = tracked_files()
    names: list[str] = []

    blocked = [name for name in files if Path(name).suffix.lower() in BLOCKED_EXTENSIONS]
    if blocked:
        failures.append("blocked source artifacts are tracked: " + ", ".join(blocked))

    missing = sorted(name for name in REQUIRED_FILES if not (ROOT / name).is_file())
    if missing:
        failures.append("required delivery files are missing: " + ", ".join(missing))

    for json_path in sorted((ROOT / "data").glob("*.json")):
        payload = json.loads(json_path.read_text(encoding="utf-8"))
        failures.extend(f"{json_path.relative_to(ROOT)}: {item}" for item in walk_keys(payload))

    dax_path = ROOT / "powerbi" / "measures-v2.dax"
    if dax_path.is_file():
        names = re.findall(
            r"^([^\s/][^:\r\n]*?)\s*:=\s*$",
            dax_path.read_text(encoding="utf-8"),
            flags=re.MULTILINE,
        )
        duplicates = sorted({name for name in names if names.count(name) > 1})
        if duplicates:
            failures.append("duplicate DAX measure names: " + ", ".join(duplicates))
        if len(names) < 20:
            failures.append(f"unexpectedly small DAX measure set: {len(names)}")

    if failures:
        print("PUBLICATION CHECK: FAILED")
        for failure in failures:
            print(f"- {failure}")
        return 1

    print(f"PUBLICATION CHECK: PASSED ({len(files)} tracked files, {len(names)} DAX measures)")
    return 0


if __name__ == "__main__":
    sys.exit(main())
