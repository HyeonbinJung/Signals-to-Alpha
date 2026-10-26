#!/usr/bin/env python3
"""Validate the canonical Signals-to-Alpha publication layout; no network required."""
import json
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
HEADINGS = [
  "01. Abstract",
  "02. Research Design & Hypotheses",
  "03. Industry Context",
  "04. Data & Source Integrity",
  "05. Point-in-Time Availability",
  "06. Factor Construction",
  "07. Exposure & Transmission",
  "08. Outcomes & Baselines",
  "09. Empirical Findings",
  "10. Robustness & Placebos",
  "11. Regime Sensitivity",
  "12. Bias Audit & Verdict",
  "13. Reproduction",
  "14. Next-Stage Protocol",
  "15. Sources & Artifacts"
]

def check(cond, message, errors):
    if not cond:
        errors.append(message)

def main():
    errors = []
    studies = sorted(ROOT.glob("*/study.json"))
    check(len(studies) >= 5, "Expected at least five published study manifests", errors)
    ids = set()
    for manifest_path in studies:
        folder = manifest_path.parent
        label = folder.name
        try:
            manifest = json.loads(manifest_path.read_text(encoding="utf-8"))
        except (ValueError, OSError) as exc:
            errors.append(f"{label}: unreadable study.json: {exc}")
            continue
        check(manifest.get("schema_version") == 1, f"{label}: schema_version must equal 1", errors)
        sid = manifest.get("id")
        check(isinstance(sid, str) and bool(sid), f"{label}: missing id", errors)
        check(sid not in ids, f"{label}: duplicate id {sid}", errors)
        ids.add(sid)
        check(manifest.get("equity_alpha_established") is False, f"{label}: unsupported alpha declaration requires manual review", errors)
        readme_path = folder / "README.md"
        if not readme_path.is_file():
            errors.append(f"{label}: README.md missing")
            continue
        readme = readme_path.read_text(encoding="utf-8")
        actual = [line[3:] for line in readme.splitlines() if line.startswith("## ")]
        check(actual == HEADINGS, f"{label}: README must follow exact 15-section outline, got {actual}", errors)
        for key in ("notebook", "source_register"):
            rel = manifest.get(key)
            check(isinstance(rel, str) and (folder / rel).is_file(), f"{label}: missing {key}: {rel}", errors)
        for key in ("analysis_entrypoint", "requirements", "notes_file"):
            rel = manifest.get(key)
            if rel is not None:
                check(isinstance(rel, str) and (folder / rel).is_file(), f"{label}: invalid {key}: {rel}", errors)
        for key in ("data_files", "result_files"):
            paths = manifest.get(key)
            check(isinstance(paths, list), f"{label}: {key} must be list", errors)
            for rel in paths if isinstance(paths, list) else []:
                check(isinstance(rel, str) and (folder / rel).is_file(), f"{label}: missing {key} file {rel}", errors)
        check(isinstance(manifest.get("test_commands"), list), f"{label}: test_commands must be list", errors)
        nb_path = folder / manifest.get("notebook", "__missing__")
        if nb_path.is_file():
            try:
                nb = json.loads(nb_path.read_text(encoding="utf-8"))
                cells = nb.get("cells", [])
                check(nb.get("nbformat") == 4 and len(cells) >= 25, f"{label}: notebook structure too small or invalid", errors)
                executed = sum(c.get("cell_type") == "code" and c.get("execution_count") is not None for c in cells)
                print(f"{label}: {len(cells)} cells, {executed} saved executed code cells (not re-executed here)")
            except (ValueError, OSError) as exc:
                errors.append(f"{label}: invalid notebook JSON: {exc}")
    for notebook in ROOT.glob("*/*.ipynb"):
        check((notebook.parent / "study.json").is_file(), f"{notebook}: study manifest missing", errors)
    root_readme = (ROOT / "README.md").read_text(encoding="utf-8")
    for manifest in studies:
        check(f"]({manifest.parent.name}/)" in root_readme, f"README.md missing index link for {manifest.parent.name}", errors)
    check("Revenue-Dip-Lab" not in root_readme and "Revenue Dip" not in root_readme, "Stale Revenue Dip entry in root README", errors)
    if errors:
        for err in errors:
            print(f"ERROR: {err}", file=sys.stderr)
        return 1
    print(f"PASS: {len(studies)} indexed studies, 15-section READMEs, source files and notebook structure")
    return 0

if __name__ == "__main__":
    raise SystemExit(main())
