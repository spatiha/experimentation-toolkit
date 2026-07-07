"""
Difference-in-Differences (DiD) — when you CAN'T randomize.

Real policy data (Kessler & Roth 2014, via the `causaldata` package):
in July 2011, California switched its driver's-license organ-donor
question from opt-in to "active choice". Other states didn't.
Did the change reduce donor sign-up rates?

DiD compares California's before/after change against the before/after
change in unaffected states, differencing out both state-level baselines
and common time shocks. Estimated with two-way fixed effects and
cluster-robust standard errors.
"""

import pandas as pd
import matplotlib.pyplot as plt
import statsmodels.formula.api as smf
from causaldata import organ_donations


def main():
    df = organ_donations.load_pandas().data
    df["treated"] = ((df.State == "California")
                     & df.Quarter.isin(["Q32011", "Q42011"])).astype(int)
    df["is_ca"] = (df.State == "California").astype(int)

    # Two-way fixed effects DiD, SEs clustered by state
    model = smf.ols("Rate ~ treated + C(State) + C(Quarter)", data=df).fit(
        cov_type="cluster", cov_kwds={"groups": df["State"]}
    )
    att = model.params["treated"]
    se = model.bse["treated"]
    print(f"DiD estimate (ATT): {att:+.4f}  (SE {se:.4f}, "
          f"p={model.pvalues['treated']:.4f})")
    print("Interpretation: active choice REDUCED California's donor "
          f"sign-up rate by {abs(att)*100:.1f}pp.")

    # Figure: California vs. control-state average over time
    order = ["Q42010", "Q12011", "Q22011", "Q32011", "Q42011"]
    trend = (df.assign(grp=df.is_ca.map({1: "California", 0: "Other states (avg)"}))
               .groupby(["grp", "Quarter"])["Rate"].mean()
               .unstack(level=0).reindex(order))
    fig, ax = plt.subplots(figsize=(8, 5))
    trend.plot(ax=ax, marker="o", lw=2)
    ax.axvline(2.5, color="black", ls="--", lw=1.2)
    ax.text(2.55, ax.get_ylim()[1]*0.98, "Policy change\n(Jul 2011)",
            va="top", fontsize=9)
    ax.set_ylabel("Organ donor sign-up rate")
    ax.set_xlabel("Quarter")
    ax.set_title(f"Difference-in-Differences: ATT = {att:+.3f} "
                 f"({abs(att)*100:.1f}pp drop)")
    ax.grid(alpha=0.3)
    fig.tight_layout()
    fig.savefig("figures/did_organ_donations.png", dpi=150)
    print("saved figures/did_organ_donations.png")


if __name__ == "__main__":
    main()
