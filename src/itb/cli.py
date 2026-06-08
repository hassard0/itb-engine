"""Command-line entry points for the ITB engine."""

import argparse
import json
import sys

from itb.constraints.scalar_positivity import (
    ScalarPositivityG4,
    ScalarPositivityG6,
)
from itb.engine import check
from itb.theory import Theory


def cmd_check(args: argparse.Namespace) -> int:
    theory = Theory(coefficients={"g_4": args.g4, "g_6": args.g6})
    report = check(theory, [ScalarPositivityG4(), ScalarPositivityG6()])
    payload = {
        "feasible": report.feasible,
        "results": [
            {
                "constraint_name": r.constraint_name,
                "satisfied": r.satisfied,
                "margin": r.margin,
            }
            for r in report.results
        ],
    }
    print(json.dumps(payload, indent=2))
    return 0 if report.feasible else 2


def cmd_predict(args: argparse.Namespace) -> int:
    from itb.predict import FRAMEWORKS, predict, render
    if args.framework == "list" or args.framework not in FRAMEWORKS:
        if args.framework != "list":
            print(f"unknown framework '{args.framework}'.")
        print("known frameworks: " + ", ".join(sorted(FRAMEWORKS)))
        return 0 if args.framework == "list" else 2
    if args.json:
        print(json.dumps(predict(args.framework), indent=2))
    else:
        print(render(args.framework))
    return 0


def cmd_serve(args: argparse.Namespace) -> int:
    import uvicorn
    uvicorn.run(
        "itb.api.server:app",
        host=args.host,
        port=args.port,
        reload=args.reload,
    )
    return 0


def cmd_research_agent(args: argparse.Namespace) -> int:
    if args.backend == "local":
        from itb.research_agent.local_runner import run_local_agent
        model = args.model
        if model.startswith("claude"):
            model = "gemma-4-26b-a4b-it"
        log = run_local_agent(
            base_url=args.base_url,
            model=model,
            iterations=args.iterations,
            max_tokens=args.max_tokens,
            temperature=args.temperature,
        )
    else:
        from itb.research_agent.runner import run_agent
        log = run_agent(iterations=args.iterations, model=args.model)
    print(f"\nCompleted {len(log)} iteration entries.")
    for entry in log:
        if "summary" in entry:
            print(f"  iter {entry['iteration']}: {entry['summary'][:200]}")
        elif "error" in entry:
            print(f"  iter {entry['iteration']}: ERROR {entry['error']}")
        elif "outcome" in entry:
            print(f"  iter {entry['iteration']}: {entry['outcome']}")
    return 0


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(prog="itb", description="ITB Engine CLI")
    sub = parser.add_subparsers(dest="command", required=True)

    p_check = sub.add_parser("check", help="Check a single theory against positivity bounds")
    p_check.add_argument("--g4", type=float, required=True)
    p_check.add_argument("--g6", type=float, required=True)
    p_check.set_defaults(fn=cmd_check)

    p_predict = sub.add_parser("predict", help="Emit a framework's full observable fingerprint")
    p_predict.add_argument("framework", help="framework name (or 'list')")
    p_predict.add_argument("--json", action="store_true", help="machine-readable JSON output")
    p_predict.set_defaults(fn=cmd_predict)

    p_serve = sub.add_parser("serve", help="Run the localhost web server")
    p_serve.add_argument("--host", default="127.0.0.1")
    p_serve.add_argument("--port", type=int, default=8000)
    p_serve.add_argument("--reload", action="store_true")
    p_serve.set_defaults(fn=cmd_serve)

    p_agent = sub.add_parser(
        "research-agent",
        help="Run the LLM-powered physicist research agent loop",
    )
    p_agent.add_argument("--iterations", type=int, default=5)
    p_agent.add_argument("--model", default="claude-opus-4-7")
    p_agent.add_argument(
        "--backend", choices=("anthropic", "local"), default="anthropic",
        help="anthropic = Anthropic SDK; local = OpenAI-compatible HTTP server",
    )
    p_agent.add_argument(
        "--base-url", default="http://192.168.4.193:8080",
        help="Base URL for local backend (default: Pluto Gemma 4 endpoint)",
    )
    p_agent.add_argument("--max-tokens", type=int, default=4096)
    p_agent.add_argument("--temperature", type=float, default=0.6)
    p_agent.set_defaults(fn=cmd_research_agent)

    args = parser.parse_args(argv)
    return args.fn(args)


if __name__ == "__main__":
    sys.exit(main())
