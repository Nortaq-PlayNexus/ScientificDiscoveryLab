"""Read-only static/provenance scan for the cross-project audit.

This script writes only inside the agent audit directory.  It does not execute
historical experiment code and does not modify source, result, registry, or
report files.
"""
from __future__ import annotations

import ast
import csv
import datetime as dt
import hashlib
import json
import os
import re
import sys
from collections import defaultdict, Counter
from pathlib import Path
from typing import Any

ROOT = Path(__file__).resolve().parents[3]
OUT = Path(__file__).resolve().parent
EXCLUDE_DIRS = {".git", ".pytest_cache", "__pycache__", "agent_static_provenance"}
TEXT_EXTS = {".py", ".md", ".json", ".jsonl", ".txt", ".yaml", ".yml", ".ini", ".bat", ".html", ".log", ".err", ".csv"}
RESULT_EXTS = {".json", ".csv", ".npz", ".png", ".txt", ".log", ".err", ".db", ".rar"}


def rel(p: Path) -> str:
    return p.relative_to(ROOT).as_posix()


def excluded(p: Path) -> bool:
    try:
        parts = p.relative_to(ROOT).parts
    except ValueError:
        return True
    return any(part in EXCLUDE_DIRS for part in parts)


def sha256(p: Path) -> str:
    h = hashlib.sha256()
    with p.open("rb") as f:
        for b in iter(lambda: f.read(1024 * 1024), b""):
            h.update(b)
    return h.hexdigest()


def jsonable(x: Any) -> Any:
    if isinstance(x, (str, int, float, bool)) or x is None:
        return x
    if isinstance(x, dict):
        return {str(k): jsonable(v) for k, v in x.items()}
    if isinstance(x, (list, tuple)):
        return [jsonable(v) for v in x]
    return str(x)


def canonical_json(obj: Any) -> str:
    return json.dumps(obj, sort_keys=True, ensure_ascii=False, separators=(",", ":"), default=str)


def source_line(path: Path, line: int) -> str:
    try:
        return path.read_text(encoding="utf-8-sig", errors="replace").splitlines()[line - 1].strip()
    except Exception:
        return ""


def expr_text(node: ast.AST | None) -> str:
    if node is None:
        return ""
    try:
        return ast.unparse(node)
    except Exception:
        return type(node).__name__


def literalish(node: ast.AST | None) -> bool:
    if node is None:
        return False
    if isinstance(node, (ast.Constant, ast.List, ast.Tuple, ast.Dict, ast.Set)):
        return True
    # A dict/list assembled entirely from constants is a hardcoded payload.
    if isinstance(node, (ast.Dict, ast.List, ast.Tuple, ast.Set)):
        return all(literalish(k) and literalish(v) for k, v in ast.walk(node) if isinstance(k, ast.AST)) if isinstance(node, ast.Dict) else all(literalish(x) for x in ast.walk(node) if isinstance(x, ast.AST))
    return False


def date_from_text(text: str) -> list[str]:
    # Capture ISO dates and common date forms; do not infer missing dates.
    pats = [r"\b20\d{2}-\d{2}-\d{2}(?:T[^\s,;\"}]+)?", r"\b20\d{2}/\d{2}/\d{2}\b"]
    out = []
    for pat in pats:
        out.extend(re.findall(pat, text))
    return sorted(set(out))


def call_name(node: ast.Call) -> str:
    f = node.func
    if isinstance(f, ast.Name):
        return f.id
    if isinstance(f, ast.Attribute):
        return f.attr
    return ""


def enclosing_function(tree: ast.AST) -> dict[int, str]:
    result: dict[int, str] = {}
    for n in ast.walk(tree):
        if isinstance(n, (ast.FunctionDef, ast.AsyncFunctionDef)):
            for child in ast.walk(n):
                if hasattr(child, "lineno"):
                    result[child.lineno] = n.name
    return result


def main() -> None:
    files: list[Path] = []
    for p in ROOT.rglob("*"):
        if p.is_file() and not excluded(p):
            files.append(p)
    files.sort(key=rel)

    inventory = []
    hash_groups: dict[str, list[str]] = defaultdict(list)
    text_records = []
    for p in files:
        try:
            st = p.stat()
            b = p.read_bytes()
            h = hashlib.sha256(b).hexdigest()
            rec = {
                "path": rel(p), "size": len(b), "sha256": h,
                "mtime": dt.datetime.fromtimestamp(st.st_mtime, dt.timezone.utc).isoformat(),
                "suffix": p.suffix.lower(),
            }
            inventory.append(rec)
            hash_groups[h].append(rel(p))
            if p.suffix.lower() in TEXT_EXTS or p.suffix == "":
                try:
                    text = b.decode("utf-8-sig")
                    text_records.append((p, text))
                except UnicodeDecodeError:
                    pass
        except Exception as e:
            inventory.append({"path": rel(p), "error": repr(e)})

    dup_files = [{"sha256": h, "paths": ps} for h, ps in sorted(hash_groups.items()) if len(ps) > 1]

    json_valid = []
    json_invalid = []
    json_objects: dict[str, Any] = {}
    json_by_file: dict[str, Any] = {}
    jsonl_records = []
    for p, text in text_records:
        rp = rel(p)
        if p.suffix.lower() == ".json":
            try:
                obj = json.loads(text)
                json_valid.append(rp)
                json_by_file[rp] = obj
                json_objects.setdefault(canonical_json(obj), []).append(rp)
            except Exception as e:
                json_invalid.append({"path": rp, "error": f"{type(e).__name__}: {e}", "prefix": text[:180]})
        elif p.suffix.lower() == ".jsonl":
            for i, line in enumerate(text.splitlines(), 1):
                if not line.strip():
                    continue
                try:
                    obj = json.loads(line)
                    jsonl_records.append({"path": rp, "line": i, "value": jsonable(obj)})
                except Exception as e:
                    jsonl_records.append({"path": rp, "line": i, "invalid": f"{type(e).__name__}: {e}", "prefix": line[:180]})

    json_dups = [{"canonical_sha256": hashlib.sha256(k.encode("utf-8")).hexdigest(), "paths": sorted(v)}
                 for k, v in json_objects.items() if len(v) > 1]

    # Static AST scan. It records source locations and nearby lines, not just keyword hits.
    ast_records = []
    syntax_errors = []
    call_counts = Counter()
    for p, text in text_records:
        if p.suffix.lower() != ".py":
            continue
        rp = rel(p)
        try:
            tree = ast.parse(text)
        except Exception as e:
            syntax_errors.append({"path": rp, "error": f"{type(e).__name__}: {e}"})
            continue
        funcs = enclosing_function(tree)
        # Track obvious write calls and result/report-like string literals.
        for n in ast.walk(tree):
            if isinstance(n, ast.Call):
                name = call_name(n)
                call_counts[name] += 1
                args = [expr_text(a) for a in n.args]
                kws = {kw.arg: expr_text(kw.value) for kw in n.keywords if kw.arg}
                is_write = False
                if name in {"dump", "dumps"} and args and ("json" in text[max(0, n.col_offset-100):n.col_offset+100].lower() or "result" in text[max(0, n.col_offset-100):n.col_offset+100].lower()):
                    is_write = True
                if name in {"save", "savez", "savez_compressed", "savetxt", "to_csv", "write_text", "write_bytes", "writerow", "writelines", "writestr"}:
                    is_write = True
                if name == "open" and any((isinstance(a, ast.Constant) and isinstance(a.value, str) and any(ch in a.value for ch in "wax+")) or (isinstance(a, ast.Constant) and a.value in {"w", "a", "x", "wb", "ab", "xb"}) for a in n.args[1:]):
                    is_write = True
                if is_write:
                    start = max(1, n.lineno - 3)
                    end = min(len(text.splitlines()), n.end_lineno + 3)
                    ast_records.append({
                        "path": rp, "line": n.lineno, "function": funcs.get(n.lineno),
                        "call": name, "args": args, "keywords": kws,
                        "write_like": True,
                        "context": text.splitlines()[start-1:end],
                    })
            if isinstance(n, ast.Assign) and isinstance(n.value, (ast.Dict, ast.List, ast.Tuple, ast.Set)):
                target = ", ".join(expr_text(t) for t in n.targets)
                if re.search(r"result|summary|output|report|metric|decision|verdict|claim|pass|failure|control|registry", target, re.I):
                    ast_records.append({
                        "path": rp, "line": n.lineno, "function": funcs.get(n.lineno),
                        "target": target, "value": expr_text(n.value),
                        "literal_payload": literalish(n.value),
                        "context": text.splitlines()[max(1, n.lineno-2):min(len(text.splitlines()), n.lineno+2)],
                    })
            if isinstance(n, ast.Constant) and isinstance(n.value, str):
                s = n.value
                if (re.search(r"\b(result|summary|report|registry|claim|verdict|pass|convergence|delta|p[_ -]?value|sha256)\b", s, re.I)
                        and (len(s) > 80 or re.search(r"[0-9]", s))):
                    ast_records.append({
                        "path": rp, "line": n.lineno, "function": funcs.get(n.lineno),
                        "string_literal": s[:500], "length": len(s),
                    })

    # Text-level provenance/claim markers, with enough context to inspect manually.
    marker_patterns = {
        "hardcoded_output": re.compile(r"(?i)(json\.dump|json\.dumps|write_text|open\([^\n]{0,180}[wax][bt]?\)|np\.save|to_csv|writerow|savefig)"),
        "result_writer": re.compile(r"(?i)(results?[_\-. /]*(json|csv|npz)|summary?[_\-. /]*(json|csv)|registry\.jsonl|report)"),
        "synthetic": re.compile(r"(?i)(synthetic|simulated perceptual|assumed hill|generate.*dose|random\.normal|np\.random|poisson\(|uniform\(|linspace\(|arange\()"),
        "hardcoded_pass": re.compile(r"(?i)(hard.?cod|pass\s*[:=]\s*true|\"pass\"\s*:\s*true|C[0-9].*pass)"),
        "prereg": re.compile(r"(?i)(prereg|frozen|before.*run|result.*hash|dataset.*hash)"),
    }
    text_hits = []
    for p, text in text_records:
        rp = rel(p)
        lines = text.splitlines()
        for i, line in enumerate(lines, 1):
            for kind, pat in marker_patterns.items():
                if pat.search(line):
                    text_hits.append({"path": rp, "line": i, "kind": kind, "text": line[:500]})

    # IDs and nearby file names. IDs are intentionally not treated as globally
    # unique until their contexts are compared.
    id_re = re.compile(r"\b(?:EXP|HYP|Q-[A-Z0-9]+|ANOM)-[A-Z0-9-]+\b", re.I)
    id_map: dict[str, list[str]] = defaultdict(list)
    id_context = defaultdict(list)
    for p, text in text_records:
        rp = rel(p)
        for i, line in enumerate(text.splitlines(), 1):
            for m in id_re.finditer(line):
                ident = m.group(0).upper()
                id_map[ident].append(rp)
                if len(id_context[ident]) < 12:
                    id_context[ident].append({"path": rp, "line": i, "text": line[:500]})

    # Chronology: filesystem mtime plus date strings in each file. The latter
    # is evidence of authored chronology, not proof of execution time.
    chronology = []
    for p, text in text_records:
        dates = date_from_text(text)
        if dates:
            try:
                mt = dt.datetime.fromtimestamp(p.stat().st_mtime, dt.timezone.utc).isoformat()
            except Exception:
                mt = None
            chronology.append({"path": rel(p), "mtime_utc": mt, "dates_in_text": dates})

    # Write compact but complete raw evidence.
    def dump(name: str, obj: Any) -> None:
        (OUT / name).write_text(json.dumps(jsonable(obj), indent=2, ensure_ascii=False, sort_keys=True) + "\n", encoding="utf-8")

    dump("raw_inventory.json", inventory)
    dump("duplicate_files.json", dup_files)
    dump("json_validity.json", {"valid": sorted(json_valid), "invalid": json_invalid, "duplicates": json_dups})
    dump("jsonl_records.json", jsonl_records)
    dump("ast_scan.json", ast_records)
    dump("text_marker_hits.json", text_hits)
    dump("id_map.json", {k: {"files": sorted(set(v)), "mentions": len(v), "contexts": id_context[k]} for k, v in sorted(id_map.items())})
    dump("chronology.json", chronology)
    with (OUT / "mtimes.csv").open("w", newline="", encoding="utf-8") as f:
        w = csv.DictWriter(f, fieldnames=["path", "size", "mtime", "sha256", "suffix"])
        w.writeheader()
        for r in inventory:
            w.writerow({k: r.get(k, "") for k in w.fieldnames})
    print(json.dumps({
        "root": str(ROOT), "files": len(files), "text_files": len(text_records),
        "json_valid": len(json_valid), "json_invalid": len(json_invalid),
        "duplicate_hash_groups": len(dup_files), "json_duplicate_groups": len(json_dups),
        "ast_records": len(ast_records), "text_hits": len(text_hits), "syntax_errors": len(syntax_errors),
    }, indent=2))


if __name__ == "__main__":
    main()
