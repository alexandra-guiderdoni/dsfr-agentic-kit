"""Relier une tentative de collecte à ses entrées et sorties sans modifier AY11."""

import hashlib
import json
from pathlib import Path


def digest(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def write_binding(root: Path, destination: Path, page: str, inputs: list[Path]) -> None:
    files = [*inputs, *destination.rglob("*.json")]
    payload = {
        "schema_version": 1,
        "page": page,
        "inputs": [str(path.relative_to(root)) for path in inputs],
        "files": {
            str(path.relative_to(root)): digest(path)
            for path in files
            if path.name != "source-identity.json"
        },
    }
    (destination / "source-identity.json").write_text(
        json.dumps(payload, ensure_ascii=False, indent=2) + "\n", encoding="utf-8"
    )


def binding_status(root: Path, destination: Path, page: str, state: dict) -> str:
    """Une preuve ancienne sans liaison reste découverte, jamais créditée à l'état courant."""
    source = destination / "source-identity.json"
    if not source.is_file():
        return "identity_unknown"
    try:
        payload = json.loads(source.read_text())
        if payload.get("page") != page:
            return "page_mismatch"
        if state.get("collect_dir") != str(destination.relative_to(root)):
            return "collection_not_selected"
        capture = state.get("capture_dir")
        if not capture or not payload.get("inputs") or not payload.get("files"):
            return "capture_unknown"
        for rel in payload["inputs"]:
            if Path(rel).parent != Path(capture):
                return "capture_mismatch"
        for rel, expected in payload["files"].items():
            path = (root / rel).resolve()
            if not path.is_relative_to(root.resolve()) or digest(path) != expected:
                return "artifact_mismatch"
        actual = {
            str(path.relative_to(root))
            for path in destination.rglob("*.json")
            if path != source
        }
        if not actual.issubset(payload["files"]):
            return "unbound_artifact"
    except (OSError, ValueError, TypeError, KeyError):
        return "invalid_identity"
    return "consumed"
