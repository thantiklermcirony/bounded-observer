"""Build a text-light research inventory from the September 2026 public Atlas.

Usage: python registry/legacy/build_inventory.py /path/to/boundedness-atlas/content/atlas.json

The source is intentionally an explicit input. It is not bundled here because it
contains full manuscript excerpts whose original publication terms are retained.
"""

from __future__ import annotations

import argparse
import hashlib
import json
import re
from pathlib import Path
from urllib.parse import urlparse


ROOT = Path(__file__).resolve().parents[2]
ATLAS_COMMIT = "29a0cfca16ac088cd08e0267b07a50c20eacbc9b"
ATLAS_BLOB = (
    "https://github.com/thantiklermcirony/boundedness-atlas/blob/"
    f"{ATLAS_COMMIT}/content/atlas.json"
)
PAPER_FIELDS = (
    "key", "title", "ssrn_id", "page_count", "sha256", "kind", "url",
    "role", "scope", "contribution", "evidence", "notice",
    "external_version_parity", "abstract_pages", "closing_pages",
)
PREDICTION_FIELDS = (
    "id", "domain", "title", "record_kind", "sources", "status",
    "next_test", "success_means", "failure_means", "depends_on",
    "source_pages", "caveat", "use_notice", "provenance",
)


def source_lines(raw: str) -> dict[str, int]:
    lines: dict[str, int] = {}
    pattern = re.compile(r'^\s+"(?:key|id)": "([^"]+)",?\s*$')
    for number, line in enumerate(raw.splitlines(), 1):
        match = pattern.match(line)
        if match:
            lines.setdefault(match.group(1), number)
    return lines


def inventory(source: Path) -> dict:
    raw_bytes = source.read_bytes()
    raw = raw_bytes.decode("utf-8")
    original = json.loads(raw)
    lines = source_lines(raw)
    papers = []
    for paper in original["papers"]:
        if not re.fullmatch(r"\d{7}", paper["ssrn_id"]):
            raise ValueError(f'Invalid SSRN ID in {paper["key"]}')
        parsed = urlparse(paper["url"])
        if (
            parsed.scheme != "https"
            or parsed.netloc not in {"ssrn.com", "www.ssrn.com", "papers.ssrn.com"}
            or paper["ssrn_id"] not in (parsed.path + parsed.query)
        ):
            raise ValueError(f'Invalid SSRN URL in {paper["key"]}')
        item = {key: paper[key] for key in PAPER_FIELDS if key in paper}
        item["indexed_pages"] = [entry["page"] for entry in paper["prediction_passages"]]
        item["original_source"] = f'{ATLAS_BLOB}#L{lines[paper["key"]]}'
        papers.append(item)
    predictions = []
    for group in ("families", "numbered_predictions"):
        for record in original[group]:
            item = {key: record[key] for key in PREDICTION_FIELDS if key in record}
            item["original_source"] = f'{ATLAS_BLOB}#L{lines[record["id"]]}'
            predictions.append(item)
    page_total = sum(len(paper["indexed_pages"]) for paper in papers)
    if (len(papers), len(predictions), page_total) != (41, 82, 471):
        raise ValueError("Unexpected historical inventory size")
    if len({paper["key"] for paper in papers}) != 41:
        raise ValueError("Duplicate paper key")
    if len({record["id"] for record in predictions}) != 82:
        raise ValueError("Duplicate prediction ID")
    paper_ids = {paper["ssrn_id"] for paper in papers}
    for record in predictions:
        if any(source_id not in paper_ids for source_id in record["sources"]):
            raise ValueError(f'Unknown source in {record["id"]}')
    return {
        "title": "Research library · September 2026 source inventory",
        "as_of": original["as_of"],
        "source_repository": f"https://github.com/thantiklermcirony/boundedness-atlas/tree/{ATLAS_COMMIT}",
        "source_file": ATLAS_BLOB,
        "source_sha256": hashlib.sha256(raw_bytes).hexdigest(),
        "scope": "Dated public source inventory. Author-reported statuses and claims have not been independently reverified by this transfer. Online SSRN revisions may differ.",
        "coverage": original["coverage"],
        "papers": papers,
        "predictions": predictions,
    }


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("source", type=Path)
    args = parser.parse_args()
    data = inventory(args.source)
    encoded = json.dumps(data, ensure_ascii=False, indent=2) + "\n"
    destinations = (
        ROOT / "registry" / "legacy" / "atlas-2026-09.json",
        ROOT / "site" / "library-data.json",
    )
    for destination in destinations:
        destination.write_text(encoded, encoding="utf-8")
    print(
        f'Wrote {len(data["papers"])} manuscripts, '
        f'{len(data["predictions"])} prediction records, '
        f'{sum(len(p["indexed_pages"]) for p in data["papers"])} indexed pages.'
    )


if __name__ == "__main__":
    main()
