"""Research agent: an LLM-powered physicist that loops with the engine.

The agent plays the role of a senior theoretical physicist hunting for a
quantum gravity breakthrough. It can:

  - Inspect the engine's current constraints, frameworks, and findings
  - Run intersection searches, full batteries, experiment-priority rankings
  - Propose new constraints, frameworks, or analyses (with code)
  - Reflect on results and update its strategy

Each iteration: the agent reads the engine's current state, picks one
action, the engine executes it, the agent reflects, and the loop continues.

Usage:

    from itb.research_agent.runner import run_agent
    run_agent(iterations=5)

Or via CLI:

    itb research-agent --iterations 5
"""

from itb.research_agent.runner import run_agent

__all__ = ["run_agent"]
