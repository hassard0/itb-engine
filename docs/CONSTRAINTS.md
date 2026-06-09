# ITB Engine — Constraint reference

The **37 theoretical constraints** assembled by `build_stack()` (in `experiments/stack.py`), plus the **4 opt-in data constraints**. Each is a self-contained module in `src/itb/constraints/` exposing `.evaluate(theory) → ConstraintResult(satisfied, margin, signed_distance_margin, details)`, `.gradient(theory)`, and a `.constraint_class`.

> **Honest note:** most bounds use O(1) placeholder prefactors ("the right streets, the wrong house numbers"). Six are tunable knobs with stated plausibility windows (`CANONICAL` / `PLAUSIBLE_RANGES` in `stack.py`) so the *realism program* can test which conclusions survive a factor-of-~2 uncertainty. Citations indicate the *origin/form*, not that the exact coefficient is the published one.

Regenerate this list any time with `python tools/dump_constraints.py`.

---

## Class A — Amplitude bootstrap (20)

Forward-limit positivity, dispersion relations, the EFThedron, conformal-collider, and causality.

- `scalar_positivity_g4` — Adams, Arkani-Hamed, Dubovsky, Nicolis, Rattazzi 2006
- `scalar_positivity_g6` — same family, next order
- `scalar_positivity_g8` — Caron-Huot et al 2021, fourth-order forward positivity
- `scalar_convexity_g6_vs_g4` — next-order forward dispersion (Bellazzini–Riva style)
- `dispersion_tower_g6_squared_bound` — Caron-Huot, Mazac, Rastelli, Simmons-Duffin 2021
- `graviton_mixed_positivity` — Caron-Huot–Mazac–Rastelli–Simmons-Duffin (2021–2024)
- `cubic_curvature_positivity` — Caron-Huot et al 2021, 2024 (`g_R3 ≥ 0`)
- `cubic_graviton_matter_bound` — Caron-Huot–de Rham–Tolley–Zhou 2024
- `spin_four_positivity` — Caron-Huot et al 2021; Bellazzini et al 2024 (J=4 partial wave)
- `cft_flat_space_bound` — Caron-Huot et al 2024 (CFT-to-flat-space bootstrap)
- `graviton_forward_positivity` — Caron-Huot–Van Duong 2021 (two-sided, forward-limit graviton)
- `matter_s3_positivity` — Caron-Huot–Van Duong 2021 / Arkani-Hamed–Huang–Huang 2021
- `cemz_causality` — Camanho–Edelstein–Maldacena–Zhiboedov 2014 (graviton time-advance)
- `cross_sector_efthedron` — Arkani-Hamed–Huang–Huang EFThedron (cross-sector dim-8)
- `hofman_maldacena_wedge` — Hofman–Maldacena 2008 (conformal collider, `1/3 ≤ a/c ≤ 31/18`)
- `parity_violating_positivity` — Caron-Huot–de Rham–Tolley–Zhou 2024 (parity-decomposed)
- `left_handed_graviton_positivity` — Caron-Huot et al 2024 (left-helicity bound)
- `right_handed_graviton_positivity` — Caron-Huot et al 2024 (right-helicity bound)
- `parity_violating_cubic_bound` — Caron-Huot et al 2024 (parity-decomposed cubic)
- `causality_bound` — Adams et al 2006; de Rham–Tolley 2014

## Class B — Information-theoretic (7)

Holographic entropy and quantum-information bounds.

- `bekenstein_tight` — Bekenstein bound applied to the gravitational EFT
- `holographic_subadditivity` — strong subadditivity (BNOSSW 2015; Hayden–Headrick–Maloney 2013)
- `bnossw_monogamy` — BNOSSW monogamy-of-mutual-information proxy (geometric-mean form)
- `quantum_focusing_conjecture` — Bousso, Fisher, Leichenauer, Wall 2015
- `generalized_second_law` — Bekenstein 1973; Wald 1993; Sarkar–Wall 2015
- `ligo_birefringence_bound` — LIGO/Virgo non-observation of GW birefringence (O3)
- `ligo_graviton_mass_bound` — LIGO/Virgo (GW170817 + O3); Will 2018

## Class C — Gravitational universality (10)

Swampland, anomaly flow, black-hole thermodynamics, complexity.

- `eft_validity_box` — EFT cutoff; Wilson coefficients O(1) in cutoff units
- `anomaly_cancellation` — Álvarez-Gaumé–Witten 1984 (toy 4D form)
- `generalized_anomaly_inflow` — Álvarez-Gaumé–Witten 1984; gravitational anomaly inflow
- `t_hooft_anomaly_matching` — 't Hooft 1980
- `weak_gravity_conjecture` — Arkani-Hamed, Motl, Nicolis, Vafa 2007
- `wald_entropy_positivity` — Cheung–Liu–Remmen 2018; Reall–Santos 2018 (`ΔS_ext > 0 ⇔ WGC`)
- `scalar_wgc` — Palti 2017 (scalar weak gravity conjecture)
- `repulsive_force_conjecture` — Heidenreich–Reece–Rudelius 2019 (convex-hull form)
- `complexity_cutoff` — Susskind 2014 / Lloyd 2000 / Bekenstein 1981 (aggregate bound)
- `swampland_distance_conjecture` — Ooguri–Vafa 2007; Palti 2019 (review)

---

## DATA constraints (opt-in, 4)

Real experiments, off by default so the theoretical-only stack is preserved. Enabled via `build_stack(include_data=…, include_birefringence=…, include_gw_speed=…, include_gw_dispersion=…)`.

| constraint | sector | experiment | effect |
|---|---|---|---|
| `submm_gravity_yukawa_bound` | matter / scalaron | Eöt-Wash: Lee et al. PRL 124,101101 (2020); Kapner et al. (2007) | excludes the unscreened dark-energy scalaron (`g_R2 ≲ 0.063`) |
| `cosmic_birefringence_data` | parity | Minami–Komatsu PRL 125,221301 (2020); Eskilt–Komatsu 2022 | prefers nonzero positive-handed `g_R2_parity` (β=0.34°±0.09°) |
| `gw_speed_bound` | tensor (speed) | Abbott et al. ApJL 848 (2017) L13; Baker et al. 2017 | blind to higher-derivative gravity (frequency-suppressed) |
| `gw_dispersion_bound` | tensor (phase) | Abbott et al. PRL 127 (2021) 161102; Mirshekari–Yunes–Will 2012 | reaches the dark-energy cutoff via the cumulative-phase lever arm |

See [FINDINGS.md](FINDINGS.md) §3–5 for how each was confronted, and the [results index](results/INDEX.md) for the per-cycle notes.
