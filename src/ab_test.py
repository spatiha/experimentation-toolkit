"""
A/B test evaluation on the Cookie Cats mobile game experiment.

Real experiment (90,189 players): the first progression gate was moved
from level 30 (control) to level 40 (treatment). Metrics: 1-day and
7-day retention.

Methods: two-proportion z-test, confidence interval on the difference,
and a bootstrap check of the 7-day retention result.
"""

import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
from statsmodels.stats.proportion import proportions_ztest, confint_proportions_2indep

RNG = np.random.default_rng(42)


def analyze_metric(df: pd.DataFrame, metric: str) -> dict:
    g = df.groupby("version")[metric].agg(["sum", "count", "mean"])
    ctrl, treat = g.loc["gate_30"], g.loc["gate_40"]

    stat, pval = proportions_ztest(
        [treat["sum"], ctrl["sum"]], [treat["count"], ctrl["count"]]
    )
    ci_lo, ci_hi = confint_proportions_2indep(
        treat["sum"], treat["count"], ctrl["sum"], ctrl["count"],
        method="wald",
    )
    return {
        "metric": metric,
        "control_rate": ctrl["mean"],
        "treatment_rate": treat["mean"],
        "abs_lift_pp": (treat["mean"] - ctrl["mean"]) * 100,
        "p_value": pval,
        "ci_lo_pp": ci_lo * 100,
        "ci_hi_pp": ci_hi * 100,
    }


def bootstrap_diff(df: pd.DataFrame, metric: str, n_boot: int = 5000) -> np.ndarray:
    ctrl = df.loc[df.version == "gate_30", metric].to_numpy(dtype=float)
    treat = df.loc[df.version == "gate_40", metric].to_numpy(dtype=float)
    diffs = np.empty(n_boot)
    for i in range(n_boot):
        diffs[i] = (RNG.choice(treat, treat.size).mean()
                    - RNG.choice(ctrl, ctrl.size).mean())
    return diffs * 100


def main():
    df = pd.read_csv("data/cookie_cats.csv")
    # Guardrail: remove one extreme-outlier bot account (49,854 game rounds)
    df = df[df.sum_gamerounds < df.sum_gamerounds.quantile(0.9999)]

    results = [analyze_metric(df, m) for m in ["retention_1", "retention_7"]]
    res_df = pd.DataFrame(results)
    print(res_df.to_string(index=False))
    res_df.to_csv("figures/ab_results.csv", index=False)

    # Figure: bootstrap distribution of 7-day retention difference
    diffs = bootstrap_diff(df, "retention_7")
    fig, ax = plt.subplots(figsize=(8, 5))
    ax.hist(diffs, bins=60, alpha=0.8)
    ax.axvline(0, color="black", lw=1.5, ls="--", label="No effect")
    ax.axvline(diffs.mean(), color="crimson", lw=2,
               label=f"Observed: {diffs.mean():+.2f}pp")
    ax.set_xlabel("Treatment − Control, 7-day retention (pp)")
    ax.set_ylabel("Bootstrap samples")
    ax.set_title("Moving the gate to level 40 HURT 7-day retention\n"
                 f"P(diff < 0) = {(diffs < 0).mean():.1%} of bootstrap samples")
    ax.legend()
    fig.tight_layout()
    fig.savefig("figures/bootstrap_retention7.png", dpi=150)
    print("saved figures/bootstrap_retention7.png")


if __name__ == "__main__":
    main()
