# ITB Engine - Research Results Index

Auto-generated front door to the full research program (125 notes). Regenerate with `python tools/build_index.py`.

## Foundations (v0.x - v1.22): the original engine

| ver | note | one line |
|---|---|---|
| - | [Cross-scenario synthesis](2026-05-08-cross-scenario-synthesis.md) | Per-framework feasibility across all scenarios. |
| v0.8 | [ITB Engine — Full Battery: v0.8 baseline (8 constraints, 4 frameworks)](2026-05-08-v0.8-baseline-report.md) | _Generated: 2026-05-08T04:15:29+00:00_ |
| v0.9 | [Honest Synthesis: What the ITB Engine Has and Has Not Shown](2026-05-08-honest-synthesis.md) | From building it: |
| v1.0 | [v1.0 Findings — what changed when we replaced toy bounds with publicat](2026-05-08-v1.0-findings.md) | Adding `g_6² ≤ g_4·g_8` — the chained Cauchy-Schwarz between adjacent forward-dispersion coefficients that the Caron-Huot et al program uses — produced **8 cell |
| v1.0 | [ITB Engine — Full Battery: v1.0 — publication-grade constraints (dispe](2026-05-08-v1.0-publication-grade-report.md) | _Generated: 2026-05-08T11:32:51+00:00_ |
| v1.1 | [ITB Engine — Full Battery: v1.1 — adds BNOSSW MMI + holographic subadd](2026-05-08-v1.1-bnossw-report.md) | _Generated: 2026-05-08T11:40:31+00:00_ |
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
| v1.2 | [ITB Engine — Full Battery: v1.2 — adds cubic curvature constraints (g_](2026-05-08-v1.2-cubic-curvature-report.md) | _Generated: 2026-05-08T11:49:50+00:00_ |
| v1.20 | [The Information-Theoretic Bootstrap Engine: A Toy Computational Pipeli](2026-05-08-RESEARCH-REPORT-v1.20.md) | We describe the Information-Theoretic Bootstrap (ITB) Engine, a localhost Python platform that imposes a curated set of consistency conditions on a parameterize |
| v1.21 | [v1.21 — Local LLM Backend Integrated (Gemma 4 / Pluto)](2026-05-09-v1.21-local-llm-integration.md) | Dr. M. (the research-agent persona) now has two backends: |
| v1.22 | [v1.22 — Gemma 4 native tool calling on Pluto](2026-05-09-v1.22-gemma-native-tools.md) | The local-LLM research-agent backend now uses **native OpenAI-compatible |
| v1.3 | [Experimental priority ranking](2026-05-08-v1.3-experimental-priorities.md) | Baseline allowed cells (without any experiment): 3 |
| v1.4 | [Experimental priority ranking](2026-05-08-v1.4-experimental-priorities.md) | Baseline allowed cells (without any experiment): 99 |
| v1.4 | [ITB Engine — Full Battery: v1.4 — parity-violation sector active (g_R2](2026-05-08-v1.4-parity-violation-report.md) | _Generated: 2026-05-08T12:04:49+00:00_ |
| v1.5 | [First-disagreement observable ranking](2026-05-08-v1.5-first-disagreement.md) | Each row is a candidate-framework pair × observable. S/N gives the signal-to-noise ratio: how many sigmas of measurement separate the two frameworks at that obs |
| v1.6 | [ITB Engine — Full Battery: v1.6 — anomaly-flow active (parity slice fi](2026-05-08-v1.6-anomaly-flow-report.md) | _Generated: 2026-05-08T12:18:30+00:00_ |
| v1.8 | [v1.8 — Honest Synthesis After 18 Iterations](2026-05-08-v1.8-honest-synthesis.md) | What it is: |
| v1.8 | [v1.8 — The Engine's Sharpest Answer](2026-05-08-v1.8-intersection-search.md) | Constraint count: **24** |
| v1.9 | [v1.9 — Research-agent session log (Dr. M.)](2026-05-08-v1.9-research-agent-session.md) | agent shipped this iteration). Live LLM loop requires `ANTHROPIC_API_KEY`. |

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
