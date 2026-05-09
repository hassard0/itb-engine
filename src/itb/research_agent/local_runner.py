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
_FENCED_JSON = re.compile(r"```(?:json|tool)?\s*(\{.*?\})\s*```", re.DOTALL)
_BARE_TOOL_OBJECT = re.compile(r'\{\s*"name"\s*:\s*"([a-z_]+)"\s*,\s*"input"\s*:\s*(\{[^{}]*\})\s*\}', re.DOTALL)


def _extract_tool_call(text: str) -> dict | None:
    """Find a tool call in any of several plausible formats Gemma might emit.

    Tries (in order):
      1. <tool>{...}</tool> — strict format
      2. ```tool ... ```  or  ```json {"name": ...} ``` — markdown fenced
      3. Any bare {"name": "...", "input": {...}} object found in the text

    Returns parsed JSON dict or None if nothing matched."""

    def _try_parse(body: str) -> dict | None:
        body = body.strip()
        # Strip nested code fences if any
        if body.startswith("```"):
            body = body.strip("`").lstrip()
            if body.lower().startswith("json"):
                body = body[4:].lstrip()
            elif body.lower().startswith("tool"):
                body = body[4:].lstrip()
        try:
            obj = json.loads(body)
            if isinstance(obj, dict) and "name" in obj:
                return obj
        except json.JSONDecodeError:
            pass
        return None

    # 1. Strict <tool>...</tool>
    m = _TOOL_PATTERN.search(text)
    if m:
        result = _try_parse(m.group(1))
        if result is not None:
            return result

    # 2. Fenced JSON block (only with name+input shape)
    for fm in _FENCED_JSON.finditer(text):
        result = _try_parse(fm.group(1))
        if result is not None and "input" in result:
            return result

    # 3. Bare {"name": ..., "input": ...} pattern
    bm = _BARE_TOOL_OBJECT.search(text)
    if bm:
        try:
            return {
                "name": bm.group(1),
                "input": json.loads(bm.group(2)),
            }
        except json.JSONDecodeError:
            pass

    return None


def _post_chat(
    base_url: str,
    model: str,
    messages: list[dict],
    max_tokens: int = 4096,
    temperature: float = 0.6,
    timeout: float = 600.0,
    tools: list[dict] | None = None,
) -> dict:
    body: dict = {
        "model": model,
        "messages": messages,
        "max_tokens": max_tokens,
        "temperature": temperature,
    }
    if tools:
        body["tools"] = tools
        body["tool_choice"] = "auto"
    req = urllib.request.Request(
        f"{base_url.rstrip('/')}/v1/chat/completions",
        data=json.dumps(body).encode("utf-8"),
        headers={"Content-Type": "application/json"},
        method="POST",
    )
    with urllib.request.urlopen(req, timeout=timeout) as resp:
        return json.loads(resp.read().decode("utf-8"))


def _tools_to_openai_format() -> list[dict]:
    """Convert our Anthropic-style TOOL_SCHEMAS to OpenAI tools format."""
    out = []
    for t in TOOL_SCHEMAS:
        out.append({
            "type": "function",
            "function": {
                "name": t["name"],
                "description": t["description"],
                "parameters": t["input_schema"],
            },
        })
    return out


def _supports_native_tools(base_url: str) -> bool:
    """Probe /props to see if the server's chat template supports tools."""
    try:
        with urllib.request.urlopen(
            f"{base_url.rstrip('/')}/props", timeout=5
        ) as resp:
            data = json.loads(resp.read().decode("utf-8"))
        caps = data.get("chat_template_caps", {})
        return bool(caps.get("supports_tool_calls") and caps.get("supports_tools"))
    except Exception:
        return False


def _run_with_native_tools(
    base_url: str,
    model: str,
    iterations: int,
    max_tokens: int,
    temperature: float,
    max_steps_per_iteration: int,
) -> list[dict]:
    """Use the OpenAI-compatible /v1/chat/completions tools API."""
    import traceback

    from itb.research_agent.persona import SYSTEM_PROMPT

    tools = _tools_to_openai_format()
    boot = _bootstrap_context()
    messages: list[dict] = [
        {"role": "system", "content": SYSTEM_PROMPT},
        {"role": "user", "content": (
            "Here is the engine's current state. Pick ONE action this iteration. "
            "Use the tools provided. Mark the iteration complete when done.\n\n"
            + boot
        )},
    ]
    log: list[dict] = []

    for it in range(iterations):
        print(f"=== iteration {it + 1}/{iterations} ===", flush=True)
        iter_complete = False
        for step in range(max_steps_per_iteration):
            print(f"  -- step {step + 1}/{max_steps_per_iteration} --", flush=True)
            try:
                resp = _post_chat(
                    base_url, model, messages,
                    max_tokens=max_tokens, temperature=temperature,
                    tools=tools,
                )
            except urllib.error.URLError as e:
                print(f"[local_runner] HTTP error: {e}", flush=True)
                log.append({"iteration": it + 1, "error": str(e)})
                return log
            except Exception as e:
                print(f"[local_runner] error: {type(e).__name__}: {e}", flush=True)
                traceback.print_exc()
                log.append({"iteration": it + 1, "error": str(e)})
                return log

            try:
                choice = resp["choices"][0]
                msg = choice["message"]
                content = msg.get("content") or ""
                reasoning = msg.get("reasoning_content") or ""
                tool_calls = msg.get("tool_calls") or []
                finish = choice.get("finish_reason", "?")
                usage = resp.get("usage", {})
            except (KeyError, IndexError, TypeError) as e:
                print(f"[local_runner] bad response: {e}", flush=True)
                log.append({"iteration": it + 1, "error": f"bad response: {e}"})
                return log

            print(f"  [resp]     finish={finish}, "
                  f"prompt_tokens={usage.get('prompt_tokens')}, "
                  f"completion_tokens={usage.get('completion_tokens')}, "
                  f"tool_calls={len(tool_calls)}", flush=True)
            if reasoning:
                print(f"  [thinking] {reasoning.replace(chr(10), ' ')[:300]}...", flush=True)
            if content.strip():
                print(f"  [content]  {content.replace(chr(10), ' ')[:300]}", flush=True)

            messages.append({
                "role": "assistant",
                "content": content,
                "tool_calls": tool_calls or None,
            })

            if not tool_calls:
                print("  [no tool]  ending iteration (native API returned none)", flush=True)
                log.append({"iteration": it + 1, "outcome": "no_tool_native"})
                iter_complete = True
                break

            try:
                for tc in tool_calls:
                    fn = tc.get("function", {})
                    tool_name = fn.get("name")
                    args_raw = fn.get("arguments") or "{}"
                    try:
                        tool_input = json.loads(args_raw) if isinstance(args_raw, str) else args_raw
                    except json.JSONDecodeError:
                        tool_input = {}
                    print(f"  [tool]     {tool_name}({json.dumps(tool_input)[:150]})", flush=True)
                    try:
                        result = dispatch(tool_name, tool_input)
                    except Exception as e:
                        print(f"  [tool ERR] {type(e).__name__}: {e}", flush=True)
                        traceback.print_exc()
                        result = {"error": f"{type(e).__name__}: {e}"}
                    tool_result_str = json.dumps(result, default=str)
                    if len(tool_result_str) > 4000:
                        tool_result_str = tool_result_str[:4000] + "...[truncated]"
                    print(f"  [result]   {tool_result_str[:300]}", flush=True)
                    messages.append({
                        "role": "tool",
                        "tool_call_id": tc.get("id", ""),
                        "content": tool_result_str,
                    })
                    if tool_name == "mark_iteration_complete":
                        log.append({
                            "iteration": it + 1,
                            "summary": result.get("summary", ""),
                        })
                        iter_complete = True
                print(f"  [loop]     processed {len(tool_calls)} tool call(s); messages={len(messages)}", flush=True)
            except Exception as e:
                print(f"  [LOOP ERR] {type(e).__name__}: {e}", flush=True)
                traceback.print_exc()
                log.append({"iteration": it + 1, "error": f"loop: {e}"})
                return log

            if iter_complete:
                break

        if not iter_complete:
            log.append({"iteration": it + 1, "outcome": "max_steps"})

        if it + 1 < iterations:
            messages.append({
                "role": "user",
                "content": (
                    f"Iteration {it + 1} done. Begin iteration {it + 2}. "
                    "Build on what you learned. ONE meaningful action this iteration."
                ),
            })

    return log


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
    use_native_tools: bool | None = None,
) -> list[dict]:
    """Run Dr. M. against a local OpenAI-compatible LLM server.

    If `use_native_tools` is None (default), probe the server's /props
    endpoint and use native tool calling if supported. Otherwise use
    structured `<tool>...</tool>` prompting."""
    if use_native_tools is None:
        use_native_tools = _supports_native_tools(base_url)
    print(f"[local_runner] base_url={base_url} model={model}", flush=True)
    print(
        f"[local_runner] iterations={iterations} max_steps_per={max_steps_per_iteration} "
        f"native_tools={use_native_tools}\n",
        flush=True,
    )

    if use_native_tools:
        return _run_with_native_tools(
            base_url, model, iterations,
            max_tokens, temperature, max_steps_per_iteration,
        )

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
            # Try harder: search reasoning_content too (some models may
            # put the tool call there)
            if tool_call is None and reasoning:
                tool_call = _extract_tool_call(reasoning)
                if tool_call is not None:
                    print("  [recovery] found tool call in reasoning_content", flush=True)

            if tool_call is None:
                # Up to 3 nudges per iteration, with corrective feedback
                nudges_so_far = sum(
                    1 for m in messages[-7:]
                    if m.get("role") == "user"
                    and "EVERY response MUST end" in m.get("content", "")
                )
                if nudges_so_far < 3:
                    print(f"  [no tool]  nudge {nudges_so_far + 1}/3", flush=True)
                    messages.append({
                        "role": "user",
                        "content": (
                            "Your last response had no tool call. EVERY response MUST end "
                            "with a `<tool>{\"name\": ..., \"input\": {...}}</tool>` block. "
                            "If you have nothing more to do, call `mark_iteration_complete`. "
                            "Try again now: emit ONE tool call."
                        ),
                    })
                    continue
                else:
                    print("  [no tool]  ending iteration after 3 nudges", flush=True)
                    log.append({"iteration": it + 1, "outcome": "no_tool_after_nudges"})
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
