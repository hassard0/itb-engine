"""CMB-S4 forecast as a proper measurement constraint.

CMB-S4 (the Stage-4 ground-based CMB experiment, planned for ~2030+) will
constrain inflationary EFT parameters to roughly 10x tighter than current
Planck bounds. The forecast sensitivity on the inflationary scalar
self-interaction parameter — which we map to g_4 in the toy basis — is
central_value ≈ 0 (consistent with single-field slow-roll), sigma ≈ 0.03
in dimensionless units after rescaling by the appropriate cutoff.

For our v1.x toy where g_4 takes O(0.5) values for actual UV completions,
a sigma of 0.03 is a *very* tight bound — it would push g_4 toward zero,
disfavoring frameworks that predict O(0.5).

Reference: CMB-S4 Science Book (Abazajian et al, 2016, updated 2022)."""

from itb.constraints.experimental import MeasuredWilsonCoefficient


class CMBS4Forecast(MeasuredWilsonCoefficient):
    """A pre-configured MeasuredWilsonCoefficient with CMB-S4 sensitivity."""

    def __init__(
        self,
        coefficient_name: str = "g_4",
        central_value: float = 0.0,
        sigma: float = 0.03,
        sigma_threshold: float = 2.0,
    ):
        super().__init__(
            coefficient_name=coefficient_name,
            central_value=central_value,
            sigma=sigma,
            sigma_threshold=sigma_threshold,
            experiment_label="CMB_S4_forecast",
        )
        self.citation = "CMB-S4 Science Book (Abazajian et al, 2016, updated 2022)"
