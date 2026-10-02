from __future__ import annotations

import ast
import hashlib
import json
import os
import re
from collections import Counter, defaultdict
from pathlib import Path
from typing import Any

ROOT = Path(__file__).resolve().parents[3]
OUT = Path(__file__).resolve().parent
TEXT_EXT = {".md", ".txt", ".log", ".err", ".py", ".json", ".jsonl", ".csv", ".html", ".ini", ".bat", ".sha256"}
SKIP_DIRS = {".git", ".pytest_cache", "__pycache__", "agent_claims_data"}
HEX64 = re.compile(r"(?<![0-9a-f])[0-9a-f]{64}(?![0-9a-f])", re.I)
EXP_RE = re.compile(r"\bEXP-\d{3,5}\b")
Q_RE = re.compile(r"\bQ-[A-Z0-9-]+\b")
HYP_RE = re.compile(r"\bHYP-[A-Z0-9-]+\b")
CLAIM_RE = re.compile(r"(?i)\b(certif(?:ied|ication)|discover(?:y|ies)|novel|proof|prove[sd]?|reproduced|reproduce[sd]?|H[01]_SUPPORTED|COMPLETE|RESOLVED|confirmed|artifact|independent|raw data|not a finite|asymptotic|100%)\b")


def rel(p: Path) -> str:
    return p.relative_to(ROOT).as_posix()


def files() -> list[Path]:
    out = []
    for p in ROOT.rglob("*"):
        if not p.is_file():
            continue
        if any(part in SKIP_DIRS for part in p.relative_to(ROOT).parts):
            continue
        out.append(p)
    return sorted(out)


def sha(p: Path) -> str:
    h = hashlib.sha256()
    with p.open("rb") as f:
        for b in iter(lambda: f.read(1024 * 1024), b""):
            h.update(b)
    return h.hexdigest()


def text(p: Path) -> str:
    try:
        return p.read_text(encoding="utf-8-sig", errors="replace")
    except Exception:
        return ""


def walk_strings(x: Any, path: str = "$"):
    if isinstance(x, dict):
        for k, v in x.items():
            yield from walk_strings(v, f"{path}.{k}")
    elif isinstance(x, list):
        for i, v in enumerate(x):
            yield from walk_strings(v, f"{path}[{i}]")
    elif isinstance(x, str):
        yield path, x


def parse_json(p: Path) -> tuple[Any | None, str | None]:
    try:
        return json.loads(text(p)), None
    except Exception as e:
        return None, f"{type(e).__name__}: {e}"


def likely_result_paths(p: Path) -> list[Path]:
    # Search nearby result files, preferring the investigation's RESULTS directories.
    parent = p.parent
    roots = [parent, parent.parent, parent.parent.parent]
    candidates = []
    for r in roots:
        if r.exists():
            candidates.extend(r.rglob("*"))
    return [q for q in candidates if q.is_file() and q.suffix.lower() in {".json", ".npz", ".csv"} and "CONFIG" not in q.parts]


def main() -> None:
    fs = files()
    report: dict[str, Any] = {
        "root": str(ROOT),
        "file_count_excluding_output_and_caches": len(fs),
        "extensions": dict(Counter(p.suffix.lower() for p in fs)),
        "json_parse": [],
        "hash_groups": {},
        "result_hash_checks": [],
        "id_definitions": {"EXP": {}, "Q": {}, "HYP": {}},
        "id_references": {"EXP": defaultdict(list), "Q": defaultdict(list), "HYP": defaultdict(list)},
        "claim_hits": [],
        "missing_path_references": [],
        "prereg_files": [],
        "code_signals": [],
        "npz_files": [],
    }

    # Duplicate byte hashes (nontrivial only; empty init files and audit copies are still useful separately).
    by_hash: dict[str, list[Path]] = defaultdict(list)
    hash_cache: dict[Path, str] = {}
    for p in fs:
        try:
            h = sha(p)
            hash_cache[p] = h
            by_hash[h].append(p)
        except Exception:
            pass
    for h, ps in sorted(by_hash.items(), key=lambda kv: (-len(kv[1]), kv[0])):
        if len(ps) > 1:
            report["hash_groups"][h] = [rel(p) for p in ps]

    # Parse JSON and collect IDs, hashes, and claim-like strings.
    for p in fs:
        s = text(p)
        rp = rel(p)
        for rx, target in ((EXP_RE, "EXP"), (Q_RE, "Q"), (HYP_RE, "HYP")):
            for m in rx.finditer(s):
                report["id_references"][target][m.group(0)].append({"path": rp, "offset": m.start()})
        if p.suffix.lower() == ".json":
            obj, err = parse_json(p)
            if err:
                report["json_parse"].append({"path": rp, "error": err})
            else:
                for jp, val in walk_strings(obj):
                    if re.search(r"(?i)(hash|sha256|checksum)", jp):
                        hs = HEX64.findall(val)
                        for h in hs:
                            report["result_hash_checks"].append({"config_path": rp, "json_path": jp, "recorded_hash": h.lower()})
        # Definitions in filenames or explicit experiment_id/question_id keys.
        for rx, target in ((EXP_RE, "EXP"), (Q_RE, "Q"), (HYP_RE, "HYP")):
            for token in set(rx.findall(p.name)):
                report["id_definitions"][target].setdefault(token, []).append(rp)
        if p.suffix.lower() in {".md", ".txt", ".log", ".err"}:
            # Capture lines with strong claim/status language; cap per file.
            hits = []
            for i, line in enumerate(s.splitlines(), 1):
                if CLAIM_RE.search(line):
                    hits.append({"line": i, "text": line.strip()[:500]})
            if hits:
                report["claim_hits"].append({"path": rp, "hits": hits[:80], "hit_count": len(hits)})

        if p.suffix.lower() in {".json", ".jsonl"} and re.search(r"(?i)prereg", p.name):
            report["prereg_files"].append({"path": rp, "mtime": p.stat().st_mtime, "size": p.stat().st_size})

    # JSON field definitions from parsed objects.
    for p in fs:
        if p.suffix.lower() != ".json":
            continue
        obj, err = parse_json(p)
        if err:
            continue
        rp = rel(p)
        if isinstance(obj, dict):
            for key, target in (("experiment_id", "EXP"), ("question_id", "Q"), ("hypothesis_id", "HYP"), ("question", "Q"), ("hypothesis", "HYP")):
                val = obj.get(key)
                if isinstance(val, str) and (EXP_RE.fullmatch(val) or Q_RE.fullmatch(val) or HYP_RE.fullmatch(val)):
                    report["id_definitions"][target].setdefault(val, []).append(rp)

    # Resolve recorded hashes against nearby result artifacts. Exact filename/hash matches are strong;
    # otherwise retain candidates for manual review.
    hash_to_paths: dict[str, list[Path]] = defaultdict(list)
    for h, ps in by_hash.items():
        hash_to_paths[h] = ps
    for item in report["result_hash_checks"]:
        h = item["recorded_hash"]
        item["exact_file_matches"] = [rel(p) for p in hash_to_paths.get(h, [])][:20]
    # Add likely result-file hash checks for common result_hash fields.
    for p in fs:
        if p.suffix.lower() != ".json":
            continue
        obj, err = parse_json(p)
        if err or not isinstance(obj, dict):
            continue
        for key, val in obj.items():
            if not isinstance(val, str) or not HEX64.fullmatch(val):
                continue
            if not re.search(r"(?i)(result|output|artifact).*hash|hash.*(result|output|artifact)", key):
                continue
            h = val.lower()
            matches = [rel(q) for q in hash_to_paths.get(h, [])]
            report["result_hash_checks"].append({"config_path": rel(p), "json_path": "$." + key, "recorded_hash": h, "exact_file_matches": matches})

    # Extract path-like backtick references and flag missing local paths, excluding URLs/globs/IDs.
    path_rx = re.compile(r"`([^`\n]{3,300})`")
    for p in fs:
        if p.suffix.lower() not in TEXT_EXT:
            continue
        s = text(p)
        for i, line in enumerate(s.splitlines(), 1):
            for ref in path_rx.findall(line):
                if any(x in ref for x in ("http://", "https://", "<", ">", "*", "EXP-", "Q-", "HYP-", "...")):
                    continue
                ref2 = ref.strip().replace("\\", "/")
                if ref2.startswith("./"):
                    ref2 = ref2[2:]
                # Skip prose with spaces unless it looks path-like.
                if ("/" not in ref2 and "\\" not in ref2) or " " in ref2:
                    continue
                q = ROOT / ref2
                if not q.exists():
                    report["missing_path_references"].append({"path": rel(p), "line": i, "reference": ref})

    # Static signals in code and helper scripts.
    signal_rx = re.compile(r"(?i)(hardcod|synthetic|simulate|assumed|default_rng|np\.random|Generator\(|seed|json\.dump|write_text|to_csv|savefig|RESULTS|registry)")
    for p in fs:
        if p.suffix.lower() not in {".py", ".bat"}:
            continue
        s = text(p)
        hits = []
        for i, line in enumerate(s.splitlines(), 1):
            if signal_rx.search(line):
                hits.append({"line": i, "text": line.strip()[:400]})
        if hits:
            report["code_signals"].append({"path": rel(p), "hits": hits[:200], "hit_count": len(hits)})

    # NPZ inventory: keys/shapes and exact duplicate groups.
    try:
        import numpy as np
        for p in fs:
            if p.suffix.lower() != ".npz":
                continue
            try:
                z = np.load(p, allow_pickle=False)
                arrays = []
                for k in z.files:
                    a = z[k]
                    arrays.append({"key": k, "shape": list(a.shape), "dtype": str(a.dtype), "sha256": hashlib.sha256(a.tobytes()).hexdigest()})
                z.close()
                report["npz_files"].append({"path": rel(p), "arrays": arrays})
            except Exception as e:
                report["npz_files"].append({"path": rel(p), "error": str(e)})
    except Exception as e:
        report["npz_error"] = str(e)

    # Make defaultdict JSON-safe.
    report["id_references"] = {k: dict(v) for k, v in report["id_references"].items()}
    report["id_definitions"] = {k: dict(sorted(v.items())) for k, v in report["id_definitions"].items()}
    report["missing_path_references"] = report["missing_path_references"][:500]
    report["result_hash_checks"] = report["result_hash_checks"][:2000]
    report["prereg_files"] = sorted(report["prereg_files"], key=lambda x: x["path"])
    out = OUT / "scan_output.json"
    out.write_text(json.dumps(report, indent=2, ensure_ascii=False, default=str), encoding="utf-8")
    print(json.dumps({"output": str(out), "files": len(fs), "json_parse_errors": len(report["json_parse"]), "duplicate_hash_groups": len(report["hash_groups"]), "claim_files": len(report["claim_hits"]), "missing_refs": len(report["missing_path_references"])}, indent=2))


if __name__ == "__main__":
    main()
