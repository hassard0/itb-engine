"""The species-scale bound: tying the EFT cutoff to a tower of light states (v1.96).

Dvali's species scale: with N light species below the cutoff, gravity becomes strongly
coupled at Lambda_species ~ M_Pl / N^(1/(d-2)) = M_Pl / sqrt(N) in d=4. The EFT cutoff
cannot exceed it:  Lambda_EFT <= Lambda_species, an upper bound that DROPS as N grows.

How the higher-derivative couplings feed N (Dr. M.-confirmed; van de Heisteeg-Vafa-
Wiesner): large Wilson coefficients signal new LIGHT states (the R^2 scalaron mass
m ~ cutoff / sqrt(g_R2), and more generally a descending tower as couplings grow). The
CURVATURE sector (g_R2, g_C, g_R3) sources the gravitational tower, so we count

        N(g) = 1 + nu * (|g_R2| + |g_C| + |g_R3|) .

Requiring Lambda_species >= Lambda_EFT (the EFT is valid up to its own cutoff) gives
N <= N_max, i.e.

        nu * (|g_R2| + |g_C| + |g_R3|)  <=  N_max - 1 .

STRUCTURE (Dr. M.): this has the SAME FORM (an aggregate-coupling bound) as the
complexity cutoff, but DISTINCT physical content -- the species scale counts the TOWER
(tied to the distance-conjecture / curvature sector), the complexity bound counts
aggregate computational cost over ALL coefficients. Whether it carries *independent*
information in this toy basis (vs being implied by complexity) is the empirical
question of the v1.96 note. The tower (sublattice) WGC is spectrum-centric and does not
directly bound the coefficients beyond this.

Reference: Dvali (species scale); van de Heisteeg, Vafa, Wiesner (species scale &
higher-derivative couplings); Heidenreich-Reece-Rudelius (tower/sublattice WGC).
"""

from itb.constraints.base import Constraint, ConstraintClass, ConstraintResult
from itb.theory import Theory


class SpeciesScaleBound(Constraint):
    """nu*(|g_R2|+|g_C|+|g_R3|) <= N_max - 1  (Lambda_species >= EFT cutoff)."""

    name = "species_scale_bound"
    citation = "Dvali (species scale); van de Heisteeg-Vafa-Wiesner; HRR (tower WGC)"
    constraint_class = ConstraintClass.C_UNIVERSALITY

    def __init__(self, nu: float = 2.0, N_max: float = 3.0):
        self.nu = float(nu)
        self.N_max = float(N_max)

    def _species(self, theory: Theory) -> float:
        gR2 = abs(theory.coefficients.get("g_R2", 0.0))
        gC = abs(theory.coefficients.get("g_C", 0.0))
        gR3 = abs(theory.coefficients.get("g_R3", 0.0))
        return 1.0 + self.nu * (gR2 + gC + gR3)

    def evaluate(self, theory: Theory) -> ConstraintResult:
        N = self._species(theory)
        margin = self.N_max - N
        return ConstraintResult(
            constraint_name=self.name,
            satisfied=margin >= 0,
            margin=margin,
            signed_distance_margin=self._signed_distance(margin, self.gradient(theory)),
            details={"bound": f"N = 1 + {self.nu}*(|g_R2|+|g_C|+|g_R3|) <= {self.N_max} "
                              f"(Lambda_species >= cutoff)",
                     "N_species": N, "margin": margin},
        )

    def gradient(self, theory: Theory) -> dict[str, float]:
        out = {k: 0.0 for k in theory.coefficients}
        for k in ("g_R2", "g_C", "g_R3"):
            out.setdefault(k, 0.0)
            v = theory.coefficients.get(k, 0.0)
            out[k] = -self.nu * (1.0 if v >= 0 else -1.0)
        return out
