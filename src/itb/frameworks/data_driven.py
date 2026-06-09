"""The data-driven EFT (v1.79): not a pre-existing theory, but the point that
THEORETICAL CONSISTENCY + CURRENT EXPERIMENTS point to.

Unlike the catalogued frameworks (string-EFT, LQG, CDT, ...) and even the
engine's earlier generative 'discovered_*' branches (which were found from theory
alone), this EFT is selected by folding in real data:
  - it satisfies the full theoretical consistency stack;
  - its parity coupling g_R2_parity = 0.094 reproduces the measured cosmic
    birefringence beta = 3.4 * g_R2_parity ~ 0.32 deg (Minami-Komatsu 0.34+/-0.09);
  - it is the MAXIMALLY-birefringent such consistent EFT (anomaly inflow,
    g_R2_parity^2 + 2 g_R3_parity^2 <= 0.06 g_4 g_R2, is the binding ceiling).

CRUCIAL CAVEAT (v1.79's headline): reaching the measured birefringence REQUIRES a
sizeable g_R2 = 0.33 (scalaron Compton wavelength ~115 um), which the unscreened
Eot-Wash sub-mm bound (v1.77) EXCLUDES. So this EFT is only viable if the scalaron
is SCREENED (chameleon/Vainshtein/dark coupling). The unscreened ceiling is only
beta <= 0.09 deg, ~2.8 sigma below the measurement. Hence the engine's prediction:
cosmic birefringence (if real) and unscreened dark-energy-scale modified gravity
are in tension; the birefringence prefers a screened scalaron.

This is a TARGET/prediction under stated order-of-magnitude mappings (kappa_beta,
rho_inflow) and a 3.6 sigma birefringence HINT -- not a claim about nature.
"""

from itb.frameworks.base import Framework
from itb.theory import Theory


class DiscoveredDataDriven(Framework):
    """The maximally-birefringent consistent EFT that matches cosmic birefringence
    (requires a screened scalaron to evade sub-mm gravity). v1.79."""

    name = "discovered_data_driven"
    citation = ("ITB v1.79: consistency + cosmic birefringence (Minami-Komatsu) "
                "+ sub-mm gravity; data-driven, screened-scalaron")

    # screening is required for sub-mm viability; flags it out-of-scope of the
    # unscreened sub-mm bound, not of the theoretical stack.
    fundamental = True
    local = True
    lorentz_invariant = True

    def encode(self) -> Theory:
        return Theory(
            coefficients={
                "g_4": 0.5668, "g_6": 0.4504, "g_8": 0.4040,
                "g_R2": 0.3258, "g_R3": 0.1437, "g_C": 0.3495,
                "g_R2_parity": 0.0937, "g_R3_parity": 0.0311,
            },
            name=self.name, source=self.citation,
        )
