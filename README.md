# Experimentation Toolkit: A/B Testing & Causal Inference in Practice

An end-to-end walkthrough of the experimentation lifecycle — from designing a test to measuring impact when randomization isn't possible. Built on **real experiment data** (90k-user Cookie Cats mobile game A/B test) and **real policy data** (California's 2011 organ-donor registration change), plus a simulation with known ground truth to validate variance-reduction methods.

The question this repo answers: **"How do you know an initiative actually worked?"**

## What's inside

| Module | Question it answers | Method |
|---|---|---|
| `src/power_analysis.py` | How many users do I need before launching? | Power analysis, MDE curves |
| `src/ab_test.py` | Did the change move the metric? | Two-proportion z-test, CIs, bootstrap |
| `src/cuped.py` | Can I get answers with less traffic? | CUPED variance reduction |
| `src/did.py` | What if I can't randomize? | Difference-in-differences (TWFE, clustered SEs) |

## Key results

### 1. Design first: power analysis
On a 44.8% baseline retention rate (α=0.05, power=80%), detecting a **+1pp lift needs ~39k users per variant**; a +0.5pp lift needs ~155k. Half of good experimentation is refusing to run underpowered tests.

![MDE curve](figures/mde_curve.png)

### 2. The A/B test: moving the gate hurt retention
Cookie Cats moved its first progression gate from level 30 to level 40, hypothesizing that delayed friction would improve retention. The data said otherwise:

| Metric | Control | Treatment | Lift | 95% CI | p-value |
|---|---|---|---|---|---|
| 1-day retention | 44.81% | 44.22% | −0.59pp | [−1.24, +0.06] | 0.073 |
| 7-day retention | 19.01% | 18.19% | **−0.82pp** | [−1.33, −0.31] | **0.002** |

The 1-day metric alone looks like a shrug — the 7-day metric shows a real, significant loss. A bootstrap confirms it: ~100% of resamples show a negative effect. **Business call: don't ship.** (Also note the guardrail step: one bot account with ~50k game rounds is excluded before analysis.)

![Bootstrap distribution](figures/bootstrap_retention7.png)

### 3. CUPED: same power, half the traffic
Using each user's pre-experiment behavior as a covariate cuts estimator variance by **~52%** (at pre/post correlation 0.7) — equivalent to needing half the sample for the same power. The simulation uses a known true effect, verifying the estimator recovers it without bias.

![CUPED](figures/cuped_variance_reduction.png)

### 4. When you can't randomize: difference-in-differences
In July 2011 California changed its driver's-license organ-donor question from opt-in to "active choice." Comparing California's before/after shift against unaffected states (two-way fixed effects, state-clustered SEs) shows the change **reduced sign-up rates by 1.6pp (p < 0.001)** — a well-intentioned nudge that backfired. Pre-period trends between groups are parallel, supporting the identifying assumption.

![DiD](figures/did_organ_donations.png)

## Why these methods matter in industry

- **Power analysis** prevents the most common experimentation failure: calling a "no effect" on a test that never had a chance to detect one.
- **Multiple-horizon metrics** (1-day vs 7-day retention) catch effects that short-window readouts miss.
- **CUPED** is standard at scale (Microsoft, Netflix, Airbnb) because traffic is the binding constraint on experiment velocity.
- **DiD** extends measurement to pricing changes, policy rollouts, and market-level launches where an A/B test is impossible.

## Run it

```bash
pip install -r requirements.txt
python src/power_analysis.py
python src/ab_test.py
python src/cuped.py
python src/did.py
```

Figures and result tables are written to `figures/`.

## Data sources

- **Cookie Cats A/B test** — 90,189 players, published by Tactile Entertainment (via DataCamp).
- **Organ donations DiD** — Kessler & Roth (2014), distributed in the [`causaldata`](https://pypi.org/project/causaldata/) package.
- **CUPED** — simulated with known ground truth (by design, since CUPED requires pre-experiment data).
