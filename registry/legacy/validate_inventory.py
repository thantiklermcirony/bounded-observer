"""Validate the carried-over September 2026 source inventory and site copy."""

from __future__ import annotations

import json
import re
from pathlib import Path
from urllib.parse import urlparse


ROOT = Path(__file__).resolve().parents[2]
CANONICAL = ROOT / "registry" / "legacy" / "atlas-2026-09.json"
SITE_COPY = ROOT / "site" / "library-data.json"
COMMIT = "29a0cfca16ac088cd08e0267b07a50c20eacbc9b"
SOURCE_PREFIX = (
    "https://github.com/thantiklermcirony/boundedness-atlas/blob/"
    f"{COMMIT}/content/atlas.json#L"
)
FORBIDDEN = {"abstract", "closing", "source_text", "prediction_passages"}


def valid_url(url: str, *, hosts: set[str]) -> bool:
    parsed = urlparse(url)
    return parsed.scheme == "https" and parsed.netloc in hosts and bool(parsed.path)


def validate() -> None:
    assert CANONICAL.read_bytes() == SITE_COPY.read_bytes(), "Site inventory differs from canonical copy"
    data = json.loads(CANONICAL.read_text(encoding="utf-8"))
    papers, predictions = data["papers"], data["predictions"]
    assert data["as_of"] == "2026-09-13"
    assert (len(papers), len(predictions)) == (41, 82)
    assert sum(len(paper["indexed_pages"]) for paper in papers) == 471
    assert len({paper["key"] for paper in papers}) == 41
    assert len({paper["ssrn_id"] for paper in papers}) == 41
    assert len({prediction["id"] for prediction in predictions}) == 82
    assert sum(prediction["record_kind"] == "Research family" for prediction in predictions) == 41
    assert sum(prediction["record_kind"] == "Original numbered prediction" for prediction in predictions) == 41
    assert re.fullmatch(r"[0-9a-f]{64}", data["source_sha256"])
    assert valid_url(data["source_file"], hosts={"github.com"})
    assert COMMIT in data["source_file"]
    ssrn_ids = {paper["ssrn_id"] for paper in papers}
    page_counts = {paper["ssrn_id"]: paper["page_count"] for paper in papers}
    for paper in papers:
        assert not FORBIDDEN.intersection(paper)
        assert re.fullmatch(r"\d{7}", paper["ssrn_id"])
        assert re.fullmatch(r"[0-9a-f]{64}", paper["sha256"])
        assert valid_url(paper["url"], hosts={"ssrn.com", "www.ssrn.com", "papers.ssrn.com"})
        parsed_paper_url = urlparse(paper["url"])
        assert paper["ssrn_id"] in (parsed_paper_url.path + parsed_paper_url.query)
        assert paper["original_source"].startswith(SOURCE_PREFIX)
        assert re.fullmatch(r"\d+", paper["original_source"][len(SOURCE_PREFIX):])
        assert all(isinstance(page, int) and 1 <= page <= paper["page_count"] for page in paper["indexed_pages"])
    for prediction in predictions:
        assert not FORBIDDEN.intersection(prediction)
        assert prediction["original_source"].startswith(SOURCE_PREFIX)
        assert re.fullmatch(r"\d+", prediction["original_source"][len(SOURCE_PREFIX):])
        assert prediction["sources"] and all(source in ssrn_ids for source in prediction["sources"])
        assert prediction["next_test"] and prediction["failure_means"]
        for source, pages in prediction["source_pages"].items():
            assert source in ssrn_ids
            assert all(isinstance(page, int) and 1 <= page <= page_counts[source] for page in pages)
    print("Inventory valid: 41 manuscripts, 82 predictions, 471 indexed pages; site copy identical.")


if __name__ == "__main__":
    validate()
