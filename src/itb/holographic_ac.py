"""Holographic unification of the a/c split and eta/s (v1.72).

The same bulk Gauss-Bonnet coupling lambda_GB controls BOTH the central-charge
split c - a (v1.71 Hofman-Maldacena wedge) AND the shear-viscosity ratio eta/s
(v1.67 holographic observable). This module encodes that single-coupling link.

Standard AdS5 / CFT4 Gauss-Bonnet results, linear order in lambda_GB:

  central charges (Myers-Sinha):   a = a0 (1 - 6 lambda),  c = a0 (1 - 2 lambda)
                                    => (c - a)/c = 4 lambda / (1 - 2 lambda)
  shear viscosity (Brigante et al): eta/s = (1/4pi) (1 - 4 lambda)

Eliminating lambda (both deviations are linear in it) gives the
"two observables, one coupling" relation, to leading order:

        1 - 4pi(eta/s)  =  (c - a)/c .

Causality / boundary positivity (Brigante-Liu-Myers-Shenker-Yaida) bounds the
coupling to  lambda_GB in [-7/36, 9/100].  Because the Hofman-Maldacena floor
a/c = 1/3 needs lambda = 1/8 = 0.125 > 9/100, and the ceiling a/c = 31/18 needs
lambda = -0.283 < -7/36, the causality-allowed window maps STRICTLY INSIDE the
HM wedge:  lambda in [-7/36, 9/100]  ->  a/c in [~0.561, ~1.560]  subset of
[1/3, 31/18].  I.e. for a holographic (GB) theory, bulk causality is the tighter
bound and already implies the conformal-collider wedge.

Toy-engine usage: a framework's single curvature coupling g_R2 (= a, Euler) is
mapped to a Gauss-Bonnet coupling  lambda_GB = MU * g_R2  (MU = 0.22, the v1.67
lam_map, chosen so the largest framework g_R2 ~ 0.4 sits just under the causality
bound). From lambda we get the Weyl^2 coupling g_C (= c) and eta/s consistently.
This is a holographic PORTRAIT of the framework (it assumes a GB dual); for
frameworks without a defensible dual it is a what-if, flagged as such.
"""

MU = 0.22                     # lambda_GB = MU * g_R2  (v1.67 lam_map)
LAMBDA_CAUSALITY_MAX = 9.0 / 100.0     # 0.09  (Brigante et al upper)
LAMBDA_CAUSALITY_MIN = -7.0 / 36.0     # -0.194 (Brigante et al lower)
AC_FLOOR = 1.0 / 3.0          # Hofman-Maldacena lower
AC_CEIL = 31.0 / 18.0         # Hofman-Maldacena upper


def lambda_GB(g_R2: float, mu: float = MU) -> float:
    """Map a toy curvature coupling g_R2 to a Gauss-Bonnet coupling."""
    return mu * g_R2


def ac_ratio(lam: float) -> float:
    """a/c from lambda_GB (exact linear-order form (1-6L)/(1-2L))."""
    denom = 1.0 - 2.0 * lam
    return (1.0 - 6.0 * lam) / denom if denom != 0 else float("inf")


def c_minus_a_over_c(lam: float) -> float:
    """(c - a)/c = 4 lambda / (1 - 2 lambda)."""
    denom = 1.0 - 2.0 * lam
    return 4.0 * lam / denom if denom != 0 else float("inf")


def eta_over_s_kss(lam: float) -> float:
    """eta/s in units of 1/4pi = 1 - 4 lambda (Brigante convention; causality
    lambda <= 9/100 gives the famous 16/25 KSS-violation floor)."""
    return 1.0 - 4.0 * lam


def gC_from_gR2(g_R2: float, mu: float = MU) -> float:
    """Weyl^2 coupling g_C (= c) from g_R2 (= a) via the GB portrait:
    g_C = a / (a/c) = g_R2 / ac_ratio(lambda)."""
    if g_R2 == 0.0:
        return 0.0
    lam = lambda_GB(g_R2, mu)
    r = ac_ratio(lam)
    return g_R2 / r if r not in (0.0, float("inf")) else g_R2


def unification_residual(lam: float) -> float:
    """Check 1 - 4pi(eta/s) == (c-a)/c to linear order.
    Returns the difference (exact forms differ at O(lambda^2))."""
    return (1.0 - eta_over_s_kss(lam)) - c_minus_a_over_c(lam)
