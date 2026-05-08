"""Research-agent main loop using the Anthropic SDK.

Per iteration, the agent reads engine state, picks one action via tool use,
the runner dispatches it, the agent reflects, and the next iteration begins
with full conversation context. Prompt caching keeps the system prompt and
engine-state context across iterations.

Usage:

    from itb.research_agent.runner import run_agent
    run_agent(iterations=5, model="claude-opus-4-7")

Or via CLI:

    itb research-agent --iterations 5
"""

from __future__ import annotations

import json
import os
from typing import Any

from itb.research_agent.persona import SYSTEM_PROMPT
from itb.research_agent.tools import TOOL_SCHEMAS, dispatch


def _bootstrap_context() -> str:
    """Pre-baked engine state to seed the first iteration."""
    from itb.research_agent.tools import list_constraints, list_frameworks
    constraints = list_constraints()
    frameworks = list_frameworks()
    summary = []
    summary.append(f"Active constraints: {constraints['count']}")
    summary.append("Constraint classes (count):")
    classes: dict[str, int] = {}
    for c in constraints["constraints"]:
        cls = c["constraint_class"]
        classes[cls] = classes.get(cls, 0) + 1
    for cls, n in sorted(classes.items()):
        summary.append(f"  {cls}: {n}")
    summary.append("")
    summary.append(f"Active frameworks: {frameworks['count']}")
    for f in frameworks["frameworks"]:
        summary.append(f"  {f['name']}: {f['coefficients']}")
    return "\n".join(summary)


def run_agent(
    iterations: int = 5,
    model: str = "claude-opus-4-7",
    max_tokens_per_turn: int = 8000,
) -> list[dict]:
    """Run the research agent for N iterations against the live engine."""
    try:
        import anthropic
    except ImportError:
        raise RuntimeError(
            "anthropic SDK not installed. pip install anthropic to use the "
            "research agent."
        )
    if not os.environ.get("ANTHROPIC_API_KEY"):
        raise RuntimeError(
            "ANTHROPIC_API_KEY not set in environment. Set it to run the agent."
        )

    client = anthropic.Anthropic()

    boot = _bootstrap_context()
    initial_user = (
        "Here is the engine's current state. Pick ONE action this iteration: "
        "inspect a finding, run an analysis, or propose a new module. Use the "
        "tools provided. Mark the iteration complete when you've done one "
        "meaningful step.\n\n" + boot
    )

    messages: list[dict] = [{"role": "user", "content": initial_user}]
    iteration_log: list[dict] = []

    for iter_idx in range(iterations):
        print(f"\n=== Research-agent iteration {iter_idx + 1}/{iterations} ===")
        iter_complete = False
        while not iter_complete:
            response = client.messages.create(
                model=model,
                max_tokens=max_tokens_per_turn,
                system=[
                    {
                        "type": "text",
                        "text": SYSTEM_PROMPT,
                        "cache_control": {"type": "ephemeral"},
                    }
                ],
                tools=TOOL_SCHEMAS,
                messages=messages,
            )

            assistant_blocks = []
            tool_uses = []
            for block in response.content:
                if block.type == "text":
                    assistant_blocks.append({"type": "text", "text": block.text})
                    if block.text.strip():
                        print(f"[agent] {block.text[:500]}")
                elif block.type == "tool_use":
                    assistant_blocks.append({
                        "type": "tool_use",
                        "id": block.id,
                        "name": block.name,
                        "input": block.input,
                    })
                    tool_uses.append(block)
                    print(f"[agent] -> {block.name}({json.dumps(block.input)[:200]})")

            messages.append({"role": "assistant", "content": assistant_blocks})

            if response.stop_reason == "end_turn" and not tool_uses:
                # Agent stopped without calling mark_iteration_complete.
                iteration_log.append({
                    "iteration": iter_idx + 1,
                    "outcome": "end_turn_without_tool",
                })
                iter_complete = True
                break

            if not tool_uses:
                iter_complete = True
                break

            tool_results = []
            for use in tool_uses:
                result = dispatch(use.name, dict(use.input))
                tool_results.append({
                    "type": "tool_result",
                    "tool_use_id": use.id,
                    "content": json.dumps(result)[:6000],
                })
                if use.name == "mark_iteration_complete":
                    iter_complete = True
                    iteration_log.append({
                        "iteration": iter_idx + 1,
                        "summary": result.get("summary"),
                    })

            messages.append({"role": "user", "content": tool_results})

            if iter_complete:
                # Re-prime for next iteration on next outer pass.
                if iter_idx + 1 < iterations:
                    messages.append({
                        "role": "user",
                        "content": (
                            f"Iteration {iter_idx + 1} complete. Now begin "
                            f"iteration {iter_idx + 2}. Build on what you "
                            "just learned. ONE action this iteration."
                        ),
                    })
                break

    return iteration_log
