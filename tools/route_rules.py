"""Shared approved redirect rules, used by production and build validation."""
import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
REDIRECTS = json.loads((ROOT / "site/redirects.json").read_text())
assert len(REDIRECTS) == 13
assert not set(REDIRECTS) & set(REDIRECTS.values()), "Redirect chain/loop"
assert all(p.startswith("/") and p.endswith("/") and not p.startswith("//")
           and ".." not in p for p in list(REDIRECTS) + list(REDIRECTS.values()))


def merged_target(path):
    """Canonical, slashless and explicit-index variants all resolve directly."""
    if path.endswith("/index.html"):
        path = path[:-len("index.html")]
    return REDIRECTS.get(path if path.endswith("/") else path + "/")