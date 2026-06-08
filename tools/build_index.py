#!/usr/bin/env python3
"""Auto-generate docs/results/INDEX.md — a navigable front door to the program.

Scans docs/results/*.md, extracts each note's date, version, title (first #
heading), and one-line summary, groups them by research arc (by version number),
and writes a chronological, sectioned table of contents.

Usage:  python tools/build_index.py   (run from repo root; pure file I/O)
"""
import glob
import os
import re

RESULTS = "docs/results"

# arc boundaries by version float; (low, high_inclusive, label)
ARCS = [
    (0.0, 0.99, "Foundations (v0.x - v1.22): the original engine"),
    (1.23, 1.26, "Arc I - Realism audit (v1.23-26): which conclusions survive the toy prefactors"),
    (1.27, 1.34, "Arc II - Generative discovery (v1.27-34): new consistent theories + the parity frontier"),
    (1.35, 1.38, "Arc III - Observability (v1.35-38): Fisher sloppiness, spin-4, the parity ceiling"),
    (1.39, 1.44, "Arc IV - The decisive experiment (v1.39-44): GIE, sub-mm gravity, the CC link"),
    (1.45, 1.51, "Arc V - Dark-energy axion + synthesis (v1.45-51): CMB EB, DESI, the scorecard"),
    (1.52, 1.57, "Arc VI - The multi-probe parity web (v1.52-57): inference, chiral HD, ringdown, forecast"),
    (1.58, 1.99, "Arc VII - Framework / scope / constraint expansion (v1.58+): new theories, 3-D scope, new bounds"),
]


def parse(path):
    txt = open(path, encoding="utf-8", errors="replace").read()
    base = os.path.basename(path)
    m = re.match(r"(\d{4}-\d{2}-\d{2})", base)
    date = m.group(1) if m else "????-??-??"
    vm = re.search(r"v(\d+\.\d+)", base) or re.search(r"v(\d+\.\d+)", txt[:200])
    ver_str = vm.group(1) if vm else ""
    ver = float(ver_str) if ver_str else (0.5 if "RESEARCH-REPORT" not in base else 0.9)
    hm = re.search(r"^#\s+(.+)$", txt, re.M)
    title = hm.group(1).strip() if hm else base
    # one-line summary: first bold-led line, or first paragraph after the meta block
    summ = ""
    for line in txt.splitlines():
        s = line.strip()
        if s.startswith("**") and s.endswith("**") and len(s) < 200 and "Date:" not in s:
            summ = s.strip("*").strip(); break
    if not summ:
        # first non-heading, non-meta, non-divider, non-bold paragraph
        for line in txt.splitlines():
            s = line.strip()
            if s and not s.startswith(("#", "-", "|", ">", "**", "```", "*", "<")) and "Date:" not in s and "Compute:" not in s:
                summ = s; break
    summ = re.sub(r"\s+", " ", summ)[:160]
    return {"date": date, "ver": ver, "ver_str": ver_str, "title": title,
            "summary": summ, "file": base}


def main():
    notes = [parse(p) for p in glob.glob(os.path.join(RESULTS, "*.md"))
             if os.path.basename(p) != "INDEX.md"]
    notes.sort(key=lambda n: (n["ver"], n["date"], len(n["ver_str"]), n["file"]))

    out = ["# ITB Engine - Research Results Index", "",
           "Auto-generated front door to the full research program "
           f"({len(notes)} notes). Regenerate with `python tools/build_index.py`.", ""]
    is_old = lambda n: n["date"] < "2026-06"     # original engine (2026-05-xx)
    for lo, hi, label in ARCS:
        if lo < 1.0:   # Foundations: all pre-June notes, regardless of version float
            arc_notes = [n for n in notes if is_old(n)]
        else:          # later arcs: June-program notes in the version band
            arc_notes = [n for n in notes if not is_old(n) and lo <= n["ver"] <= hi]
        if not arc_notes:
            continue
        out.append(f"## {label}")
        out.append("")
        out.append("| ver | note | one line |")
        out.append("|---|---|---|")
        for n in arc_notes:
            vd = f"v{n['ver_str']}" if n["ver_str"] else "-"
            link = f"[{n['title'][:70]}]({n['file']})"
            out.append(f"| {vd} | {link} | {n['summary']} |")
        out.append("")

    open(os.path.join(RESULTS, "INDEX.md"), "w", encoding="utf-8").write("\n".join(out))
    print(f"wrote {RESULTS}/INDEX.md ({len(notes)} notes)")


if __name__ == "__main__":
    main()
