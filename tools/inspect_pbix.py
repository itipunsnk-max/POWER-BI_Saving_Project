"""Read-only inventory for the report metadata stored inside a PBIX file."""

from __future__ import annotations

import argparse
import json
import zipfile
from pathlib import Path


def load_json_entry(archive: zipfile.ZipFile, name: str) -> dict:
    raw = archive.read(name)
    for encoding in ("utf-16-le", "utf-8"):
        try:
            return json.loads(raw.decode(encoding))
        except (UnicodeDecodeError, json.JSONDecodeError):
            continue
    raise ValueError(f"Unable to decode {name}")


def summarize_visual(container: dict) -> dict:
    config = json.loads(container.get("config", "{}"))
    visual = config.get("singleVisual", {})
    projections = visual.get("projections", {})
    fields = [
        item["queryRef"]
        for role_items in projections.values()
        for item in role_items
        if isinstance(item, dict) and item.get("queryRef")
    ]
    return {
        "name": config.get("name"),
        "type": visual.get("visualType", "shape/text/image"),
        "fields": fields,
        "x": container.get("x"),
        "y": container.get("y"),
        "width": container.get("width"),
        "height": container.get("height"),
    }


def inspect_pbix(path: Path) -> dict:
    with zipfile.ZipFile(path) as archive:
        layout = load_json_entry(archive, "Report/Layout")
        connections = load_json_entry(archive, "Connections")
        pages = []
        for index, section in enumerate(layout.get("sections", []), start=1):
            pages.append(
                {
                    "index": index,
                    "name": section.get("name"),
                    "display_name": section.get("displayName"),
                    "width": section.get("width"),
                    "height": section.get("height"),
                    "visuals": [
                        summarize_visual(item)
                        for item in section.get("visualContainers", [])
                    ],
                }
            )
        return {
            "file": str(path),
            "connections": connections,
            "page_count": len(pages),
            "pages": pages,
        }


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("pbix", type=Path)
    parser.add_argument("--json", action="store_true")
    args = parser.parse_args()
    result = inspect_pbix(args.pbix)
    if args.json:
        print(json.dumps(result, ensure_ascii=False, indent=2))
        return

    remote = result["connections"].get("RemoteArtifacts", [])
    print(f"PBIX: {result['file']}")
    print(f"Remote artifacts: {remote}")
    print(f"Pages: {result['page_count']}")
    for page in result["pages"]:
        print(
            f"\nPAGE {page['index']}: {page['display_name']} "
            f"({page['width']}x{page['height']})"
        )
        for visual in page["visuals"]:
            fields = ", ".join(visual["fields"]) or "-"
            print(f"  - {visual['type']}: {fields}")


if __name__ == "__main__":
    main()
