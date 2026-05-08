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
    from itb.research_agent.runner import run_agent
    log = run_agent(iterations=args.iterations, model=args.model)
    print(f"\nCompleted {len(log)} iterations.")
    for entry in log:
        if "summary" in entry:
            print(f"  iter {entry['iteration']}: {entry['summary'][:200]}")
    return 0


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(prog="itb", description="ITB Engine CLI")
    sub = parser.add_subparsers(dest="command", required=True)

    p_check = sub.add_parser("check", help="Check a single theory against positivity bounds")
    p_check.add_argument("--g4", type=float, required=True)
    p_check.add_argument("--g6", type=float, required=True)
    p_check.set_defaults(fn=cmd_check)

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
    p_agent.set_defaults(fn=cmd_research_agent)

    args = parser.parse_args(argv)
    return args.fn(args)


if __name__ == "__main__":
    sys.exit(main())
