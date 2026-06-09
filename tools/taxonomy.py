"""v2.09 - Thematic taxonomy of the ITB result notes: a navigable map of the program.

Reads every docs/results/*.md note, extracts (version, date, title), and assigns it to one
of ~9 THEMES by transparent keyword rules (first matching theme wins, in priority order).
Writes docs/results/TAXONOMY.md (notes grouped by theme, each theme summarised, plus a
theme x version-era table) and an optional timeline figure.

HONEST: keyword clustering is heuristic -- a navigation aid, not analysis.

Run:  python tools/taxonomy.py            (reads/writes the local repo)
"""
import re
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
RESULTS = ROOT / "docs" / "results"

# themes in PRIORITY order (a note joins the first theme whose keywords it matches)
THEMES = [
    ("Synthesis & reports",
     "Cross-cutting syntheses, research reports, and capstones.",
     ["research-report", "synthesis", "capstone", "conclusion", "state-of"]),
    ("Empirical swampland & data ingestion",
     "Confronting the EFT with real experiments (sub-mm gravity, cosmic birefringence, GW, "
     "neutron stars, Diosi-Penrose) and the dark-energy/cosmology connections.",
     ["sub-mm", "submm", "birefringence", "gw-speed", "gw-dispersion", "neutron", "diosi",
      "penrose", "yukawa", "dark-energy", "darkenergy", "axion", "desi", "eb-spectrum",
      "quintessence", "cosmological-constant", "four-probe", "ingest", "confrontation"]),
    ("Data-driven EFT & the central tension",
     "The screened-scalaron + positive-parity EFT the data point to, its tension, and the "
     "Bayesian / falsifiability analyses around it.",
     ["data-driven", "tension", "multimessenger", "bayesian", "falsifier", "alt-birefringence",
      "model-comparison"]),
    ("Meta-experiments & auditing",
     "Turning the engine on itself: internal consistency, load-bearing structure, robustness, "
     "and structural tests (double copy, genetic recombination, phylogeny, information geometry).",
     ["godel", "jenga", "adversarial", "double-copy", "genetic", "phylogeny", "robustness",
      "species", "inverse-constraint", "info-geometry", "a-theorem", "taxonomy"]),
    ("Holographic observables",
     "Conformal-collider and holographic diagnostics: a/c, eta/s, black-hole entropy, complexity.",
     ["eta-over-s", "ac-wedge", "ac-portrait", "one-coupling", "complexity", "bh-entropy",
      "holographic", "lloyd", "wgc"]),
    ("Inflation & cosmology",
     "The R^2 (Starobinsky) inflation connection and cosmological observables.",
     ["inflation", "starobinsky", "cmb-eb", "potential-shapes"]),
    ("Forecasts & experiment design",
     "What to measure, how decisive it is, and when: priorities, the minimum set, the timeline.",
     ["experiment", "priority", "convergence", "scorecard", "decisive", "spec-sheet",
      "min-experiment", "projection", "guidance", "discrimination"]),
    ("The consistent island",
     "The geometry of the consistent region: census, center, dimensionality, sloppiness, phases.",
     ["island", "census", "center", "freedom-map", "phases", "sloppi", "fisher",
      "error-bars", "degeneracy"]),
    ("Foundations & basis",
     "The EFT basis, the constraint stack, framework catalogue, and parity sector.",
     ["a-theorem-basis", "basis-extension", "anomaly-flow", "positivity", "cubic-curvature",
      "genealogy", "catalog", "fingerprint", "parity", "lqg", "bnossw", "rfc", "mmi",
      "coefficient-audit", "graviton", "first-disagreement", "discovery", "freedom",
      "matter-degeneracy", "ceiling", "intersection", "baseline", "findings"]),
]
FALLBACK = "Foundations & basis"

ERAS = [("v0.8-v1.5  foundations", 0.8, 1.5),
        ("v1.6-v1.68 structure", 1.6, 1.68),
        ("v1.69-v1.85 empirical swampland", 1.69, 1.85),
        ("v1.86-v2.10 new sectors & meta", 1.86, 2.10)]


def parse_note(p):
    name = p.name
    m = re.search(r"v(\d+\.\d+)", name)
    ver = m.group(1) if m else None
    dm = re.match(r"(\d{4}-\d{2}-\d{2})", name)
    date = dm.group(1) if dm else ""
    title = ""
    txt = p.read_text(encoding="utf-8", errors="ignore")
    for line in txt.splitlines():
        if line.startswith("# "):
            title = line[2:].strip()
            break
    blob = (name + " " + title + " " + txt[:500]).lower()
    return {"file": name, "version": ver,
            "vnum": float(ver) if ver else -1.0, "date": date, "title": title, "blob": blob}


def assign(note):
    for theme, _summary, kws in THEMES:
        if any(k in note["blob"] for k in kws):
            return theme
    return FALLBACK


def build():
    notes = [parse_note(p) for p in sorted(RESULTS.glob("*.md"))
             if p.name not in ("INDEX.md", "TAXONOMY.md")]
    for n in notes:
        n["theme"] = assign(n)
    by_theme = {t: [] for t, _, _ in THEMES}
    for n in notes:
        by_theme[n["theme"]].append(n)
    return notes, by_theme


def write_md(notes, by_theme):
    L = ["# ITB Engine — Thematic Taxonomy of Results", "",
         f"*A navigable map of the program's {len(notes)} result notes, grouped by theme.* "
         "For the chronological list see [INDEX.md](INDEX.md); for the curated findings see "
         "[../FINDINGS.md](../FINDINGS.md); for the overview see "
         "[the v2.0 research report](2026-06-09-v2.0-RESEARCH-REPORT.md).", "",
         "> Themes are assigned by transparent keyword rules (a navigation aid, not analysis).",
         ""]
    # theme x era table
    L += ["## How the program's focus shifted", "",
          "| theme | " + " | ".join(e[0] for e in ERAS) + " |",
          "|" + "---|" * (len(ERAS) + 1)]
    for theme, _s, _k in THEMES:
        if not by_theme[theme]:
            continue
        counts = []
        for _lbl, lo, hi in ERAS:
            counts.append(str(sum(1 for n in by_theme[theme] if lo <= n["vnum"] <= hi)))
        L.append(f"| {theme} | " + " | ".join(counts) + " |")
    L.append("")
    # grouped notes
    for theme, summary, _k in THEMES:
        ns = sorted(by_theme[theme], key=lambda n: n["vnum"])
        if not ns:
            continue
        L += [f"## {theme}  ({len(ns)})", "", f"*{summary}*", ""]
        for n in ns:
            v = f"v{n['version']}" if n["version"] else n["date"]
            short = n["title"].split("—")[-1].split(":")[-1].strip()[:90] if n["title"] else n["file"]
            L.append(f"- **{v}** — [{short}]({n['file']})")
        L.append("")
    (RESULTS / "TAXONOMY.md").write_text("\n".join(L), encoding="utf-8")
    return len(notes)


def figure(notes):
    try:
        import matplotlib
        matplotlib.use("Agg")
        import matplotlib.pyplot as plt
    except Exception:
        return None
    themes = [t for t, _, _ in THEMES if any(n["theme"] == t for n in notes)]
    tidx = {t: i for i, t in enumerate(themes)}
    fig, ax = plt.subplots(figsize=(12, 6))
    colors = plt.cm.tab10.colors
    for n in notes:
        if n["vnum"] < 0:
            continue
        ax.scatter(n["vnum"], tidx[n["theme"]], s=36,
                   color=colors[tidx[n["theme"]] % 10], alpha=0.8)
    ax.set_yticks(range(len(themes))); ax.set_yticklabels(themes, fontsize=8)
    ax.set_xlabel("version"); ax.set_title(
        "v2.09  The ITB program's thematic arc (one dot per result note)", fontsize=11)
    ax.grid(axis="x", alpha=0.2)
    fig.tight_layout()
    out = ROOT / "experiments" / "taxonomy_timeline.png"
    fig.savefig(out, dpi=140)
    return out


if __name__ == "__main__":
    notes, by_theme = build()
    n = write_md(notes, by_theme)
    fig = figure(notes)
    unassigned = [x["file"] for x in notes if x["theme"] not in by_theme]
    print(f"taxonomy: {n} notes, {sum(1 for t in by_theme if by_theme[t])} nonempty themes")
    for t, _, _ in THEMES:
        if by_theme[t]:
            print(f"  {len(by_theme[t]):3d}  {t}")
    print(f"figure: {fig}")
