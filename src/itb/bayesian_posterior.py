"""Bayesian posterior over Wilson coefficients via rejection sampling.

Given a Gaussian prior centered at a framework's encoded values and the
current constraint set, sample the posterior:

    P(theory | constraints) ∝ P(theory) * I[all_constraints_satisfied]

with I a hard 0/1 likelihood. Implementation: rejection sampling — draw
N samples from prior, keep the ones that satisfy every constraint.

Reports the posterior mean per coefficient and the acceptance rate.
Acceptance rate is itself informative: low rate = constraints tight
relative to prior; high rate = constraints loose relative to prior."""

from dataclasses import dataclass

import numpy as np

from itb.constraints.base import Constraint
from itb.engine import check
from itb.theory import Theory


@dataclass
class BayesianPosterior:
    n_samples_drawn: int
    n_samples_accepted: int
    acceptance_rate: float
    posterior_mean: dict[str, float]
    posterior_std: dict[str, float]
    prior_center: dict[str, float]
    prior_sigma: float


def sample_posterior(
    prior_center: dict[str, float],
    constraints: list[Constraint],
    sigma: float = 0.1,
    n_samples: int = 5000,
    rng_seed: int = 42,
) -> BayesianPosterior:
    rng = np.random.default_rng(rng_seed)
    keys = list(prior_center.keys())
    accepted: list[dict[str, float]] = []
    for _ in range(n_samples):
        sample = {
            k: float(prior_center[k] + rng.normal(0, sigma)) for k in keys
        }
        if check(Theory(coefficients=sample), constraints).feasible:
            accepted.append(sample)

    n_acc = len(accepted)
    if n_acc == 0:
        return BayesianPosterior(
            n_samples_drawn=n_samples,
            n_samples_accepted=0,
            acceptance_rate=0.0,
            posterior_mean={k: float("nan") for k in keys},
            posterior_std={k: float("nan") for k in keys},
            prior_center=dict(prior_center),
            prior_sigma=sigma,
        )
    posterior_mean = {
        k: float(np.mean([s[k] for s in accepted])) for k in keys
    }
    posterior_std = {
        k: float(np.std([s[k] for s in accepted])) for k in keys
    }
    return BayesianPosterior(
        n_samples_drawn=n_samples,
        n_samples_accepted=n_acc,
        acceptance_rate=n_acc / n_samples,
        posterior_mean=posterior_mean,
        posterior_std=posterior_std,
        prior_center=dict(prior_center),
        prior_sigma=sigma,
    )
