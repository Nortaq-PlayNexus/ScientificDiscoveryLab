from __future__ import annotations

import ast
import csv
import hashlib
import json
import os
import re
from collections import Counter
from datetime import datetime, timezone
from pathlib import Path

ROOT = Path(r"C:\Users\natha\ScientificDiscoveryLab")
OUT = ROOT / "AUDIT" / "INDEPENDENT_AUDIT_20260924"
OUT.mkdir(parents=True, exist_ok=True)
EXCLUDE_DIRS = {".git", "__pycache__", ".pytest_cache"}
TEXT_EXT = {".py", ".md", ".json", ".jsonl", ".txt", ".log", ".err", ".bat", ".ini", ".html", ".sha256"}
ID_RE = re.compile(r"\b(?:EXP-\d{4}|Q-[A-Z]+\d{3}|HYP-[A-Z0-9-]+)\b")


def sha256(path: Path) -> str:
    h = hashlib.sha256()
    with path.open("rb") as f:
        for chunk in iter(lambda: f.read(1024 * 1024), b""):
            h.update(chunk)
    return h.hexdigest()


def read_text(path: Path) -> str:
    try:
        return path.read_text(encoding="utf-8")
    except UnicodeDecodeError:
        return path.read_text(encoding="utf-8", errors="replace")


records = []
python_symbols = []
doc_ids = Counter()
for path in sorted(ROOT.rglob("*")):
    if not path.is_file():
        continue
    rel = path.relative_to(ROOT)
    if any(part in EXCLUDE_DIRS for part in rel.parts):
        continue
    # Do not recursively include this generated inventory in the source hash manifest.
    source_record = not (len(rel.parts) >= 3 and rel.parts[:3] == ("AUDIT", "INDEPENDENT_AUDIT_20260924", "inventory"))
    rec = {
        "path": rel.as_posix(),
        "extension": path.suffix.lower(),
        "size_bytes": path.stat().st_size,
        "mtime_utc": datetime.fromtimestamp(path.stat().st_mtime, timezone.utc).isoformat(),
        "sha256": sha256(path) if source_record else "",
    }
    records.append(rec)
    if path.suffix.lower() in TEXT_EXT and source_record:
        text = read_text(path)
        found_ids = sorted(set(ID_RE.findall(text)))
        for item in found_ids:
            doc_ids[item] += 1
        rec["mentioned_ids"] = found_ids
        if path.suffix.lower() == ".py":
            try:
                tree = ast.parse(text, filename=str(path))
                funcs = [n.name for n in ast.walk(tree) if isinstance(n, (ast.FunctionDef, ast.AsyncFunctionDef))]
                classes = [n.name for n in ast.walk(tree) if isinstance(n, ast.ClassDef)]
                imports = []
                for n in ast.walk(tree):
                    if isinstance(n, ast.Import):
                        imports.extend(a.name for a in n.names)
                    elif isinstance(n, ast.ImportFrom):
                        imports.append(n.module or "")
                python_symbols.append({
                    "path": rel.as_posix(),
                    "lines": text.count("\n") + 1,
                    "functions": funcs,
                    "classes": classes,
                    "imports": sorted(set(imports)),
                })
            except SyntaxError as exc:
                python_symbols.append({"path": rel.as_posix(), "syntax_error": str(exc)})

with (OUT / "file_manifest.json").open("w", encoding="utf-8") as f:
    json.dump({
        "generated_utc": datetime.now(timezone.utc).isoformat(),
        "root": str(ROOT),
        "record_count": len(records),
        "files": records,
    }, f, indent=2, ensure_ascii=False)

with (OUT / "file_manifest.csv").open("w", newline="", encoding="utf-8-sig") as f:
    w = csv.DictWriter(f, fieldnames=["path", "extension", "size_bytes", "mtime_utc", "sha256", "mentioned_ids"])
    w.writeheader()
    for r in records:
        rr = dict(r)
        rr["mentioned_ids"] = ";".join(rr.get("mentioned_ids", []))
        w.writerow(rr)

with (OUT / "python_symbols.json").open("w", encoding="utf-8") as f:
    json.dump(python_symbols, f, indent=2, ensure_ascii=False)

summary = {
    "generated_utc": datetime.now(timezone.utc).isoformat(),
    "file_count_excluding_caches": len(records),
    "total_bytes_excluding_caches": sum(r["size_bytes"] for r in records),
    "extensions": dict(Counter(r["extension"] or "<none>" for r in records)),
    "python_files_parsed": len(python_symbols),
    "python_syntax_errors": sum("syntax_error" in x for x in python_symbols),
    "id_mentions": dict(doc_ids.most_common()),
}
with (OUT / "inventory_summary.json").open("w", encoding="utf-8") as f:
    json.dump(summary, f, indent=2, ensure_ascii=False)
print(json.dumps(summary, indent=2))
