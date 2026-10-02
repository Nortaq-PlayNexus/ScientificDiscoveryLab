"""Second-pass whole-laboratory anomaly scanner.

Read-only with respect to historical project files. Writes JSON/CSV/Markdown
summaries only under AUDIT/CROSS_PROJECT_ANOMALY_SCAN_20260924/.
"""
from __future__ import annotations

import ast
import collections
import datetime as dt
import hashlib
import json
import math
import os
import re
from pathlib import Path
from typing import Any

import numpy as np

ROOT = Path(r"C:\Users\natha\ScientificDiscoveryLab")
OUT = ROOT / "AUDIT" / "CROSS_PROJECT_ANOMALY_SCAN_20260924"
OUT.mkdir(parents=True, exist_ok=True)
EXCLUDE_PARTS = {"__pycache__", ".git", ".pytest_cache"}
EXCLUDE_PREFIXES = (
    "AUDIT/CROSS_PROJECT_ANOMALY_SCAN_20260924/",
    "AUDIT/PRIOR_AUDIT_20260923/",
)

TEXT_EXTS = {".py", ".md", ".json", ".jsonl", ".txt", ".log", ".err", ".csv", ".ini", ".bat", ".html"}
KNOWN_COMMON_DECIMALS = {
    "0.00000000", "1.00000000", "0.00000001", "0.00000010",
}


def included(path: Path) -> bool:
    rel = path.relative_to(ROOT).as_posix()
    return not any(part in EXCLUDE_PARTS for part in path.parts) and not rel.startswith(EXCLUDE_PREFIXES)


def files_under(root: Path):
    for p in root.rglob("*"):
        if p.is_file() and included(p):
            yield p


def sha256(path: Path) -> str:
    h = hashlib.sha256()
    with path.open("rb") as f:
        for block in iter(lambda: f.read(1 << 20), b""):
            h.update(block)
    return h.hexdigest()


def flatten(obj: Any, path: str = "$"):
    if isinstance(obj, dict):
        for k, v in obj.items():
            yield from flatten(v, f"{path}/{k}")
    elif isinstance(obj, list):
        for i, v in enumerate(obj):
            yield from flatten(v, f"{path}/{i}")
    else:
        yield path, obj


def json_kind(obj: Any, name: str) -> str:
    keys = set(obj.keys()) if isinstance(obj, dict) else set()
    if {"decision", "experiment"} & keys or "exponents" in keys or "cells" in keys:
        return "result-like"
    if any(x in name.lower() for x in ("result", "summary", "combined", "experiment", "metrics")):
        return "result-name"
    return "other-json"


def ast_findings(path: Path) -> list[dict]:
    findings: list[dict] = []
    try:
        text = path.read_text(encoding="utf-8-sig")
        tree = ast.parse(text)
    except Exception as e:
        return [{"kind": "parse-error", "path": path.relative_to(ROOT).as_posix(), "detail": repr(e)}]
    rel = path.relative_to(ROOT).as_posix()
    # Suspicious hard-coded decision/result strings and writer patterns.
    for node in ast.walk(tree):
        if isinstance(node, ast.Constant) and isinstance(node.value, str):
            s = node.value
            if re.search(r"H0_SUPPORTED|LATTICE_ARTIFACT|CERTIFIED|H1_SUPPORTED|INCONCLUSIVE|ABNORMAL", s, re.I):
                findings.append({"kind": "decision-string-literal", "path": rel, "line": node.lineno, "detail": s})
            if re.search(r"hardcod|synthetic|assumed|placeholder|dummy|fake|not implemented", s, re.I):
                findings.append({"kind": "suspicious-literal", "path": rel, "line": node.lineno, "detail": s[:240]})
        if isinstance(node, ast.Call) and isinstance(node.func, ast.Name):
            if node.func.id in {"eval", "exec"}:
                findings.append({"kind": "dynamic-exec", "path": rel, "line": node.lineno, "detail": node.func.id})
        if isinstance(node, ast.Assign):
            # Numeric assignments to result-like names are a review target, not a verdict.
            for target in node.targets:
                if isinstance(target, ast.Name) and re.search(r"result|decision|verdict|expected|threshold|p_value|pval|delta|tau|exponent", target.id, re.I):
                    if isinstance(node.value, ast.Constant) and isinstance(node.value.value, (int, float, str, bool)):
                        findings.append({"kind": "constant-result-assignment", "path": rel, "line": node.lineno, "detail": f"{target.id}={node.value.value!r}"})
    # Detect obvious no-op control branches.
    for node in ast.walk(tree):
        if isinstance(node, ast.If):
            body = node.body
            if len(body) == 1 and isinstance(body[0], ast.Pass):
                findings.append({"kind": "empty-if-pass", "path": rel, "line": node.lineno, "detail": ast.unparse(node.test)[:200]})
    return findings


def scan_json(path: Path) -> tuple[dict | None, list[dict]]:
    rel = path.relative_to(ROOT).as_posix()
    try:
        obj = json.loads(path.read_text(encoding="utf-8-sig"))
    except Exception as e:
        return None, [{"kind": "json-parse-error", "path": rel, "detail": repr(e)}]
    issues: list[dict] = []
    for jp, value in flatten(obj):
        lname = jp.rsplit("/", 1)[-1].lower()
        if isinstance(value, float):
            if not math.isfinite(value):
                issues.append({"kind": "nonfinite-number", "path": rel, "json_path": jp, "detail": repr(value)})
            if ("p" == lname or "pvalue" in lname or lname.startswith("p_") or lname.endswith("_p")) and not (0 <= value <= 1):
                issues.append({"kind": "p-value-out-of-range", "path": rel, "json_path": jp, "detail": value})
            if any(x in lname for x in ("se", "std", "sigma", "uncertainty")) and value < 0:
                issues.append({"kind": "negative-uncertainty", "path": rel, "json_path": jp, "detail": value})
            if lname.endswith("_p") and value in (0.0, 1.0):
                issues.append({"kind": "exact-boundary-p-value", "path": rel, "json_path": jp, "detail": value})
        if isinstance(value, list) and len(value) == 2 and all(isinstance(x, (int, float)) for x in value):
            lo, hi = value
            if "ci" in lname or "interval" in lname or "range" in lname:
                if lo > hi:
                    issues.append({"kind": "reversed-ci", "path": rel, "json_path": jp, "detail": value})
    return obj, issues


def npz_summary(path: Path) -> dict:
    rel = path.relative_to(ROOT).as_posix()
    out = {"path": rel, "sha256": sha256(path), "keys": [], "arrays": {}, "errors": []}
    try:
        z = np.load(path, allow_pickle=True)
        out["keys"] = list(z.files)
        for k in z.files:
            a = z[k]
            info = {"shape": list(a.shape), "dtype": str(a.dtype), "size": int(a.size)}
            if a.dtype == object:
                info["object_lengths"] = [len(x) if hasattr(x, "__len__") else None for x in a.flat[:20]]
            out["arrays"][k] = info
    except Exception as e:
        out["errors"].append(repr(e))
    return out


def main() -> None:
    all_files = list(files_under(ROOT))
    by_ext = collections.Counter(p.suffix.lower() or "<none>" for p in all_files)
    hashes: dict[str, list[str]] = collections.defaultdict(list)
    for p in all_files:
        hashes[sha256(p)].append(p.relative_to(ROOT).as_posix())
    duplicate_groups = [{"sha256": h, "paths": paths} for h, paths in hashes.items() if len(paths) > 1]

    json_files = [p for p in all_files if p.suffix.lower() in {".json", ".jsonl"}]
    json_infos = []
    json_issues = []
    id_occurrences: dict[str, list[str]] = collections.defaultdict(list)
    id_pattern = re.compile(r"\b(?:EXP|HYP|Q)-[A-Z0-9-]+\b", re.I)
    for p in all_files:
        if p.suffix.lower() not in TEXT_EXTS:
            continue
        try:
            text = p.read_text(encoding="utf-8-sig", errors="replace")
        except Exception:
            continue
        rel = p.relative_to(ROOT).as_posix()
        for ident in id_pattern.findall(text):
            id_occurrences[ident.upper()].append(rel)
        if p in json_files:
            obj, issues = scan_json(p)
            json_issues.extend(issues)
            json_infos.append({"path": rel, "kind": json_kind(obj, p.name) if obj is not None else "parse-error", "sha256": sha256(p)})

    ast_issues = []
    for p in all_files:
        if p.suffix.lower() == ".py":
            ast_issues.extend(ast_findings(p))

    npz = [npz_summary(p) for p in all_files if p.suffix.lower() == ".npz"]

    # Chronology: result-like files vs nearby source/config files.
    chronology = []
    for info in json_infos:
        if info["kind"] not in {"result-like", "result-name"}:
            continue
        rp = ROOT / info["path"]
        parent = rp.parent
        siblings = [p for p in parent.rglob("*") if p.is_file() and p.suffix.lower() in {".py", ".json", ".md"} and p != rp]
        older_code = [p.relative_to(ROOT).as_posix() for p in siblings if p.stat().st_mtime > rp.stat().st_mtime]
        chronology.append({"result": info["path"], "mtime": dt.datetime.fromtimestamp(rp.stat().st_mtime, dt.timezone.utc).isoformat(), "newer_sibling_count": len(older_code), "newer_siblings_sample": older_code[:20]})

    # Repeated long decimal literals across unrelated files.
    decimal_re = re.compile(r"(?<![A-Za-z0-9])[-+]?\d+\.\d{8,}(?![A-Za-z0-9])")
    decimal_occurrences: dict[str, list[str]] = collections.defaultdict(list)
    for p in all_files:
        if p.suffix.lower() not in TEXT_EXTS:
            continue
        text = p.read_text(encoding="utf-8-sig", errors="replace")
        for token in decimal_re.findall(text):
            if token not in KNOWN_COMMON_DECIMALS:
                decimal_occurrences[token].append(p.relative_to(ROOT).as_posix())
    repeated_decimals = [{"value": k, "paths": sorted(set(v)), "count": len(v)} for k, v in decimal_occurrences.items() if len(set(v)) >= 2]
    repeated_decimals.sort(key=lambda x: (-x["count"], x["value"]))

    # IDs that occur in multiple top-level investigations.
    id_collisions = []
    for ident, paths in sorted(id_occurrences.items()):
        domains = {p.split("/")[2] if p.startswith("03_INVESTIGATIONS/") and len(p.split("/")) > 2 else p.split("/")[0] for p in paths}
        if len(domains) > 1:
            id_collisions.append({"id": ident, "domains": sorted(domains), "paths": sorted(set(paths))})

    # Text markers that deserve manual review, with paths/lines.
    marker_re = re.compile(r"hardcod|synthetic|assumed|placeholder|dummy|fake|not implemented|TODO|FIXME|pending|post-hoc|after the fact", re.I)
    markers = []
    for p in all_files:
        if p.suffix.lower() not in TEXT_EXTS:
            continue
        for i, line in enumerate(p.read_text(encoding="utf-8-sig", errors="replace").splitlines(), 1):
            if marker_re.search(line):
                markers.append({"path": p.relative_to(ROOT).as_posix(), "line": i, "text": line.strip()[:300]})

    result = {
        "generated_utc": dt.datetime.now(dt.timezone.utc).isoformat(),
        "scope": "whole laboratory, excluding caches, this scan, and preserved prior audit copy",
        "file_count": len(all_files),
        "total_bytes": sum(p.stat().st_size for p in all_files),
        "extensions": dict(sorted(by_ext.items())),
        "duplicate_hash_groups": duplicate_groups,
        "json_file_count": len(json_files),
        "json_result_like_count": sum(x["kind"] == "result-like" for x in json_infos),
        "json_issues": json_issues,
        "ast_issues": ast_issues,
        "npz_files": npz,
        "chronology": chronology,
        "id_collisions": id_collisions,
        "repeated_long_decimals": repeated_decimals[:500],
        "review_markers": markers,
    }
    (OUT / "whole_lab_scan.json").write_text(json.dumps(result, indent=2, default=str), encoding="utf-8")
    # Compact summaries for quick human review.
    lines = [
        "# Whole-laboratory anomaly scan",
        "",
        f"Generated: `{result['generated_utc']}`",
        "",
        "## Counts",
        f"- Files scanned: **{result['file_count']}**",
        f"- Bytes scanned: **{result['total_bytes']}**",
        f"- JSON files: **{result['json_file_count']}** ({result['json_result_like_count']} result-like)",
        f"- Duplicate hash groups: **{len(duplicate_groups)}**",
        f"- AST review findings: **{len(ast_issues)}**",
        f"- JSON numerical/format issues: **{len(json_issues)}**",
        "",
        "## Highest-signal categories",
        "### ID collisions",
    ]
    lines += [f"- `{x['id']}`: {', '.join(x['domains'])}" for x in id_collisions] or ["- None"]
    lines += ["", "### Repeated long decimal literals"]
    lines += [f"- `{x['value']}` in {x['count']} files: {', '.join(x['paths'][:5])}" for x in repeated_decimals[:50]] or ["- None"]
    lines += ["", "### Review markers"]
    lines += [f"- `{x['path']}:{x['line']}` — {x['text']}" for x in markers[:100]] or ["- None"]
    (OUT / "whole_lab_scan.md").write_text("\n".join(lines) + "\n", encoding="utf-8")
    print(json.dumps({k: result[k] for k in ("file_count", "total_bytes", "json_file_count", "json_result_like_count", "duplicate_hash_groups", "ast_issues", "json_issues", "id_collisions", "repeated_long_decimals", "review_markers")}, indent=2, default=str))


if __name__ == "__main__":
    main()
