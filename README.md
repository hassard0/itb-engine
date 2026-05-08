# ITB Engine

Information-Theoretic Bootstrap engine for quantum gravity theory-space exclusions.

A localhost research platform that constrains the space of possible quantum
gravity theories by simultaneously imposing every well-established consistency
condition we have — amplitude bootstrap (unitarity, crossing, positivity bounds),
information-theoretic (holographic entropy cone, Bekenstein, modular flow), and
universality (equivalence principle, BH entropy formula) — and asking which
gravitational EFTs survive at once. Output: a map of allowed theory space, with
candidate frameworks (string theory, asymptotic safety, ...) plotted on it.

The MVP (v0.1.0) ships the engine spine end-to-end with a single class of
constraints (Adams et al 2006 scalar-EFT positivity bounds) and one framework
encoder (Pure GR baseline). See `docs/superpowers/specs/` for the design,
`docs/superpowers/plans/` for the implementation plan, and
`docs/superpowers/notes/` for research-direction ideas captured during the build.

## Quickstart

```powershell
python -m venv .venv
.\.venv\Scripts\Activate.ps1
pip install -e ".[dev]"
pytest
itb --help
itb serve                  # http://localhost:8000
```

## Status

MVP. See `docs/superpowers/specs/2026-05-07-itb-engine-design.md` for the design,
and `docs/superpowers/plans/2026-05-07-itb-engine-mvp.md` for the plan.
