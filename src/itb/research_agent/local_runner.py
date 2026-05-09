"""Local-LLM-backed research-agent runner.

Targets an OpenAI-compatible server (llama.cpp / Ollama / vLLM / etc.) at
a configurable base URL. Uses structured prompting for tool dispatch
rather than model-specific tool APIs — works with any model that can
emit JSON-tagged blocks reliably.

Tested against Gemma 4 26B BF16 served by llama.cpp on Pluto
(192.168.4.193:8080).

Usage:

    from itb.research_agent.local_runner import run_local_agent
    run_local_agent(
        base_url="http://192.168.4.193:8080",
        model="gemma-4-26b-a4b-it",
        iterations=5,
    )
"""

from __future__ import annotations

import json
import re
import urllib.error
import urllib.request
from typing import Any

from itb.research_agent.persona import SYSTEM_PROMPT
from itb.research_agent.tools import TOOL_SCHEMAS, dispatch


def _build_system_prompt() -> str:
    """Augment the persona with tool descriptions in a structured-output
    format. We ask the model to emit one tool call at a time wrapped in
    <tool>...</tool> tags with a JSON body."""
    tool_doc = [
        "",
        "## CRITICAL OUTPUT RULE",
        "",
        "EVERY response of yours MUST end with exactly one tool call wrapped in <tool>...</tool> tags.",
        "Plain-text reasoning is fine inside your response, but the response MUST end with a tool call.",
        "If you have nothing more to do, call `mark_iteration_complete` with a summary — that is itself a tool call.",
        "",
        "Format:",
        "",
        "```",
        "<tool>",
        "{",
        '  "name": "tool_name_here",',
        '  "input": { ... arguments ... }',
        "}",
        "</tool>",
        "```",
        "",
        "After exploring (≤ 2 read-only tools), you should propose a new module via `propose_new_module` OR run an analysis (intersection, etc.) OR call `mark_iteration_complete`. Do NOT keep listing/reading; act decisively after at most 2 reads.",
        "",
        "### Tool catalog",
        "",
    ]
    for t in TOOL_SCHEMAS:
        tool_doc.append(f"**{t['name']}** — {t['description']}")
        props = t["input_schema"].get("properties", {})
        if props:
            tool_doc.append("Inputs:")
            for k, v in props.items():
                desc = v.get("description", "")
                tool_doc.append(f"  - `{k}` ({v.get('type', '?')}): {desc}")
        else:
            tool_doc.append("(no inputs)")
        tool_doc.append("")
    return SYSTEM_PROMPT + "\n\n" + "\n".join(tool_doc)


_TOOL_PATTERN = re.compile(r"<tool>\s*(.*?)\s*</tool>", re.DOTALL)


def _extract_tool_call(text: str) -> dict | None:
    """Find a <tool>...</tool> block and parse its JSON body."""
    m = _TOOL_PATTERN.search(text)
    if not m:
        return None
    body = m.group(1).strip()
    # Strip code fences if model added them
    if body.startswith("```"):
        body = body.strip("`")
        if body.startswith("json"):
            body = body[4:]
    try:
        return json.loads(body)
    except json.JSONDecodeError:
        return None


def _post_chat(
    base_url: str,
    model: str,
    messages: list[dict],
    max_tokens: int = 4096,
    temperature: float = 0.6,
    timeout: float = 600.0,
) -> dict:
    body = {
        "model": model,
        "messages": messages,
        "max_tokens": max_tokens,
        "temperature": temperature,
    }
    req = urllib.request.Request(
        f"{base_url.rstrip('/')}/v1/chat/completions",
        data=json.dumps(body).encode("utf-8"),
        headers={"Content-Type": "application/json"},
        method="POST",
    )
    with urllib.request.urlopen(req, timeout=timeout) as resp:
        return json.loads(resp.read().decode("utf-8"))


def _bootstrap_context() -> str:
    from itb.research_agent.tools import list_constraints, list_frameworks
    constraints = list_constraints()
    frameworks = list_frameworks()
    by_class: dict[str, int] = {}
    for c in constraints["constraints"]:
        cls = c["constraint_class"]
        by_class[cls] = by_class.get(cls, 0) + 1
    lines = [f"Active constraints: {constraints['count']}"]
    for cls, n in sorted(by_class.items()):
        lines.append(f"  {cls}: {n}")
    lines.append(f"Active frameworks: {frameworks['count']}")
    for f in frameworks["frameworks"]:
        coefs = ", ".join(f"{k}={v}" for k, v in f["coefficients"].items())
        lines.append(f"  {f['name']}: {coefs}")
    return "\n".join(lines)


def run_local_agent(
    base_url: str = "http://192.168.4.193:8080",
    model: str = "gemma-4-26b-a4b-it",
    iterations: int = 3,
    max_tokens: int = 4096,
    temperature: float = 0.6,
    max_steps_per_iteration: int = 8,
) -> list[dict]:
    """Run Dr. M. against a local OpenAI-compatible LLM server."""
    print(f"[local_runner] base_url={base_url} model={model}")
    print(f"[local_runner] iterations={iterations} max_steps_per={max_steps_per_iteration}\n")

    system = _build_system_prompt()
    boot = _bootstrap_context()
    user_initial = (
        "Here is the engine's current state. Pick ONE action this iteration. "
        "Use the tools provided. Mark the iteration complete when done.\n\n"
        + boot
    )
    messages: list[dict] = [
        {"role": "system", "content": system},
        {"role": "user", "content": user_initial},
    ]
    log: list[dict] = []

    for it in range(iterations):
        print(f"=== iteration {it + 1}/{iterations} ===")
        iter_complete = False
        for step in range(max_steps_per_iteration):
            try:
                resp = _post_chat(
                    base_url, model, messages,
                    max_tokens=max_tokens, temperature=temperature,
                )
            except urllib.error.URLError as e:
                print(f"[local_runner] HTTP error: {e}")
                log.append({"iteration": it + 1, "error": str(e)})
                return log
            choice = resp["choices"][0]
            msg = choice["message"]
            content = msg.get("content") or ""
            reasoning = msg.get("reasoning_content") or ""

            if reasoning:
                preview = reasoning.replace("\n", " ")[:300]
                print(f"  [thinking] {preview}...")
            if content.strip():
                preview = content.replace("\n", " ")[:300]
                print(f"  [content]  {preview}")

            messages.append({"role": "assistant", "content": content})

            tool_call = _extract_tool_call(content)
            if tool_call is None:
                # No tool emitted; nudge once, then bail.
                if step == 0:
                    print("  [no tool]  prompting for tool emission")
                    messages.append({
                        "role": "user",
                        "content": "Please emit a single tool call wrapped in <tool>...</tool> tags.",
                    })
                    continue
                else:
                    print("  [no tool]  ending iteration")
                    log.append({"iteration": it + 1, "outcome": "no_tool"})
                    iter_complete = True
                    break

            tool_name = tool_call.get("name")
            tool_input = tool_call.get("input") or {}
            print(f"  [tool]     {tool_name}({json.dumps(tool_input)[:120]})")
            result = dispatch(tool_name, tool_input)
            tool_result_str = json.dumps(result, default=str)
            if len(tool_result_str) > 4000:
                tool_result_str = tool_result_str[:4000] + "...[truncated]"
            print(f"  [result]   {tool_result_str[:300]}")
            messages.append({
                "role": "user",
                "content": f"Tool `{tool_name}` returned:\n```\n{tool_result_str}\n```",
            })

            if tool_name == "mark_iteration_complete":
                log.append({
                    "iteration": it + 1,
                    "summary": result.get("summary"),
                })
                iter_complete = True
                break

        if not iter_complete:
            log.append({"iteration": it + 1, "outcome": "max_steps"})

        if it + 1 < iterations:
            messages.append({
                "role": "user",
                "content": (
                    f"Iteration {it + 1} done. Begin iteration {it + 2}. "
                    "Build on what you learned. ONE action this iteration."
                ),
            })

    return log
