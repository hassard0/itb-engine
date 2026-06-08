# ITB Engine — Research Report v1.44 (2026-06-08)

**The realism → generative → decisive-experiment program.** This report
synthesizes 22 cycles (v1.23–v1.44) run on the Vulcan compute server with the
local Gemma-4 "Dr. M." as physics partner. It supersedes the v1.20 report's
framing.

The arc, in one sentence: *we stress-tested the engine's headline claims against
its own toy-prefactor uncertainty (deleting the artifacts), used the surviving
structure generatively to find new consistent theories and the experiments that
would reveal them, and connected the whole thing to a concrete near-term
experimental program rooted in the cosmological-constant scale.*

---

## Arc I — The realism audit (v1.23–26): what survives the toy prefactors

Every constraint uses O(1) placeholder coefficients. We Monte-Carlo'd the six
most-uncertain prefactors over factor-of-2 ranges (300k draws/condition) and the
framework coefficients over literature-motivated ranges, and asked which
conclusions survive.

- **Artifacts removed.** The Repulsive Force Conjecture exclusion was a *miscast
  encoding* (it multiplied two matter coefficients against a graviton one); fixed
  via `RepulsiveForceConjecture(form="convex_hull")`. The "LQG fails BNOSSW
  monogamy" headline is *proxy-form fragile* (harmonic 44% → geometric 5%). The
  forward-positivity exclusion of LQG (v1.24) was itself an artifact of the
  engine's inflated LQG g_R3 (v1.25).
- **What is robust.** (1) A fully consistent theory exists (intersection
  non-empty in 51–78% of prefactor space). (2) **LQG-induced is robustly
  disfavoured** — viable in only ~2% of the joint coefficient×prefactor space,
  ~10× below every other framework, and *redundantly* (no single constraint
  carries the exclusion, so no single artifact can rescue it; its real
  liabilities are parity violation and complexity-bound tension). (3) String,
  AS, and CDT cannot be ranked at toy precision.

## Arc II — Generative discovery (v1.27–34): new consistent theories

Used the engine in reverse — searching for consistent theories *unlike* any
catalogued framework.

- **Three engine-discovered theories**, now first-class encoders
  (`DiscoveredNovel`, `DiscoveredParityViolating`, `DiscoveredHighG8`): a robust
  weakly-coupled low-g_8 branch (feasible 76%), a robust high-g_8 branch (63%),
  and a fragile parity-violating branch (18%).
- **The consistent frontier is parity-violating.** All 79 extreme consistent
  theories violate parity; the catalogued frameworks occupy a parity-conserving
  interior slice. A consistent parity-violating gravity exists — *the consistent
  cousin of LQG* — provided it suppresses its cubic curvature (g_R2/g_R3 ≳ 3,
  the needle LQG fails); parity is capped at ≈0.14, set by anomaly inflow.
- **Freedom map.** The matter coupling g_8 is the loosest direction; the cubic
  gravitational parity coupling g_R3_parity is the most pinned (a robust
  prediction). The feasible region is a single connected sliver (not the "31
  islands" a boundary artifact suggested).

## Arc III — Observability (v1.35–36): what can be measured

- **Sloppiness.** The observable set is deeply sloppy (Fisher condition number
  ~10⁵). The loose direction g_8 is observationally degenerate from a forward
  amplitude — *but* the **spin-4 partial wave isolates g_8** (only the
  dimension-8 operator reaches ℓ=4), dropping the matter-sector condition number
  from ~12 000 to 15. Angular data, not energy reach, breaks the degeneracy.
- **Parity is the stiff, pinned, top-priority signal**, and (v1.37) its ceiling
  ≈ √(ρ·g_4·g_R2) is set by the anomaly coefficient ρ — so a gravitational
  parity measurement would *pin ρ*, the engine's most uncertain swampland number.

## Arc IV — The decisive experiment (v1.39–44)

- **GIE (Bose / Marletto–Vedral)** answers the foundational question — *is
  gravity quantum?* — via the entanglement two masses acquire through their
  mutual gravity (LOCC theorem). Phase ~0.09–1 rad at µg masses; a null falsifies
  the entire feasible region.
- **The engine's g_R2 is a short-range-gravity observable.** The R² (Stelle)
  term gives a Yukawa correction of range λ_Y = √(6 g_R2)·ℏc/Λ. Dr. M.
  independently named short-range gravity (not GIE) the decisive *discriminating*
  experiment, because the Yukawa directly fixes g_R2 and Λ.
- **Spec sheet (v1.41).** At a dark-energy-scale cutoff the candidate theories
  predict Yukawa ranges 74–127 µm; at the optimal probe distance **r\* = 93 µm**
  the deviations are 10–16 % of Newton, and **current torsion balances (~1 %
  force) resolve 14/21 framework pairs; 0.1 % resolves all.**
- **Combined program (v1.43).** Matter scattering (with partial-wave resolution)
  + sub-mm gravity + GW birefringence resolves **20/21 framework pairs**. Clean
  division of labour: matter amplitude = workhorse (15 pairs); birefringence =
  the irreplaceable parity probe (4 pairs); sub-mm gravity = the tiebreaker. The
  lone holdout is **string ≈ CDT** — distinct but near-degenerate (their
  representative coefficients overlap within ±40 % uncertainty; S/N 2.6), needing
  pinned coefficients plus sub-percent short-range gravity.
- **Why the dark-energy cutoff (v1.44).** It is consistency-*motivated*, not
  assumed: it is the unique scale that simultaneously dissolves the
  cosmological-constant fine-tuning (Λ⁴ ≈ ρ_Λ), keeps the Wilson coefficients
  inside the EFT-validity box (the Planckian alternative needs g_R2 ~ 10¹²¹), and
  lands the signal in the sub-mm gravity window. The dark-energy-length ↔ sub-mm
  coincidence becomes structural.

---

## The bottom line, and the program it implies

The engine now produces an **end-to-end map**: consistency constraints →
candidate theories (including novel ones) → observable signatures → the decisive
experiments → required apparatus precision → which experiment resolves which
theory. It does not *prove* which theory is correct — only data can — but it
turns "solve quantum gravity" into a concrete, costed program:

1. **Gravitational entanglement** → *is gravity quantum?*
2. **Sub-mm gravity at ~93 µm to ≲1 % force** → *which completion?* (and, via
   v1.44, a test of whether the gravitational cutoff is the dark-energy scale —
   i.e. whether the CC fine-tuning is real).
3. **GW birefringence to |g_R2_parity| ~ 0.01** → the parity sector and the
   swampland coefficient ρ.

A 1/r deviation at 70–130 µm of order 10 % would reveal the gravitational cutoff
scale *and* pick out the UV completion — the single most decisive measurement the
engine points to.

## Honest limitations

Toy-prefactor precision throughout; the gravitational-channel numbers assume the
dark-energy-scale cutoff (a consistency-favoured hypothesis, not a proof). The
robust, assumption-light content is structural: the audit verdicts (Arc I), the
parity-violating frontier and freedom map (Arc II), the spin-4/g_8 and parity
observability facts (Arc III), and the three-way CC ⇔ EFT-box ⇔ sub-mm link
(Arc IV). The single highest-value external input remains literature-pinned
coefficients (LQG parity/g_R3, AS g_6/g_8), deliberately not fabricated.

## Reproducibility

All harnesses under `experiments/`, all artifacts under `experiments/results/`,
one dated note per cycle under `docs/results/2026-06-08-v1.2x..v1.44-*.md`.
Engine changes: corrected RFC form, forward-positivity & matter-s³ constraints,
three discovered-theory encoders, gravitational observables. **374 tests pass.**
