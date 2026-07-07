"""
CUPED (Controlled-experiment Using Pre-Experiment Data).

CUPED uses each user's pre-experiment metric as a covariate to strip
predictable variance out of the experiment metric, letting you detect
the same effect with far fewer users (or detect smaller effects with
the same traffic).

Because CUPED requires a pre-period, this module uses a simulation with
a KNOWN true effect — which also validates that the estimator is unbiased.

    Y_adj = Y − θ·(X − mean(X)),   θ = cov(X, Y) / var(X)
"""

import numpy as np
import matplotlib.pyplot as plt

RNG = np.random.default_rng(7)

N_USERS = 20_000
TRUE_EFFECT = 2.0          # true lift in post-period spend
PRE_POST_CORR = 0.7        # correlation between pre and post metric
N_SIMS = 2_000


def simulate_once():
    pre = RNG.gamma(shape=2.0, scale=25.0, size=N_USERS)          # pre-period spend
    noise = RNG.normal(0, np.std(pre) * np.sqrt(1 / PRE_POST_CORR**2 - 1),
                       N_USERS)
    post = pre + noise                                            # corr ≈ PRE_POST_CORR
    treat = RNG.random(N_USERS) < 0.5
    post = post + TRUE_EFFECT * treat

    # Naive estimate
    naive = post[treat].mean() - post[~treat].mean()

    # CUPED adjustment
    theta = np.cov(pre, post)[0, 1] / np.var(pre)
    y_adj = post - theta * (pre - pre.mean())
    cuped = y_adj[treat].mean() - y_adj[~treat].mean()
    return naive, cuped


def main():
    est = np.array([simulate_once() for _ in range(N_SIMS)])
    naive, cuped = est[:, 0], est[:, 1]

    var_reduction = 1 - cuped.var() / naive.var()
    print(f"True effect:            {TRUE_EFFECT:.2f}")
    print(f"Naive estimator:        mean {naive.mean():.2f}, SD {naive.std():.3f}")
    print(f"CUPED estimator:        mean {cuped.mean():.2f}, SD {cuped.std():.3f}")
    print(f"Variance reduction:     {var_reduction:.1%}")
    print(f"Equivalent sample-size saving: {var_reduction:.1%} fewer users "
          f"for the same power")

    fig, ax = plt.subplots(figsize=(8, 5))
    bins = np.linspace(min(naive.min(), cuped.min()),
                       max(naive.max(), cuped.max()), 60)
    ax.hist(naive, bins=bins, alpha=0.55, label=f"Naive (SD={naive.std():.2f})")
    ax.hist(cuped, bins=bins, alpha=0.55, label=f"CUPED (SD={cuped.std():.2f})")
    ax.axvline(TRUE_EFFECT, color="black", ls="--", lw=1.5, label="True effect")
    ax.set_xlabel("Estimated treatment effect")
    ax.set_ylabel("Simulations")
    ax.set_title(f"CUPED cuts estimator variance by {var_reduction:.0%} "
                 f"(pre/post corr = {PRE_POST_CORR})")
    ax.legend()
    fig.tight_layout()
    fig.savefig("figures/cuped_variance_reduction.png", dpi=150)
    print("saved figures/cuped_variance_reduction.png")


if __name__ == "__main__":
    main()
