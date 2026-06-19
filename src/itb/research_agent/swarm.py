"""Swarm planning utilities for ITB research cycles."""

from __future__ import annotations

from datetime import date
from pathlib import Path

from itb.research_agent.personas import PERSONAS
from itb.research_agent.tools import REPO_ROOT, list_constraints, list_frameworks


DEFAULT_RESULTS_DIR = REPO_ROOT / "docs" / "results"


def build_swarm_brief(vulcan_host: str = "192.168.4.178") -> str:
    """Return a Markdown brief for the next coordinated research cycle."""
    constraints = list_constraints()
    frameworks = list_frameworks()
    today = date.today().isoformat()
    by_class: dict[str, int] = {}
    for constraint in constraints["constraints"]:
        cls = constraint["constraint_class"]
        by_class[cls] = by_class.get(cls, 0) + 1

    lines = [
        f"# v2.11 Agent Swarm Research Program ({today})",
        "",
        "## Mission",
        "",
        (
            "Use a coordinated adversarial swarm to push the ITB engine toward a "
            "quantum-gravity discriminator: a compact set of consistency "
            "constraints plus measurements that leaves only viable, falsifiable "
            "regions of theory space. This is a research program, not a claim "
            "that quantum gravity is solved."
        ),
        "",
        "## Current Engine State",
        "",
        f"- Registered constraints exposed to the API/tools: {constraints['count']}",
    ]
    for cls, count in sorted(by_class.items()):
        lines.append(f"- {cls}: {count}")
    lines.extend([
        f"- Registered frameworks exposed to the API/tools: {frameworks['count']}",
        f"- Remote compute target: `admin@{vulcan_host}` (`tools/vulcan.py`)",
        "",
        "## Operating Rules",
        "",
        "- Every result note must separate theorem, toy model, data ingest, and speculation.",
        "- Every positive claim needs a corresponding adversarial-referee pass.",
        "- Heavy sweeps run on Vulcan; notebooks and local UI remain for inspection.",
        "- New constraints must define gradients or explicitly justify why the signed margin is raw.",
        "- Generated artifacts go under `experiments/results/`; conclusions go under `docs/results/`.",
        "",
        "## Personas",
        "",
    ])

    for persona in PERSONAS:
        lines.extend([
            f"### {persona.name}",
            "",
            f"- Discipline: {persona.discipline}",
            f"- Mission: {persona.mission}",
            "- Priority questions:",
        ])
        for question in persona.questions:
            lines.append(f"  - {question}")
        lines.append(f"- Preferred actions: {', '.join(persona.preferred_actions)}")
        lines.append("")

    lines.extend([
        "## First Swarm Queue",
        "",
        "1. Numerical Cartographer: run a full-basis connectivity and fragility sweep on Vulcan.",
        "2. Amplitude Bootstrapper: audit whether non-forward/spinning positivity can constrain `g_8` and `g_R3` independently.",
        "3. Holographic Geometer: test whether Hofman-Maldacena, eta/s, and complexity constraints are redundant in the current basis.",
        "4. Phenomenology Scout: rank the next measurements after sub-mm gravity, CMB birefringence, and GW dispersion.",
        "5. Swampland Cartographer: re-check the corrected RFC/Scalar-WGC/species-scale stack under prefactor uncertainty.",
        "6. Adversarial Referee: write the limitation note for any claim that fails scope, locality, Lorentz, or screening assumptions.",
        "",
        "## Documentation Standard",
        "",
        (
            "Each cycle should end with a dated result note containing: question, "
            "method, constraints/frameworks used, command or script, quantitative "
            "result, caveats, and next action. The note should be short enough "
            "to index but detailed enough to reproduce."
        ),
    ])
    return "\n".join(lines) + "\n"


def default_brief_path() -> Path:
    return DEFAULT_RESULTS_DIR / f"{date.today().isoformat()}-v2.11-agent-swarm-research-program.md"


def write_swarm_brief(path: str | Path | None = None, vulcan_host: str = "192.168.4.178") -> Path:
    target = Path(path) if path is not None else default_brief_path()
    if not target.is_absolute():
        target = REPO_ROOT / target
    target.parent.mkdir(parents=True, exist_ok=True)
    target.write_text(build_swarm_brief(vulcan_host=vulcan_host), encoding="utf-8")
    return target
