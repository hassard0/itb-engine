"""Bayesian framework inference: which candidate theories does a measurement favour?

Turns the engine from "which theories are consistent" into "which theories does
the data prefer." Given measurements of Wilson coefficients (or observables that
map to them) with Gaussian uncertainties, compute the posterior probability over
a set of candidate frameworks.

This is the live measurement -> theory inference layer (2026-06 program, v1.52).
A measurement is {coefficient_name: (central_value, sigma)}; each framework
predicts a coefficient vector via its encode(); the likelihood is the product of
per-coefficient Gaussians; the posterior is the normalized prior x likelihood.
"""

from dataclasses import dataclass
import math


@dataclass
class FrameworkPosterior:
    name: str
    prior: float
    log_likelihood: float
    posterior: float


def _gauss_loglik(predicted: float, central: float, sigma: float) -> float:
    if sigma <= 0:
        raise ValueError("sigma must be positive")
    z = (predicted - central) / sigma
    return -0.5 * z * z - math.log(sigma * math.sqrt(2 * math.pi))


def framework_posterior(measurements, frameworks, prior=None):
    """Posterior over `frameworks` given `measurements`.

    measurements: dict {coefficient_name: (central, sigma)}
    frameworks:   iterable of Framework instances (have .name and .encode())
    prior:        optional dict {name: prior_weight}; defaults to uniform.

    Returns: list[FrameworkPosterior] sorted by posterior (desc).
    """
    fws = list(frameworks)
    n = len(fws)
    if prior is None:
        prior = {fw.name: 1.0 / n for fw in fws}
    # normalize prior
    z = sum(prior.get(fw.name, 0.0) for fw in fws)
    prior = {fw.name: prior.get(fw.name, 0.0) / z for fw in fws}

    rows = []
    for fw in fws:
        coeffs = fw.encode().coefficients
        ll = 0.0
        for cname, (central, sigma) in measurements.items():
            pred = coeffs.get(cname, 0.0)
            ll += _gauss_loglik(pred, central, sigma)
        rows.append([fw.name, prior[fw.name], ll])

    # posterior ∝ prior * exp(ll); use log-sum-exp for stability
    max_ll = max(r[2] for r in rows) if rows else 0.0
    unnorm = [r[1] * math.exp(r[2] - max_ll) for r in rows]
    total = sum(unnorm)
    out = []
    for r, u in zip(rows, unnorm):
        out.append(FrameworkPosterior(name=r[0], prior=r[1], log_likelihood=r[2],
                                      posterior=(u / total if total > 0 else 0.0)))
    out.sort(key=lambda p: -p.posterior)
    return out
