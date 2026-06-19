"""Post-promotion-guard discriminator frontier audit (v2.43)."""

from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

sys.path.insert(0, ".")
from experiments.discriminator_frontier import diagnose_discriminator_frontier
from experiments.explicit_tower_basis import _json_default


def diagnose_post_guard_discriminator_frontier() -> dict:
    result = diagnose_discriminator_frontier()
    guard_ready_rows = [
        name for name, row in result["frameworks"].items()
        if row["tower_promotion_guard"]["ready_for_promotion"]
    ]
    guard_blocked_rows = [
        name for name, row in result["frameworks"].items()
        if "known_qg_positive_control_family" in row["tower_promotion_guard"]["blockers"]
    ]
    return {
        **result,
        "basis": [*result["basis"], "tower_promotion_guard"],
        "promotion_guard_ready_frameworks": guard_ready_rows,
        "promotion_guard_positive_control_blocked_frameworks": guard_blocked_rows,
        "post_guard_interpretation": (
            "The promotion guard is wired into every framework row, but the current "
            "registered catalogue is still blocked before that gate because no "
            "reference-feasible in-scope framework supplies native non-synthetic "
            "tower evidence."
        ),
    }


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument(
        "--out",
        default="experiments/results/v2.43/post_guard_discriminator_frontier.json",
    )
    args = parser.parse_args()

    result = diagnose_post_guard_discriminator_frontier()
    out_path = Path(args.out)
    out_path.parent.mkdir(parents=True, exist_ok=True)
    out_path.write_text(json.dumps(result, indent=2, default=_json_default), encoding="utf-8")
    print(json.dumps(result, indent=2, default=_json_default))
    print(f"wrote {out_path}")


if __name__ == "__main__":
    main()
