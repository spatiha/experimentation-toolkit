"""
Power analysis for proportion-metric experiments.

Answers the two questions every experiment design starts with:
1. How many users do I need to detect a given lift?
2. Given my traffic, what's the smallest lift I can reliably detect (MDE)?
"""

import numpy as np
import matplotlib.pyplot as plt
from statsmodels.stats.power import NormalIndPower
from statsmodels.stats.proportion import proportion_effectsize

ALPHA = 0.05
POWER = 0.80


def required_sample_size(baseline_rate: float, mde_abs: float,
                         alpha: float = ALPHA, power: float = POWER) -> int:
    """Users needed PER VARIANT to detect an absolute lift of `mde_abs`."""
    effect = proportion_effectsize(baseline_rate, baseline_rate + mde_abs)
    n = NormalIndPower().solve_power(effect_size=effect, alpha=alpha,
                                     power=power, ratio=1.0)
    return int(np.ceil(n))


def mde_curve(baseline_rate: float, out_path: str):
    """Plot minimum detectable effect vs. sample size per variant."""
    sizes = np.logspace(3, 5.5, 40).astype(int)
    mdes = []
    solver = NormalIndPower()
    for n in sizes:
        es = solver.solve_power(nobs1=n, alpha=ALPHA, power=POWER, ratio=1.0)
        # invert effect size back to absolute lift via search
        lo, hi = 1e-5, 0.5
        for _ in range(60):
            mid = (lo + hi) / 2
            if proportion_effectsize(baseline_rate, baseline_rate + mid) < es:
                lo = mid
            else:
                hi = mid
        mdes.append(mid * 100)

    fig, ax = plt.subplots(figsize=(8, 5))
    ax.plot(sizes, mdes, lw=2)
    ax.set_xscale("log")
    ax.set_xlabel("Users per variant (log scale)")
    ax.set_ylabel("Minimum detectable lift (percentage points)")
    ax.set_title(f"MDE curve — baseline rate {baseline_rate:.0%}, "
                 f"α={ALPHA}, power={POWER:.0%}")
    ax.grid(alpha=0.3)
    fig.tight_layout()
    fig.savefig(out_path, dpi=150)
    print(f"saved {out_path}")


if __name__ == "__main__":
    baseline = 0.448  # Cookie Cats 1-day retention baseline
    for lift in [0.005, 0.01, 0.02]:
        n = required_sample_size(baseline, lift)
        print(f"To detect a +{lift*100:.1f}pp lift on a {baseline:.1%} baseline: "
              f"{n:,} users per variant")
    mde_curve(baseline, "figures/mde_curve.png")
