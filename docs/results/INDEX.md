# ITB Engine - Research Results Index

Auto-generated front door to the full research program (241 notes). Regenerate with `python tools/build_index.py`.

## Foundations (v0.x - v1.22): the original engine

| ver | note | one line |
|---|---|---|
| - | [Cross-scenario synthesis](2026-05-08-cross-scenario-synthesis.md) | Per-framework feasibility across all scenarios. |
| v0.8 | [ITB Engine — Full Battery: v0.8 baseline (8 constraints, 4 frameworks)](2026-05-08-v0.8-baseline-report.md) | _Generated: 2026-05-08T04:15:29+00:00_ |
| v0.9 | [Honest Synthesis: What the ITB Engine Has and Has Not Shown](2026-05-08-honest-synthesis.md) | From building it: |
| v1.0 | [v1.0 Findings — what changed when we replaced toy bounds with publicat](2026-05-08-v1.0-findings.md) | Adding `g_6² ≤ g_4·g_8` — the chained Cauchy-Schwarz between adjacent forward-dispersion coefficients that the Caron-Huot et al program uses — produced **8 cell |
| v1.0 | [ITB Engine — Full Battery: v1.0 — publication-grade constraints (dispe](2026-05-08-v1.0-publication-grade-report.md) | _Generated: 2026-05-08T11:32:51+00:00_ |
| v1.1 | [ITB Engine — Full Battery: v1.1 — adds BNOSSW MMI + holographic subadd](2026-05-08-v1.1-bnossw-report.md) | _Generated: 2026-05-08T11:40:31+00:00_ |
| v1.2 | [ITB Engine — Full Battery: v1.2 — adds cubic curvature constraints (g_](2026-05-08-v1.2-cubic-curvature-report.md) | _Generated: 2026-05-08T11:49:50+00:00_ |
| v1.3 | [Experimental priority ranking](2026-05-08-v1.3-experimental-priorities.md) | Baseline allowed cells (without any experiment): 3 |
| v1.4 | [Experimental priority ranking](2026-05-08-v1.4-experimental-priorities.md) | Baseline allowed cells (without any experiment): 99 |
| v1.4 | [ITB Engine — Full Battery: v1.4 — parity-violation sector active (g_R2](2026-05-08-v1.4-parity-violation-report.md) | _Generated: 2026-05-08T12:04:49+00:00_ |
| v1.5 | [First-disagreement observable ranking](2026-05-08-v1.5-first-disagreement.md) | Each row is a candidate-framework pair × observable. S/N gives the signal-to-noise ratio: how many sigmas of measurement separate the two frameworks at that obs |
| v1.6 | [ITB Engine — Full Battery: v1.6 — anomaly-flow active (parity slice fi](2026-05-08-v1.6-anomaly-flow-report.md) | _Generated: 2026-05-08T12:18:30+00:00_ |
| v1.8 | [v1.8 — Honest Synthesis After 18 Iterations](2026-05-08-v1.8-honest-synthesis.md) | What it is: |
| v1.8 | [v1.8 — The Engine's Sharpest Answer](2026-05-08-v1.8-intersection-search.md) | Constraint count: **24** |
| v1.9 | [v1.9 — Research-agent session log (Dr. M.)](2026-05-08-v1.9-research-agent-session.md) | agent shipped this iteration). Live LLM loop requires `ANTHROPIC_API_KEY`. |
| v1.10 | [v1.10 — Dr. M.'s session conclusion (after 6 iterations)](2026-05-08-v1.10-dr-m-conclusion.md) | After six iterations of additions, the engine's behavior is now well-characterized: |
| v1.10 | [v1.10 — Intersection search after Dr. M.'s 5 additions](2026-05-08-v1.10-intersection-update.md) | Total constraints: **28** |
| v1.11 | [v1.11 — Dr. M., Iteration 7: BNOSSW MMI prefactor sensitivity](2026-05-08-v1.11-dr-m-iter7-finding.md) | Three new findings that weren't visible from any prior iteration: |
| v1.11 | [Prefactor sensitivity: BNOSSW MMI](2026-05-08-v1.11-mmi-prefactor-sensitivity.md) | If a framework's transition is at prefactor ≈ 1.0 (the canonical value), its status is on a knife-edge and may not survive publication-grade encoding. If the tr |
| v1.12 | [v1.12 — Dr. M., Iteration 8: Systematic robustness map](2026-05-08-v1.12-dr-m-iter8-robustness-map.md) | The v1.11 finding (CDT on a knife-edge with BNOSSW MMI) suggested that |
| v1.12 | [v1.12 — Robustness Map (5 constraints x 5 frameworks)](2026-05-08-v1.12-robustness-map.md) | Per (framework, constraint) pair: the prefactor at which the framework's status flips, and the relative margin from canonical. |
| v1.13 | [v1.13 — Swampland variant sensitivity (RFC + Scalar WGC)](2026-05-08-v1.13-rfc-scalar-wgc-sensitivity.md) | `g_4*g_6 - g_R2 - gamma*g_R2^2 >= 0`. Canonical gamma ~ 1.0. |
| v1.14 | [v1.14 — Dr. M., Iteration 10: Per-framework feasibility projection](2026-05-08-v1.14-dr-m-iter10-projection.md) | (b) The swampland constraints are too tight at canonical prefactors. |
| v1.14 | [Per-framework feasibility projection](2026-05-08-v1.14-framework-projections.md) | For each framework, the L2-nearest feasible point in 7D Wilson- |
| v1.15 | [v1.15 - Cross-framework convergence analysis](2026-05-08-v1.15-convergence-analysis.md) | Pairwise L2 distances in 7D coefficient space, before and after |
| v1.16 | [v1.16 - Class-decomposed projection](2026-05-08-v1.16-class-decomposed-projection.md) | Each framework projected onto class-A-only, class-B-only, class-C-only feasible regions. The shift differences identify which class is responsible for which con |
| v1.17 | [v1.17 - Bayesian posterior per framework](2026-05-08-v1.17-bayesian-posterior.md) | Rejection sampling: 5000 draws from Gaussian prior centered at encoded values, sigma=0.05. Posterior = those satisfying all 31 v1.16 constraints. |
| v1.18 | [Constraint genealogy](2026-05-08-v1.18-constraint-genealogy.md) | For each constraint, which frameworks does it actively bind on (within tolerance) or solely-violate at toy values? |
| v1.19 | [Experimental priority ranking](2026-05-08-v1.19-priority-update.md) | Baseline allowed cells (without any experiment): 9 |
| v1.20 | [The Information-Theoretic Bootstrap Engine: A Toy Computational Pipeli](2026-05-08-RESEARCH-REPORT-v1.20.md) | We describe the Information-Theoretic Bootstrap (ITB) Engine, a localhost Python platform that imposes a curated set of consistency conditions on a parameterize |
| v1.21 | [v1.21 — Local LLM Backend Integrated (Gemma 4 / Pluto)](2026-05-09-v1.21-local-llm-integration.md) | Dr. M. (the research-agent persona) now has two backends: |
| v1.22 | [v1.22 — Gemma 4 native tool calling on Pluto](2026-05-09-v1.22-gemma-native-tools.md) | The local-LLM research-agent backend now uses **native OpenAI-compatible |

## Arc I - Realism audit (v1.23-26): which conclusions survive the toy prefactors

| ver | note | one line |
|---|---|---|
| v1.23 | [v1.23 — Prefactor-realism audit: which headline findings survive the t](2026-06-08-v1.23-prefactor-realism-audit.md) | Monte-Carlo runs at 300 000 draws, 16 workers, ~25 s each. |
| v1.24 | [v1.24 — Forward-limit graviton positivity: a physical replacement for ](2026-06-08-v1.24-graviton-forward-positivity.md) | The v1.23 audit demolished two of the engine's graviton-sector discriminators: |
| v1.25 | [v1.25 — Framework-coefficient audit: the other half of the toy-ness (a](2026-06-08-v1.25-framework-coefficient-audit.md) | v1.23–24 perturbed the **constraint prefactors**. But the engine's **framework |
| v1.26 | [v1.26 — Capstone: comparative survival under joint uncertainty, and wh](2026-06-08-v1.26-lqg-survival-capstone.md) | The realism program watched LQG's proposed exclusion mechanism collapse three |

## Arc II - Generative discovery (v1.27-34): new consistent theories + the parity frontier

| ver | note | one line |
|---|---|---|
| v1.27 | [v1.27 — Generative mode: theories not yet on the map, and the experime](2026-06-08-v1.27-generative-discovery.md) | Every prior cycle used the engine *defensively*: which catalogued frameworks |
| v1.28 | [v1.28 — How many consistent-theory classes? Theory-space connectivity ](2026-06-08-v1.28-theory-space-phases.md) | v1.27 suggested the feasible region fragments into ~31 islands. That count came |
| v1.29 | [v1.29 — Experiment-priority ranking on the corrected stack: the metric](2026-06-08-v1.29-experiment-priority-saturation.md) | The engine's flagship real-world output is a ranked list of experiments by how |
| v1.30 | [v1.30 — Honest experiment guidance: which observable separates the sur](2026-06-08-v1.30-honest-experiment-guidance.md) | v1.29 showed the exclusion-count priority ranking saturates (forecast-central- |
| v1.31 | [v1.31 — The consistent parity-violating branch, characterized; discove](2026-06-08-v1.31-parity-violating-branch.md) | The most genuinely novel result of the program is that a **parity-violating |
| v1.32 | [v1.32 — A catalog of possible quantum gravities: the frontier is parit](2026-06-08-v1.32-catalog-of-possible-quantum-gravities.md) | Rather than discover novel theories one at a time, this cycle maps the **full |
| v1.33 | [v1.33 — Freedom map: where consistent quantum gravity is loose vs pinn](2026-06-08-v1.33-freedom-map.md) | The generative cycles found novel theories and a parity-violating frontier. This |
| v1.34 | [v1.34 — Observable fingerprint: where the discovered theories sit, and](2026-06-08-v1.34-fingerprint-discovered.md) | The engine-discovered theories are now first-class encoders (`DiscoveredNovel`, |

## Arc III - Observability (v1.35-38): Fisher sloppiness, spin-4, the parity ceiling

| ver | note | one line |
|---|---|---|
| v1.35 | [v1.35 — Fisher sloppiness: the new-physics freedom hides in the unmeas](2026-06-08-v1.35-fisher-sloppiness.md) | v1.29 showed the exclusion-count priority metric saturates. The principled |
| v1.36 | [v1.36 — Breaking the matter degeneracy: spin-4 partial wave isolates g](2026-06-08-v1.36-breaking-the-matter-degeneracy.md) | v1.35 found the matter couplings g_4/g_6/g_8 observationally degenerate from a |
| v1.37 | [v1.37 — The parity ceiling: ≈0.14, set by anomaly inflow, flat across ](2026-06-08-v1.37-parity-ceiling.md) | Gravitational parity violation is now the top testable new-physics signal |
| v1.38 | [v1.38 — The map in one picture: catalogued frameworks on the parity fl](2026-06-08-v1.38-catalog-projection.md) | Two axes emerged as the program's most important: **g_8** (the loosest direction |

## Arc IV - The decisive experiment (v1.39-44): GIE, sub-mm gravity, the CC link

| ver | note | one line |
|---|---|---|
| v1.39 | [v1.39 — The decisive experiment: gravitationally-induced entanglement ](2026-06-08-v1.39-the-decisive-experiment.md) | actually move quantum gravity. |
| v1.40 | [v1.40 — Dr. M. converges on short-range gravity; the target sits at th](2026-06-08-v1.40-yukawa-target-darkenergy.md) | Asked for the single experiment most likely to decisively change quantum gravity |
| v1.41 | [v1.41 — The spec sheet: what precision actually discriminates the theo](2026-06-08-v1.41-experimental-spec-sheet.md) | v1.39–40 identified the decisive program and the target length (70–130 µm). This |
| v1.42 | [v1.42 — Decisive-experiment observables, encoded as first-class engine](2026-06-08-v1.42-gravitational-observables.md) | v1.39–41 built the decisive-experiment program as standalone analysis scripts. |
| v1.43 | [v1.43 — The full program resolves 20 of 21 theory pairs; string≈CDT is](2026-06-08-v1.43-combined-discrimination.md) | With matter amplitude, graviton amplitude, sub-mm Yukawa, and gravitational |
| v1.44 | [ITB Engine — Research Report v1.44 (2026-06-08)](2026-06-08-RESEARCH-REPORT-v1.44.md) | synthesizes 22 cycles (v1.23–v1.44) run on the Vulcan compute server with the |
| v1.44 | [v1.44 — Why the dark-energy-scale cutoff is motivated, not assumed: th](2026-06-08-v1.44-cosmological-constant-cutoff.md) | The whole discriminating program (v1.40–43) rests on one assumption: the |

## Arc V - Dark-energy axion + synthesis (v1.45-51): CMB EB, DESI, the scorecard

| ver | note | one line |
|---|---|---|
| v1.46 | [v1.46 — The dark-energy axion: tying cosmic acceleration, cosmic biref](2026-06-08-v1.46-dark-energy-axion.md) | The same axion's gravitational coupling lands in the engine's allowed range. |
| v1.47 | [v1.47 — One field, four probes: the swampland dark-energy axion lands ](2026-06-08-v1.47-four-probe-coincidence.md) | If the dark-energy field is a quintessence axion (v1.46), it is *fully specified* |
| v1.48 | [v1.48 — The cosmic-birefringence prediction as a real CMB EB spectrum ](2026-06-08-v1.48-cmb-eb-spectrum.md) | v1.46/47 predicted cosmic birefringence β ≈ 0.34° from the dark-energy axion. |
| v1.49 | [v1.49 — Solving the axion EOM: w₀ hits DESI, wₐ is the thawing track (](2026-06-08-v1.49-quintessence-wz-vs-desi.md) | v1.47 used the schematic w₀ = −1 + c²/3. Here we solve the **actual** quintessence |
| v1.50 | [v1.50 — Can a different potential reach DESI's steep wₐ? No — the shal](2026-06-08-v1.50-potential-shapes-vs-desi.md) | v1.49 found the minimal cosine axion sits on the shallow thawing track. Does a |
| v1.51 | [v1.51 — The ITB prediction scorecard: every falsifiable claim, graded](2026-06-08-v1.51-prediction-scorecard.md) | This is the experimentalist's cheat-sheet and an honest self-audit: every |

## Arc VI - The multi-probe parity web (v1.52-57): inference, chiral HD, ringdown, forecast

| ver | note | one line |
|---|---|---|
| v1.52 | [v1.52 — The engine as a live inference machine: which theory does the ](2026-06-08-v1.52-inference-engine.md) | A new engine layer turns the question around: not "which theories are |
| v1.53 | [v1.53 — Chiral Hellings–Downs: a new pulsar-timing probe of the parity](2026-06-08-v1.53-chiral-hellings-downs.md) | Asked for a genuinely new observational handle on the parity sector, Dr. M. |
| v1.54 | [v1.54 — Ringdown QNM parity splitting: a predicted NULL that explains ](2026-06-08-v1.54-ringdown-qnm.md) | In dynamical Chern–Simons gravity the parity coupling g_R2_parity splits the |
| v1.55 | [v1.55 — 2030 discrimination forecast: would next-decade data identify ](2026-06-08-v1.55-forecast-2030.md) | For each "nature = theory X" hypothesis, simulate the projected ~2030 |
| v1.56 | [v1.56 — Multimessenger parity: the GW+EM birefringence test (and why t](2026-06-08-v1.56-multimessenger.md) | If one dark-energy axion (v1.46) sources both gravitational parity (g_R2_parity, |
| v1.57 | [v1.57 — Capstone: the multi-probe parity web, and the close of the cre](2026-06-08-v1.57-parity-web-capstone.md) | The engine's signature prediction — a parity-violating gravity with |

## Arc VII - Framework / scope / constraint expansion (v1.58-99): new theories, 3-D scope, new bounds

| ver | note | one line |
|---|---|---|
| v1.58 | [v1.58 — New frameworks (Hořava–Lifshitz, Causal Sets, GFT) reveal the ](2026-06-08-v1.58-new-frameworks-and-engine-scope.md) | The catalogue had 5 named frameworks (+3 engine-discovered). This adds three more |
| v1.59 | [v1.59 — The engine now declares its own validity scope](2026-06-08-v1.59-engine-scope-flags.md) | v1.58 found that the engine's constraints only validly apply to local, |
| v1.60 | [v1.60 — Resolving the GFT borderline: the pass/fail boundary is one cu](2026-06-08-v1.60-gft-boundary.md) | Group Field Theory's verdict was left hanging on its cubic curvature coupling. |
| v1.61 | [v1.61 — Two new constraints from new principles: cross-sector EFThedro](2026-06-08-v1.61-new-constraints.md) | Two genuinely new consistency constraints, each from a *different* physical |
| v1.62 | [v1.62 — The realism corrections didn't tweak the picture; they created](2026-06-08-v1.62-original-vs-corrected.md) | How much did the v1.23–25 corrections (convex-hull RFC, geometric BNOSSW) change |
| v1.63 | [v1.63 — `itb predict <framework>`: the whole program as one command](2026-06-08-v1.63-predict-cli.md) | A unified predictions layer that turns the entire program into a usable tool: |
| v1.64 | [v1.64 — The cross-sector EFThedron is load-bearing: α between 1.1 and ](2026-06-08-v1.64-efthedron-sensitivity.md) | The cross-sector EFThedron bound g_8·g_R2 ≥ α·g_6·g_R3 (v1.61) has an O(1) |
| v1.65 | [v1.65 — Emergent gravity, and a third dimension of engine scope (funda](2026-06-08-v1.65-emergent-gravity.md) | A 12th candidate framework — **Verlinde entropic / emergent gravity** — chosen |
| v1.66 | [v1.66 — Survival on the full 35-constraint stack: the new bounds shrin](2026-06-08-v1.66-survival-full-stack.md) | Joint coefficient × prefactor survival, now on the full **35-constraint** stack |
| v1.67 | [v1.67 — A holographic observable: η/s, an orthogonal discriminator (ev](2026-06-08-v1.67-holographic-eta-over-s.md) | A new holographic observable in `gravitational_observables.py`, |
| v1.69 | [v1.69 — The allowed region, seen directly: a 2-D feasibility slice in ](2026-06-08-v1.69-feasibility-slice-gR2-gR3.md) | Every prior cycle reported feasibility as a *number* (survival fraction, a |
| v1.70 | [v1.70 — The a-theorem in the toy basis: a constraint of new origin, no](2026-06-08-v1.70-a-theorem-basis-degeneracy.md) | I set out to add a *genuinely new* constraint of independent physical origin — |
| v1.71 | [v1.71 — The basis extension that makes RG-monotonicity load-bearing: t](2026-06-08-v1.71-ac-wedge-basis-extension.md) | v1.70 ended with a precise diagnosis: the a-theorem (and every other anomaly / |
| v1.72 | [v1.72 — One coupling, two observables: the a/c wedge and η/s are the s](2026-06-08-v1.72-one-coupling-two-observables.md) | GB literature (Dr. M. again could not converge the arithmetic; derived here and |
| v1.73 | [v1.73 — How constrained is a consistent quantum-gravity EFT? The dimen](2026-06-08-v1.73-island-census.md) | Every prior cycle excluded *parts* of theory-space. v1.73 asks the global, |
| v1.74 | [v1.74 — The most robustly-consistent EFT: the island's center and its ](2026-06-08-v1.74-island-center.md) | The most robustly-consistent EFT is closest to string theory's tree-level EFT. |
| v1.75 | [v1.75 — Error bars on the central prediction: does the most-robust EFT](2026-06-08-v1.75-central-prediction-error-bars.md) | The "string tree-EFT is nearest" claim is a plurality, not a robust majority. |
| v1.76 | [v1.76 — Confronting the central prediction with real sub-mm gravity da](2026-06-08-v1.76-submm-confrontation.md) | The program has spent six cycles building toward a falsifiable central prediction. |
| v1.77 | [v1.77 — The engine ingests real data: the sub-mm bound as the first ex](2026-06-08-v1.77-ingest-data.md) | Every one of the engine's ~36 constraints has been a **theoretical axiom** — |
| v1.78 | [v1.78 — The second experiment: cosmic birefringence, and the engine's ](2026-06-08-v1.78-cosmic-birefringence.md) | v1.77 ingested an *exclusion* (Eöt-Wash sub-mm gravity) in the matter sector. v1.78 |
| v1.79 | [v1.79 — The EFT the data points to: a tension, and the engine's predic](2026-06-08-v1.79-data-driven-eft.md) | The plan was to construct the single best EFT consistent with **theory + sub-mm |
| v1.80 | [v1.80 — Is the birefringence-vs-gravity tension robust? Stress-testing](2026-06-08-v1.80-tension-robustness.md) | v1.79's headline — anomaly inflow + unscreened sub-mm gravity cap cosmic |
| v1.81 | [v1.81 — One parity coupling, three messengers: is the data-driven EFT ](2026-06-08-v1.81-multimessenger-parity.md) | The data-driven EFT (v1.79) carries a gravitational Chern–Simons / Pontryagin |
| v1.82 | [v1.82 — Black-hole entropy and the WGC: the engine's coefficients fix ](2026-06-08-v1.82-bh-entropy-wgc.md) | After the data/parity arc, v1.82 opens a genuinely new connection: the engine's |
| v1.83 | [v1.83 — The master predictions scorecard & falsifiable roadmap](2026-06-08-v1.83-master-scorecard.md) | After a long arc (v1.71–82) the program has accumulated many distinct results — |
| v1.84 | [v1.84 — The third experiment: GW170817 graviton speed, and the honest ](2026-06-08-v1.84-gw-speed.md) | Sub-mm gravity (v1.77) squeezed the *matter* sector; cosmic birefringence (v1.78) |
| v1.85 | [v1.85 — The proper tensor probe: the LIGO dispersion test reaches the ](2026-06-08-v1.85-gw-dispersion.md) | v1.84 found GW170817's arrival-time **speed** test blind to the engine's |
| v1.86 | [v1.86 — R² is the inflaton: the engine's g_R2 sector is the observatio](2026-06-08-v1.86-inflation.md) | Every prior cycle treated the R² coupling g_R2 as a *late-universe* object — a |
| v1.87 | [v1.87 — The Gödel test: is the engine internally consistent, and what ](2026-06-08-v1.87-godel-test.md) | The first of a new "meta-experiment" track (auditing the engine itself rather than |
| v1.88 | [v1.88 — The minimum decisive experiment set: what is the smallest expe](2026-06-08-v1.88-min-experiment-set.md) | The minimum decisive experiment program is 6 measurements: |
| v1.89 | [v1.89 — The phylogenetic tree of quantum gravities: are the frameworks](2026-06-08-v1.89-phylogeny.md) | All frameworks lie in the basin of the single UV fixed point and flow toward it |
| v1.90 | [v1.90 — The Diósi–Penrose exclusion: is gravity classical?](2026-06-08-v1.90-diosi-penrose.md) | The engine assumes gravity is **quantum** (it bootstraps a graviton EFT). The |
| v1.91 | [v1.91 — The strong-field probe: do neutron-star tides (GW170817) see t](2026-06-08-v1.91-neutron-star.md) | All four ingested experiments are weak-field. Neutron stars are the strongest |
| v1.92 | [v1.92 — The convergence forecast: when does the data pin the quantum-g](2026-06-08-v1.92-convergence-forecast.md) | g_8 (the s⁴ matter moment) and g_R3 (cubic curvature), have no funded experiment. |
| v1.93 | [v1.93 — Constraint Jenga: which consistency conditions are load-bearin](2026-06-08-v1.93-constraint-jenga.md) | The engine imposes 37 theoretical constraints. **How many actually do work?** We pull |
| v1.94 | [v1.94 — The gravitational double-copy test: is the consistent graviton](2026-06-08-v1.94-double-copy.md) | The **double copy** (Bern–Carrasco–Johansson; KLT) builds gravity from gauge × gauge: |
| v1.95 | [v1.95 — Genetic recombination: breeding the quantum-gravity frameworks](2026-06-08-v1.95-genetic-recombination.md) | Earlier discovery cycles found new consistent theories by *optimization*. v1.95 tries |
| v1.96 | [v1.96 — The species scale: tying the EFT cutoff to a tower of states (](2026-06-08-v1.96-species-scale.md) | Dvali's **species scale**: with N light species below the cutoff, gravity becomes |
| v1.97 | [v1.97 — The adversarial self-audit: which constraints are sole gatekee](2026-06-08-v1.97-adversarial-audit.md) | The Gödel test (v1.87) and constraint Jenga (v1.93) audited the engine's logic and |
| v1.98 | [v1.98 — Holographic complexity growth: do higher-derivative gravities ](2026-06-08-v1.98-complexity-rate.md) | 'Complexity = Action' (Brown–Roberts–Susskind–Swingle–Zhao 2016): the late-time growth |
| v1.99 | [v1.99 — The a-theorem along the RG phylogeny: does the central charge ](2026-06-09-v1.99-a-theorem-flow.md) | v1.89 treated the Wilson coefficients as running couplings flowing to a UV fixed point. |

## Arc VIII - Synthesis and self-audit (v2.00-10): Bayesian comparison, falsifiers, robustness

| ver | note | one line |
|---|---|---|
| v2.0 | [The ITB Engine v2.0 — A Research Report](2026-06-09-v2.0-RESEARCH-REPORT.md) | An information-theoretic bootstrap for quantum gravity: constraining the higher-derivative EFT, confronting it with data, and auditing the engine itself. |
| v2.01 | [v2.01 — Bayesian model comparison: which quantum-gravity framework doe](2026-06-09-v2.01-bayesian-model-comparison.md) | The whole catalogue of 14 frameworks, one posterior. Given the ingested data, **which |
| v2.02 | [v2.02 — Inverse constraint design: which new bound would most shrink t](2026-06-09-v2.02-inverse-constraint-design.md) | v1.93 *removed* each constraint to rank irreplaceability. v2.02 *adds* hypothetical ones: |
| v2.03 | [v2.03 — The holographic (a,c) RG portrait: the conformal-collider plan](2026-06-09-v2.03-ac-portrait.md) | The Euler/Weyl² basis split (v1.71) turned out to be the spine of the engine. v2.03 draws |
| v2.04 | [v2.04 — The minimal falsifier: the single cheapest measurement that wo](2026-06-09-v2.04-minimal-falsifier.md) | The data-driven EFT (v1.79) makes a 9-observable fingerprint. v2.04 asks the |
| v2.05 | [v2.05 — The observable redundancy map: how many independent things can](2026-06-09-v2.05-observable-redundancy.md) | The engine has 9 observables but only 8 coefficients on a ~3.4-dimensional island |
| v2.06 | [v2.06 — The information-geometry curvature map: the island as a Rieman](2026-06-09-v2.06-info-geometry.md) | Treat the space of EFTs as a manifold with the **Fisher information metric** |
| v2.07 | [v2.07 — The robustness jackknife: which of the program's headline find](2026-06-09-v2.07-robustness-jackknife.md) | v1.80 stress-tested *one* finding (the birefringence tension) against the toy-prefactor |
| v2.08 | [v2.08 — The alternative-birefringence EFTs: how the favored quantum gr](2026-06-09-v2.08-alt-birefringence.md) | v2.04 found the data-driven EFT is a *one-observable theory* — its whole case rests on |
| v2.09 | [v2.09 — The thematic taxonomy: a navigable map of the program](2026-06-09-v2.09-taxonomy.md) | empirical swampland** opens up at v1.69–v1.85 (data ingestion); and **meta-experiments |
| v2.10 | [v2.10 — Capstone: the ITB program in one page](2026-06-09-v2.10-capstone.md) | Take the space of higher-derivative quantum-gravity EFTs. Impose **every consistency |

## Arc IX - Agent-swarm research loop (v2.11+): adversarial cycles and live compute

| ver | note | one line |
|---|---|---|
| v2.11 | [v2.11 Agent Swarm Research Program (2026-06-19)](2026-06-19-v2.11-agent-swarm-research-program.md) | Use a coordinated adversarial swarm to push the ITB engine toward a quantum-gravity discriminator: a compact set of consistency constraints plus measurements th |
| v2.12 | [v2.12 - Agent-swarm cycle 1: boundary audit and parity contingency](2026-06-19-v2.12-agent-swarm-cycle-1.md) | Run the engine as a research team and ask what survives adversarial review: |
| v2.13 | [v2.13 - Full-basis connectivity: g_C restores the topology test](2026-06-19-v2.13-full-basis-connectivity.md) | v2.12 identified a stale topology path: `experiments/phases.py` still used a |
| v2.14 | [v2.14 - Parity bridge diagnostic: the four lobes are a distance-prior ](2026-06-19-v2.14-parity-bridge-diagnostic.md) | v2.13 found four straight-line components in the full 8D phase graph. The open question was |
| v2.15 | [v2.15 - Distance-prior variant: parity lobes reconnect when parity zer](2026-06-19-v2.15-distance-prior-variant.md) | v2.14 showed that the four v2.13 parity lobes are split by the hard nonzero-threshold |
| v2.16 | [v2.16 - Continuous distance-prior diagnostics: parity topology is stil](2026-06-19-v2.16-continuous-distance-prior.md) | v2.14 and v2.15 showed that the four v2.13 parity lobes are split by the hard |
| v2.17 | [v2.17 - Tower/species surrogate gate: continuous replacements pass top](2026-06-19-v2.17-tower-surrogate-distance.md) | v2.16 showed that the parity-lobe topology is functional-form dependent. The next |
| v2.18 | [v2.18 - Tower-surrogate overlap audit: cleaner priors, still redundant](2026-06-19-v2.18-tower-surrogate-overlap.md) | v2.17 showed that continuous tower/species surrogates pass a basic sanity gate: they |
| v2.19 | [v2.19 - Latent moduli/tower diagnostic: explicit tower chain, still no](2026-06-19-v2.19-latent-moduli-tower.md) | v2.18 closed the simple tower-norm loop: continuous species/tower priors are better |
| v2.20 | [v2.20 - Explicit tower-coordinate basis: a nonredundant 9D gate, not f](2026-06-19-v2.20-explicit-tower-basis.md) | v2.16-v2.19 showed that every coefficient-only replacement for the hard distance prior |
| v2.21 | [v2.21 - Tower-observable thresholds: what would make the 9D gate measu](2026-06-19-v2.21-tower-observable-thresholds.md) | v2.20 found a nonredundant 9D tower gate, but it is not framework discrimination until |
| v2.22 | [v2.22 - Tower framework scenarios: exclusions are assignment-dependent](2026-06-19-v2.22-tower-framework-scenarios.md) | v2.21 identified concrete tower-observable thresholds, but named framework encoders still |
| v2.23 | [v2.23 - Tower measurement design: observations reduce assignments, not](2026-06-19-v2.23-tower-measurement-design.md) | v2.22 showed that framework exclusions depend on how `phi_tower` is assigned. v2.23 asks: |
| v2.24 | [v2.24 - Tower spectrum readiness: framework claims are blocked on miss](2026-06-19-v2.24-tower-spectrum-readiness.md) | v2.23 identified which tower measurements would reduce assignment ambiguity. v2.24 asks: |
| v2.25 | [v2.25 - Tower adapter thresholds: what future spectra must prove](2026-06-19-v2.25-tower-adapter-thresholds.md) | v2.24 added the optional tower-spectrum adapter but found no native framework spectra. |
| v2.26 | [v2.26 - Tower literature seed audit: qualitative SDC sources are not a](2026-06-19-v2.26-tower-literature-seed-audit.md) | v2.25 defined the numerical thresholds a future framework tower adapter must clear. |
| v2.27 | [v2.27 - SDC distance requirements: turning tower seeds into adapter ta](2026-06-19-v2.27-sdc-distance-requirements.md) | v2.26 found qualitative SDC sources but no actionable `TowerSpectrum`. v2.27 asks: |
| v2.28 | [v2.28 - SDC adapter candidate scan: the conversion path is ready](2026-06-19-v2.28-sdc-adapter-candidate-scan.md) | v2.27 translated SDC slopes into required moduli distances. v2.28 asks: |
| v2.29 | [v2.29 - KK radius adapter scan: radius ratios can drive the tower gate](2026-06-19-v2.29-kk-radius-adapter-scan.md) | v2.28 showed how to convert an SDC moduli distance into a `TowerSpectrum`. v2.29 asks: |
| v2.30 | [v2.30 - KK radius precision requirements: how accurate the radius must](2026-06-19-v2.30-kk-radius-precision-requirements.md) | v2.29 gave radius-ratio thresholds at fixed uncertainty. v2.30 asks the inverse question: |
| v2.31 | [v2.31 - Tower evidence gate: math is not enough for a framework claim](2026-06-19-v2.31-tower-evidence-gate.md) | v2.30 made the KK-radius route precise. v2.31 asks: |
| v2.32 | [v2.32 - Discriminator frontier: what is actually blocking a claim](2026-06-19-v2.32-discriminator-frontier.md) | v2.31 added a provenance gate for tower claims. v2.32 asks: |
| v2.33 | [v2.33 - Tower evidence sourceability: current encoders cannot supply t](2026-06-19-v2.33-tower-evidence-sourceability.md) | v2.32 identified the next required artifact: |
| v2.34 | [v2.34 - Quintic KK tower evidence candidate: first sourced row, still ](2026-06-19-v2.34-quintic-tower-evidence-candidate.md) | v2.33 proved that current framework encoders do not already contain tower evidence. |
| v2.35 | [v2.35 - Quintic SDC bound audit: finite-range evidence is not an asymp](2026-06-19-v2.35-quintic-sdc-bound-audit.md) | v2.34 added the first non-synthetic, primary-source tower candidate. v2.35 asks: |
| v2.36 | [v2.36 - Quintic promotion forecast: ownership would improve, exclusion](2026-06-19-v2.36-quintic-promotion-forecast.md) | v2.34 produced a schema-ready sourced tower candidate. v2.35 showed it is not an |
| v2.37 | [v2.37 - Large-volume SDC benchmark: math exclusion, still not a framew](2026-06-19-v2.37-large-volume-sdc-benchmark.md) | v2.36 ended with two possible next moves: asymptotic lightest-tower extraction or a |
| v2.38 | [v2.38 - Analytic KK tower benchmark: rates are enough, ownership is no](2026-06-19-v2.38-analytic-kk-tower-benchmark.md) | v2.37 found a large-volume benchmark that crosses the tower threshold, but still lacks |
| v2.39 | [v2.39 - Tower-gate calibration: positive controls fail, so no discrimi](2026-06-19-v2.39-tower-gate-positive-control-calibration.md) | v2.37 and v2.38 found primary-source benchmarks that cross the current tower threshold. |
| v2.40 | [v2.40 - Tower-gate recalibration options: block promotion before chang](2026-06-19-v2.40-tower-gate-recalibration-options.md) | v2.39 showed that the current tower gate rejects known string-compatible positive |
| v2.41 | [v2.41 - Tower promotion guard: positive controls blocked before claims](2026-06-19-v2.41-tower-promotion-guard-audit.md) | v2.40 recommended adding a promotion guard before changing tower-gate math. v2.41 asks: |
| v2.42 | [v2.42 - Frontier status matrix: guard-blocked is not claim-ready](2026-06-19-v2.42-discriminator-frontier-status-matrix.md) | v2.41 added a promotion guard. v2.42 asks: |
| v2.43 | [v2.43 - Post-guard discriminator frontier: live catalogue is still blo](2026-06-19-v2.43-post-guard-discriminator-frontier.md) | v2.41 and v2.42 installed and tested the tower-promotion guard. v2.43 asks: |
| v2.44 | [v2.44 - Tower source-scope classifier: guard-ready is not source-ready](2026-06-19-v2.44-tower-source-scope-classifier.md) | v2.41 added a promotion guard for known positive controls. v2.44 asks: |
| v2.45 | [v2.45 - Generic framework claim guard: promotion-ready is not claim-re](2026-06-19-v2.45-generic-framework-claim-guard.md) | Artifacts: |
| v2.46 | [v2.46 - Native tower ownership frontier: the live blocker is adapter a](2026-06-19-v2.46-native-tower-ownership-frontier.md) | v2.45 made promotion-ready evidence insufficient for a framework claim. v2.46 |
| v2.47 | [v2.47 - Native adapter acceptance harness: future adapters have a live](2026-06-19-v2.47-native-adapter-acceptance-harness.md) | v2.46 showed that no live framework currently exposes native tower evidence. v2.47 |
| v2.48 | [v2.48 - Candidate native-adapter promotion audit: existing evidence ca](2026-06-19-v2.48-candidate-native-adapter-promotion-audit.md) | v2.47 proved that a future native adapter will route through the live |
| v2.49 | [v2.49 - Birefringence evidence freshness: alive, but not claimable](2026-06-19-v2.49-birefringence-evidence-freshness.md) | The tower/native route is now blocked on missing framework-owned spectra rather than engine plumbing. The best non-tower route is the data-driven EFT, but that  |
| v2.50 | [v2.50 - Weyl/g8 discriminator frontier: geometry confirmed, not yet a ](2026-06-19-v2.50-weyl-g8-discriminator-frontier.md) | v2.49 kept the birefringence/data-driven route alive, but still one-observable dominated. The next non-tower route is the full-basis frontier identified in v2.0 |
| v2.51 | [v2.51 - Weyl/g8 observable sourceability: source-rich, measurement-blo](2026-06-19-v2.51-weyl-g8-observable-sourceability.md) | v2.50 confirmed a robust non-tower frontier: `g_C` / Weyl^2 is the fattest raw island direction and `g_8` is the next single-coefficient direction. The open que |
| v2.52 | [v2.52 - Non-tower promotion guard: internal cuts cannot become claims](2026-06-19-v2.52-nontower-promotion-guard.md) | v2.49, v2.50, and v2.51 left three non-tower routes alive but non-claimable: |
| v2.53 | [v2.53 - Unified discriminator route frontier: organized, still unsolve](2026-06-19-v2.53-unified-discriminator-route-frontier.md) | After v2.48-v2.52, the program has multiple live or partially live routes, each with different blockers. This audit consolidates them into one route frontier ta |
| v2.54 | [v2.54 - g8 high-moment measurement specification: the route is defined](2026-06-19-v2.54-g8-high-moment-measurement-specification.md) | v2.53 made `matter_high_moment_g_8` the highest-priority unsolved route. The |
| v2.55 | [v2.55 - g8 existing measurement packet search: public data exists, but](2026-06-19-v2.55-g8-existing-measurement-packet-search.md) | v2.54 defined the packet needed to promote the `matter_high_moment_g_8` route. |
| v2.56 | [v2.56 - Birefringence parity adapter requirements: beta is alive, the ](2026-06-19-v2.56-birefringence-parity-adapter-requirements.md) | v2.49 kept cosmic birefringence empirically alive, and v2.52/v2.53 blocked it on |
| v2.57 | [v2.57 - Birefringence prediction non-circularity: no source-backed bet](2026-06-19-v2.57-birefringence-prediction-noncircularity-audit.md) | v2.56 showed that the cosmic-birefringence route needs a source-backed adapter |
| v2.58 | [v2.58 - Birefringence adapter sourceability: CMB beta is not a direct ](2026-06-19-v2.58-birefringence-adapter-literature-sourceability.md) | v2.56 and v2.57 showed that the engine needs a source-backed map from CMB |
| v2.59 | [v2.59 - Parity route split: CMB beta retired as a direct gravity-parit](2026-06-19-v2.59-parity-route-split-frontier.md) | v2.58 blocked the direct CMB-beta to gravitational-parity map. This audit turns |
| v2.60 | [v2.60 - GW parity measurement packet search: constraints exist, no eng](2026-06-19-v2.60-gw-parity-measurement-packet-search.md) | v2.59 retired CMB cosmic-birefringence beta as a direct |
| v2.61 | [v2.61 - GW parity adapter readiness: public likelihood material is not](2026-06-19-v2.61-gw-parity-adapter-readiness.md) | v2.60 found that existing GW parity papers contain real constraints but no |
| v2.62 | [v2.62 - GW parity native packet registry: source-ready, non-promoting](2026-06-19-v2.62-gw-parity-native-packet-registry.md) | v2.61 showed that public GW parity likelihood material exists, but not in the |
| v2.63 | [v2.63 - GW parity PPV adapter spec: intermediate basis chosen, formula](2026-06-19-v2.63-gw-parity-ppv-adapter-spec.md) | v2.62 registered Ng and Callister as native, non-promoting GW parity packets. |
| v2.64 | [v2.64 - GW parity formula implementation: source-native log gain only](2026-06-19-v2.64-gw-parity-ppv-formula-implementation.md) | v2.63 chose the PPV amplitude branch as the intermediate target but left the |
| v2.65 | [v2.65 - GW parity Callister posterior parser: release schema ready, re](2026-06-19-v2.65-gw-parity-callister-posterior-parser.md) | v2.64 implemented source-native GW parity formulas but left posterior ingestion |
| v2.66 | [v2.66 - GW parity Callister real release probe: fixed-rate files inges](2026-06-19-v2.66-gw-parity-callister-real-release-probe.md) | v2.65 implemented the Callister fixed-rate HDF parser contract on |
| v2.67 | [v2.67 - GW parity Callister variable evolution probe: sample file inge](2026-06-19-v2.67-gw-parity-callister-variable-evolution-probe.md) | v2.66 verified all eight Callister fixed-rate HDF products. This iteration asks |
| v2.68 | [v2.68 - GW parity Callister sample density adapter: source-native hist](2026-06-19-v2.68-gw-parity-callister-sample-density-adapter.md) | v2.67 parsed the Callister variable-evolution HDF file, but it was sample-based |
| v2.69 | [v2.69 - GW parity Callister fixed-variable comparison: source-native s](2026-06-19-v2.69-gw-parity-callister-fixed-variable-comparison.md) | v2.68 converted the Callister variable-evolution samples into normalized |
| v2.70 | [v2.70 - GW parity PPV convention audit: candidates identified, promoti](2026-06-19-v2.70-gw-parity-ppv-convention-audit.md) | v2.69 quantified Callister source-native posterior sensitivity. This iteration |
| v2.71 | [v2.71 - GW parity Ng Gaussian posterior parser: source-native NPZ inge](2026-06-19-v2.71-gw-parity-ng-gaussian-posterior-parser.md) | v2.70 identified Ng as the closest source-backed route to a Jenks `beta_1_0` |
| v2.72 | [v2.72 - GW parity Ng event-level parser: full Feather table ingested](2026-06-19-v2.72-gw-parity-ng-event-level-feather-parser.md) | v2.71 verified the compact Ng Gaussian hyperposterior NPZ. This iteration asks |
| v2.73 | [v2.73 - GW parity Ng restricted likelihood: source result reproduced](2026-06-19-v2.73-gw-parity-ng-restricted-likelihood.md) | v2.72 verified and parsed the full Ng event-level `kappa` table. This iteration |
| v2.74 | [v2.74 - GW parity Ng PPV beta candidate: packet ready, engine blocked](2026-06-19-v2.74-gw-parity-ng-ppv-beta-candidate.md) | v2.73 reproduced the Ng restricted global-`kappa` likelihood. This iteration |
| v2.75 | [v2.75 - GW parity engine-axis audit: Ng PPV cannot promote](2026-06-19-v2.75-gw-parity-engine-axis-audit.md) | v2.74 produced a source-native Ng/Jenks `beta_1_0` candidate packet. This |
| v2.76 | [v2.76 - GW parity route decision: direct Ng promotion retired](2026-06-19-v2.76-gw-parity-route-decision.md) | v2.75 showed that no current engine parity axis can accept the Ng/Jenks |
| v2.77 | [v2.77 - Post-GW retirement frontier: g8 is next](2026-06-19-v2.77-post-gw-retirement-frontier.md) | v2.76 retired direct Ng PPV promotion for the current engine. This iteration asks |
| v2.78 | [v2.78 - g8 current source recheck: theory bridges, no packet](2026-06-19-v2.78-g8-current-source-recheck.md) | v2.77 selected `g8_high_moment_measurement` as the next best route. This |
| v2.79 | [v2.79 - g8 adapter acceptance harness: future gate ready, no real pack](2026-06-19-v2.79-g8-adapter-acceptance-harness.md) | v2.78 found useful partial-wave and detector-theory bridges, but no |
| v2.80 | [v2.80 - g8 public data acquisition: data exists, no adapter packet](2026-06-19-v2.80-g8-public-data-product-acquisition-audit.md) | v2.79 made the `g_8` adapter gate executable. This iteration asks whether any |
| v2.81 | [v2.81 - g8 route decision: direct public-data promotion retired](2026-06-19-v2.81-g8-route-decision.md) | v2.80 found public energy-correlator data products and useful theory bridges, but |
| v2.82 | [v2.82 - Post-g8 frontier: native tower evidence is next](2026-06-19-v2.82-post-g8-route-decision-frontier.md) | v2.81 retired direct promotion of current public energy-correlator products into |
| v2.83 | [v2.83 - Native tower source audit: no registered adapter](2026-06-19-v2.83-native-tower-current-source-audit.md) | v2.82 selected `native_tower_evidence` as the next no-new-experiment route. This |
| v2.84 | [v2.84 - Native tower route decision: direct source promotion retired](2026-06-19-v2.84-native-tower-route-decision.md) | v2.83 found useful tower-like sources but no registered-framework native adapter. |
| v2.85 | [v2.85 - Post-native frontier: g8 adapter derivation is next](2026-06-19-v2.85-post-native-tower-route-decision-frontier.md) | v2.84 retired direct promotion of current native-tower-like sources. This |
| v2.86 | [v2.86 - g8 adapter derivation audit: no source-backed identity](2026-06-19-v2.86-g8-adapter-derivation-source-audit.md) | v2.85 selected `source_backed_g8_adapter_derivation` as the next route. This |
| v2.87 | [v2.87 - g8 derivation route decision: current sources retired](2026-06-19-v2.87-g8-adapter-derivation-route-decision.md) | v2.86 found no source-backed operator identity from detector/energy-correlator |
| v2.88 | [v2.88 - Post-g8 derivation frontier: direct measurement is next](2026-06-19-v2.88-post-g8-derivation-route-decision-frontier.md) | v2.87 retired current-source `g_8` adapter derivation. This iteration asks which |
| v2.89 | [v2.89 - g8 direct measurement feasibility: external experiment require](2026-06-19-v2.89-g8-direct-measurement-feasibility-audit.md) | v2.88 selected `new_spin4_or_detector_g8_measurement` as the next route. This |
| v2.90 | [v2.90 - g8 direct measurement route decision: external dependency](2026-06-19-v2.90-g8-direct-measurement-route-decision.md) | v2.89 showed that the repo cannot create the missing direct spin-4/detector |
| v2.91 | [v2.91 - Post-direct-g8 frontier: external-only, no claim-ready route](2026-06-19-v2.91-post-g8-direct-measurement-frontier.md) | v2.90 retired direct in-repo execution of the spin-4/detector `g_8` |
| v2.92 | [v2.92 - External evidence packet contract: missing objects made explic](2026-06-19-v2.92-external-evidence-packet-contract.md) | v2.91 found no current in-repo promotion-ready route. This iteration asks what a |
| v2.93 | [v2.93 - External evidence intake gate: executable rejection path](2026-06-19-v2.93-external-evidence-intake-gate.md) | v2.92 defined packet contracts for retained external routes. This iteration asks |
| v2.94 | [v2.94 - Current external packet probe: no source satisfies the gate](2026-06-19-v2.94-current-external-packet-probe.md) | v2.93 made the external evidence intake gate executable. This iteration asks |
| v2.95 | [v2.95 - External dependency blocker synthesis: current run cannot prom](2026-06-19-v2.95-external-dependency-blocker-synthesis.md) | After v2.91-v2.94, does the current run still have a defensible in-repo path to |
| v2.96 | [v2.96 - g8 measurement sensitivity targets: precision floor defined](2026-06-20-v2.96-g8-measurement-sensitivity-targets.md) | Given the v2.95 external-packet blocker, what engine-normalized `g_8` |
| v2.97 | [v2.97 - g8 secondary-axis targets: near-degeneracy has a joint route](2026-06-20-v2.97-g8-secondary-axis-targets.md) | v2.96 found that the tightest eligible `g_8` pair requires total uncertainty |
| v2.98 | [v2.98 - g8 joint-packet acceptance gate: executable route, no real pac](2026-06-20-v2.98-g8-joint-packet-acceptance-gate.md) | v2.97 defined joint `g_8 + secondary_axis` targets for the tightest eligible |
| v2.99 | [v2.99 - g8 joint-source discovery queue: next adapter build selected](2026-06-20-v2.99-g8-joint-source-discovery-queue.md) | v2.98 made the joint `g_8 + secondary_axis` gate executable. Instead of |
| v2.100 | [v2.100 - GW secondary-axis adapter blueprint: real constraints, no eng](2026-06-20-v2.100-gw-secondary-axis-adapter-blueprint.md) | v2.99 selected a public-GW reanalysis path as the next build route. Can the |
| v2.101 | [v2.101 - GW alpha engine Jacobian audit: preserve cubic source basis](2026-06-20-v2.101-gw-alpha-engine-jacobian-audit.md) | v2.100 selected the next action: |
| v2.102 | [v2.102 - GW cubic source-native adapter: alpha packet gate is explicit](2026-06-20-v2.102-gw-cubic-source-native-adapter.md) | v2.101 rejected a direct `alpha_bar_1` / `alpha_bar_2` projection into |
| v2.103 | [v2.103 - GW alpha interval surrogate: covariance fixture, not evidence](2026-06-20-v2.103-gw-alpha-interval-surrogate.md) | v2.102 selected alpha-bar likelihood reproduction as the next build target. Can |
| v2.104 | [v2.104 - GW170608 alpha reanalysis manifest: public inputs, missing li](2026-06-20-v2.104-gw170608-alpha-reanalysis-manifest.md) | v2.103 selected the next concrete step: |
| v2.105 | [v2.105 - GW alpha likelihood stub: source-native packet harness](2026-06-20-v2.105-gw-alpha-likelihood-stub.md) | v2.104 selected the next implementation step: |
| v2.106 | [v2.106 - GW public strain connector: URLs connected, bytes not ingeste](2026-06-20-v2.106-gw-public-strain-connector.md) | v2.105 selected the next implementation step: |
| v2.107 | [v2.107 - GW public strain loader: HDF5 bytes verified, residual missin](2026-06-20-v2.107-gw-public-strain-loader.md) | v2.106 selected the next implementation step: |
| v2.108 | [v2.108 - GW strain alpha residual projection: public data, proxy templ](2026-06-20-v2.108-gw-strain-alpha-residual-projection.md) | v2.107 selected the next implementation step: |
| v2.109 | [v2.109 - GW source-backed cubic waveform response: proxy removed, like](2026-06-20-v2.109-gw-source-backed-cubic-waveform-response.md) | v2.108 selected the next implementation step: |
| v2.110 | [v2.110 - GW source-backed strain projection: public data touched, like](2026-06-20-v2.110-gw-source-backed-strain-projection.md) | v2.109 selected the next implementation step: |
| v2.111 | [v2.111 - GW PSD-whitened complex projection: stricter diagnostic, no l](2026-06-20-v2.111-gw-psd-whitened-complex-projection.md) | v2.110 selected the next implementation step: |
| v2.112 | [v2.112 - GW GR inspiral reference projection: physical phase, still no](2026-06-20-v2.112-gw-gr-inspiral-reference-projection.md) | v2.111 selected the next implementation step: |
| v2.113 | [v2.113 - GW LALSuite IMR projection: waveform baseline ready, likeliho](2026-06-20-v2.113-gw-lalsuite-imr-projection.md) | v2.112 selected the next implementation step: |
| v2.114 | [v2.114 - GW LALSuite alpha likelihood grid: fixed parameters only](2026-06-20-v2.114-gw-lalsuite-alpha-likelihood-grid.md) | v2.113 selected the next implementation step: |
| v2.115 | [v2.115 - GW LALSuite marginal alpha likelihood: nuisance grid, not pos](2026-06-20-v2.115-gw-lalsuite-marginal-alpha-likelihood.md) | v2.114 selected the next implementation step: |
| v2.116 | [v2.116 - GW marginal alpha packet export: adapter parses, claim blocke](2026-06-20-v2.116-gw-marginal-alpha-packet-export.md) | v2.115 selected the next implementation step: |
| v2.117 | [v2.117 - GW alpha engine projection packet: identity axis, still noncl](2026-06-20-v2.117-gw-alpha-engine-projection-packet.md) | v2.116 selected the next implementation step: |
| v2.118 | [v2.118 - GW alpha systematics budget gate: two components bounded](2026-06-20-v2.118-gw-alpha-systematics-budget-gate.md) | v2.117 selected the next implementation step: |
| v2.119 | [v2.119 - GW alpha systematics envelope audit: proxies quantified, stil](2026-06-20-v2.119-gw-alpha-systematics-envelope-audit.md) | v2.118 selected the next implementation step: |
| v2.120 | [v2.120 - GW alpha detector calibration bound: one proxy replaced](2026-06-20-v2.120-gw-alpha-detector-calibration-bound.md) | v2.119 selected the next implementation step: |
| v2.121 | [v2.121 - GW alpha prior treatment stress test: cube export required](2026-06-20-v2.121-gw-alpha-prior-treatment-stress-test.md) | v2.120 selected the next implementation step: |
| v2.122 | [v2.122 - GW alpha likelihood cube export: prior blocker made actionabl](2026-06-20-v2.122-gw-alpha-likelihood-cube-export.md) | v2.121 selected the next implementation step: |
| v2.123 | [v2.123 - GW alpha prior reweight sweep: prior sensitivity bounded for ](2026-06-20-v2.123-gw-alpha-prior-reweight-sweep.md) | v2.122 selected the next implementation step: |
| v2.124 | [v2.124 - GW alpha waveform/EFT bounds: components bounded, budget held](2026-06-20-v2.124-gw-alpha-waveform-eft-bound.md) | v2.123 selected the next implementation step: |
| v2.125 | [v2.125 - GW alpha joint likelihood calibration: alpha packet ready, G8](2026-06-20-v2.125-gw-alpha-joint-likelihood-calibration.md) | v2.124 selected the next implementation step: |
| v2.126 | [v2.126 - GW alpha/G8 joint audit: alpha ready, no current G8 component](2026-06-20-v2.126-gw-alpha-g8-joint-component-audit.md) | v2.125 selected the next implementation step: |
| v2.127 | [v2.127 - GW alpha/G8 external sidecar spec: contract defined, not sati](2026-06-20-v2.127-gw-alpha-g8-external-measurement-spec.md) | v2.126 selected the next implementation step: |
| v2.128 | [v2.128 - GW alpha/G8 sidecar gate: executable, no real packet](2026-06-20-v2.128-gw-alpha-g8-sidecar-acceptance-gate.md) | v2.127 selected the next implementation step: |
| v2.129 | [v2.129 - GW alpha/G8 sidecar source scout: current sources scanned, no](2026-06-20-v2.129-gw-alpha-g8-sidecar-source-scout.md) | v2.128 selected the next implementation step: |
| v2.130 | [v2.130 - Bresciani v2 projection audit: R4 gravity formalism, not engi](2026-06-20-v2.130-bresciani-g8-projection-audit.md) | v2.129 selected the next implementation step: |
