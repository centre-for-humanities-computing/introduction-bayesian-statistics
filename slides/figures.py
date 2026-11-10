"""Generate every figure, equation image and QR code used in the slides.

Run from the repository root:  uv run python slides/figures.py

Figures are drawn at the size they occupy on the slide (inches), so font sizes
in the images match font sizes on the slide. Key numbers quoted on the slides
are written to slides/figures/numbers.json.
"""

import json
import sys
from pathlib import Path

import matplotlib

matplotlib.use("Agg")
import matplotlib.pyplot as plt  # noqa: E402
import numpy as np  # noqa: E402
import pandas as pd  # noqa: E402
import pymc as pm  # noqa: E402
import qrcode  # noqa: E402
import statsmodels.formula.api as smf  # noqa: E402
from scipy import stats  # noqa: E402

sys.path.insert(0, str(Path(__file__).parent))
from style import (  # noqa: E402
    BLUE,
    BLUE_DARK,
    GREY,
    GREY_BAR,
    GREY_DARK,
    GREY_LIGHT,
    GREY_MID,
    ROSE,
    ROSE_DARK,
    ROSE_LIGHT,
    SAGE,
    SAGE_DARK,
    use_style,
)

ROOT = Path(__file__).resolve().parents[1]
OUT = ROOT / "slides" / "figures"
OUT.mkdir(parents=True, exist_ok=True)

REPO = "centre-for-humanities-computing/introduction-bayesian-statistics"
COLAB = f"https://colab.research.google.com/github/{REPO}/blob/master/notebooks"
QUIZ_URL = "https://centre-for-humanities-computing.github.io/introduction-bayesian-statistics/quiz/"

# Figure sizes (inches) matching the slide layouts in build_slides.py
WIDE = (12.2, 4.9)
RIGHT = (7.4, 5.0)


TRUE = dict(intercept=0.5, slope=0.8, sigma=1.0)
XLAB = "Text length (hundreds of words)"
YLAB = "Reading time (minutes)"
NUMBERS: dict = {}


# ----------------------------------------------------------------------------
# Data and models (identical to the notebooks)
# ----------------------------------------------------------------------------
def simulate_reading(n=40, intercept=0.5, slope=0.8, sigma=1.0, seed=226):
    """Reading time (minutes) as a function of text length (hundreds of words)."""
    rng = np.random.default_rng(seed)
    words = rng.uniform(1, 12, size=n).round(1)
    time = intercept + slope * words + rng.normal(0, sigma, size=n)
    return pd.DataFrame({"words": words, "time": time.round(2)})


def repeat_study(slope=0.8, seed=None):
    """Repeat our study: the same 40 texts, new reading times.

    The standard error that statsmodels reports is about this kind of repetition
    (text lengths fixed, new noise), so the simulated spread matches it.
    """
    words = simulate_reading()["words"]
    rng = np.random.default_rng(seed)
    time = TRUE["intercept"] + slope * words + rng.normal(0, TRUE["sigma"], len(words))
    return pd.DataFrame({"words": words, "time": time.round(2)})


def fit_reading_bayes(df, slope_mu=0.0, slope_sigma=2.0, seed=1):
    with pm.Model():
        intercept = pm.Normal("intercept", mu=0, sigma=5)
        slope = pm.Normal("slope", mu=slope_mu, sigma=slope_sigma)
        sigma = pm.HalfNormal("sigma", sigma=2)
        mu = intercept + slope * df["words"].values
        pm.Normal("time", mu=mu, sigma=sigma, observed=df["time"].values)
        return pm.sample(1000, tune=1000, chains=2, random_seed=seed, progressbar=False)


def fit_kid_bayes(kid, seed=1):
    with pm.Model():
        intercept = pm.Normal("intercept", mu=80, sigma=20)
        b_hs = pm.Normal("b_hs", mu=0, sigma=10)
        b_iq = pm.Normal("b_iq", mu=0, sigma=1)
        sigma = pm.HalfNormal("sigma", sigma=20)
        mu = intercept + b_hs * kid["mom_hs"].values + b_iq * kid["mom_iq_c"].values
        pm.Normal("kid_score", mu=mu, sigma=sigma, observed=kid["kid_score"].values)
        return pm.sample(1000, tune=1000, chains=2, random_seed=seed, progressbar=False)


def draws(idata, name):
    """All posterior draws of one parameter as a flat numpy array."""
    return np.asarray(idata.posterior[name].values).ravel()


def interval(x, prob=0.95):
    lo = (1 - prob) / 2
    return np.quantile(x, [lo, 1 - lo])


def ols_ci(fit, name):
    return fit.conf_int().loc[name].to_numpy()


def r(x, k=2):
    return float(np.round(x, k))


# ----------------------------------------------------------------------------
# Helpers
# ----------------------------------------------------------------------------
def minus(s):
    """Typographic minus signs in annotation text."""
    return s.replace("-", "−")


def save(fig, name):
    fig.savefig(OUT / f"{name}.png", dpi=200)
    plt.close(fig)
    print("  wrote", name)


def reading_axes(ax, xlim=(0, 12.5), ylim=(0, 12)):
    ax.set_xlim(*xlim)
    ax.set_ylim(*ylim)
    ax.set_xlabel(XLAB)
    ax.set_ylabel(YLAB)


def scatter_data(ax, df, **kw):
    style = dict(s=42, color=GREY, alpha=0.85, zorder=3)
    style.update(kw)
    ax.scatter(df["words"], df["time"], **style)


def sideways_bell(ax, x0, mu, sigma, width=1.6, color=GREY_LIGHT, alpha=0.55):
    y = np.linspace(mu - 3.2 * sigma, mu + 3.2 * sigma, 200)
    d = stats.norm.pdf(y, mu, sigma)
    d = d / d.max() * width
    ax.fill_betweenx(y, x0, x0 + d, color=color, alpha=alpha, lw=0, zorder=1)
    ax.plot(x0 + d, y, color=color, lw=1.2, alpha=0.9, zorder=1)
    ax.plot([x0, x0], [y[0], y[-1]], color=color, lw=1.0, zorder=1)


# ----------------------------------------------------------------------------
# Title motif
# ----------------------------------------------------------------------------
def fig_title_motif():
    rng = np.random.default_rng(3)
    x = rng.uniform(0, 10, 28)
    y = 1 + 0.6 * x + rng.normal(0, 0.9, 28)
    fig, ax = plt.subplots(figsize=(4.6, 3.4))
    xs = np.array([-0.5, 10.5])
    for _ in range(40):
        a = rng.normal(1, 0.35)
        b = rng.normal(0.6, 0.05)
        ax.plot(xs, a + b * xs, color=ROSE, alpha=0.12, lw=2)
    ax.plot(xs, 1 + 0.6 * xs, color=BLUE, lw=4)
    ax.scatter(x, y, s=60, color=GREY, alpha=0.9, zorder=3)
    ax.axis("off")
    fig.subplots_adjust(0, 0, 1, 1)
    save(fig, "title_motif")


# ----------------------------------------------------------------------------
# Block 1 - drawing a line
# ----------------------------------------------------------------------------
def fig_b1(df, fit):
    a_hat, b_hat = fit.params["Intercept"], fit.params["words"]
    xs = np.array([0, 12.5])

    # 1. scatter
    fig, ax = plt.subplots(figsize=RIGHT)
    scatter_data(ax, df)
    reading_axes(ax)
    fig.tight_layout()
    save(fig, "b1_scatter")

    # 2. anatomy of a line
    a, b = TRUE["intercept"], TRUE["slope"]
    fig, ax = plt.subplots(figsize=RIGHT)
    scatter_data(ax, df, alpha=0.18)
    ax.plot(xs, a + b * xs, color=GREY_DARK, lw=3)
    ax.scatter([0], [a], s=120, color=ROSE_DARK, zorder=5, clip_on=False)
    ax.annotate(
        "intercept a = 0.5\npredicted time for a\ntext of length 0",
        xy=(0, a),
        xytext=(0.6, 4.6),
        color=ROSE_DARK,
        fontsize=14,
        arrowprops=dict(arrowstyle="-|>", color=ROSE_DARK, lw=1.5),
    )
    x0, x1 = 6, 8
    ax.plot([x0, x1], [a + b * x0] * 2, color=BLUE_DARK, lw=2.5)
    ax.plot([x1, x1], [a + b * x0, a + b * x1], color=BLUE_DARK, lw=2.5)
    ax.text(
        (x0 + x1) / 2,
        a + b * x0 - 0.6,
        "+2 (200 words)",
        ha="center",
        va="top",
        color=BLUE_DARK,
        fontsize=14,
    )
    ax.text(
        x1 + 0.25,
        a + b * (x0 + x1) / 2,
        "+1.6 min",
        va="center",
        color=BLUE_DARK,
        fontsize=14,
    )
    ax.text(
        8.9, 3.0, "slope b = 0.8\nminutes per 100 words", color=BLUE_DARK, fontsize=14
    )
    reading_axes(ax)
    fig.tight_layout()
    save(fig, "b1_anatomy")

    # 3. error term and sigma
    fig, ax = plt.subplots(figsize=RIGHT)
    ax.plot(xs, a + b * xs, color=GREY_DARK, lw=2.5, zorder=2)
    for x0 in (2.5, 6.5, 10.5):
        sideways_bell(ax, x0, a + b * x0, TRUE["sigma"], width=1.5, color=SAGE)
    scatter_data(ax, df)
    ax.annotate(
        "",
        xy=(6.3, a + b * 6.5 + 1),
        xytext=(6.3, a + b * 6.5),
        arrowprops=dict(arrowstyle="<->", color=SAGE_DARK, lw=2.5),
        zorder=5,
    )
    ax.annotate(
        "σ: typical distance\nof a point from the line",
        xy=(6.2, a + b * 6.5 + 0.5),
        xytext=(0.6, 9.6),
        color=SAGE_DARK,
        fontsize=14,
        zorder=5,
        arrowprops=dict(arrowstyle="-|>", color=SAGE_DARK, lw=1.5),
        bbox=dict(boxstyle="round,pad=0.3", fc="white", ec="none", alpha=0.9),
    )
    reading_axes(ax)
    fig.tight_layout()
    save(fig, "b1_error")

    # 4. residuals
    pred = a_hat + b_hat * df["words"]
    fig, ax = plt.subplots(figsize=RIGHT)
    ax.vlines(df["words"], pred, df["time"], color=GREY_MID, lw=1.5, zorder=2)
    ax.plot(xs, a_hat + b_hat * xs, color=BLUE, lw=3, zorder=2)
    scatter_data(ax, df)
    i = int(np.argmax(df["time"] - pred))
    xi, yi, pi = df["words"][i], df["time"][i], pred[i]
    ax.vlines(xi, pi, yi, color=ROSE_DARK, lw=3, zorder=4)
    ax.annotate(
        f"residual = observed − predicted\n= {yi:.2f} − {pi:.2f} = {yi - pi:+.2f} min",
        xy=(xi, (yi + pi) / 2),
        xytext=(0.6, 10.2),
        color=ROSE_DARK,
        fontsize=14,
        arrowprops=dict(arrowstyle="-|>", color=ROSE_DARK, lw=1.5),
    )
    reading_axes(ax)
    fig.tight_layout()
    save(fig, "b1_residuals")

    # 5. least squares: squares on residuals
    guess = (2.8, 0.4)
    fig, axes = plt.subplots(1, 2, figsize=WIDE)
    for ax, (aa, bb), title, col, fill in [
        (axes[0], guess, "A poor guess", GREY_DARK, GREY_LIGHT),
        (axes[1], (a_hat, b_hat), "The least-squares line", BLUE_DARK, BLUE),
    ]:
        p = aa + bb * df["words"]
        res = df["time"] - p
        for x, pp, rr in zip(df["words"], p, res):
            ax.add_patch(
                plt.Rectangle(
                    (x, min(pp, pp + rr)),
                    abs(rr),
                    abs(rr),
                    facecolor=fill,
                    edgecolor="none",
                    alpha=0.35,
                    zorder=1,
                )
            )
        ax.plot(xs, aa + bb * xs, color=col, lw=3, zorder=2)
        scatter_data(ax, df, s=30)
        rss = float((res**2).sum())
        ax.set_title(f"{title}:  RSS = {rss:.1f}", color=col)
        ax.set_aspect("equal")
        reading_axes(ax, xlim=(0, 13.5), ylim=(0, 12))
        NUMBERS.setdefault("rss", {})[title] = r(rss, 1)
    fig.tight_layout()
    save(fig, "b1_least_squares")

    # 6. maximum likelihood: bell curves around two candidate lines
    fig, axes = plt.subplots(1, 2, figsize=WIDE)
    for ax, (aa, bb), title, col in [
        (axes[0], guess, "A poor guess", GREY_DARK),
        (axes[1], (a_hat, b_hat), "Maximum likelihood line", BLUE_DARK),
    ]:
        p = aa + bb * df["words"]
        s_hat = np.sqrt(((df["time"] - p) ** 2).mean())
        loglik = stats.norm.logpdf(df["time"], p, s_hat).sum()
        for x0 in (2, 5, 8, 11):
            sideways_bell(
                ax,
                x0,
                aa + bb * x0,
                s_hat,
                width=1.3,
                color=BLUE if col == BLUE_DARK else GREY_MID,
            )
        ax.plot(xs, aa + bb * xs, color=col, lw=3, zorder=2)
        scatter_data(ax, df, s=30)
        ax.set_title(minus(f"{title}:  log-likelihood = {loglik:.0f}"), color=col)
        reading_axes(ax, xlim=(0, 13.5), ylim=(0, 12))
    fig.tight_layout()
    save(fig, "b1_mle")

    NUMBERS["guess"] = {"intercept": guess[0], "slope": guess[1]}


# ----------------------------------------------------------------------------
# Block 2 - uncertainty
# ----------------------------------------------------------------------------
def fig_b2(df, fit, idata):
    xs = np.array([0, 12.5])
    b_hat = fit.params["words"]

    # 1. three new datasets
    fig, axes = plt.subplots(1, 3, figsize=WIDE, sharey=True)
    for ax, seed in zip(axes, (101, 202, 303)):
        d = repeat_study(seed=seed)
        f = smf.ols("time ~ words", d).fit()
        ax.plot(xs, TRUE["intercept"] + TRUE["slope"] * xs, color=SAGE, lw=2, ls="--")
        ax.plot(xs, f.params["Intercept"] + f.params["words"] * xs, color=BLUE, lw=3)
        scatter_data(ax, d, s=28)
        ax.set_title(f"New sample: slope = {f.params['words']:.2f}", color=BLUE_DARK)
        reading_axes(ax)
        ax.set_xticks([0, 4, 8, 12])
        ax.set_xlabel("Text length (×100 words)")
        if ax is not axes[0]:
            ax.set_ylabel("")
    fig.tight_layout()
    save(fig, "b2_three_datasets")

    # 2. sampling distribution
    rng = np.random.default_rng(7)
    slopes = []
    for _ in range(2000):
        d = repeat_study(seed=int(rng.integers(1e9)))
        slopes.append(np.polyfit(d["words"], d["time"], 1)[0])
    slopes = np.array(slopes)
    sd = slopes.std()
    NUMBERS["sampling_sd"] = r(sd, 3)
    fig, ax = plt.subplots(figsize=RIGHT)
    ax.hist(slopes, bins=45, color=BLUE, alpha=0.85)
    ax.axvline(TRUE["slope"], color=SAGE_DARK, lw=2.5, ls="--")
    ax.text(
        TRUE["slope"] + 0.004,
        ax.get_ylim()[1] * 0.97,
        "true slope",
        color=SAGE_DARK,
        va="top",
        fontsize=14,
        bbox=dict(boxstyle="round,pad=0.2", fc="white", ec="none", alpha=0.9),
    )
    y = ax.get_ylim()[1] * 0.55
    ax.annotate(
        "",
        xy=(TRUE["slope"] - sd, y),
        xytext=(TRUE["slope"] + sd, y),
        arrowprops=dict(arrowstyle="<->", color=BLUE_DARK, lw=2),
    )
    ax.text(
        TRUE["slope"] + sd + 0.006,
        y,
        f"± 1 SD\n≈ {sd:.3f}",
        color=BLUE_DARK,
        va="center",
        fontsize=14,
    )
    ax.set_xlabel("Estimated slope (2000 simulated studies)")
    ax.set_ylabel("Number of studies")
    ax.grid(axis="x")
    fig.tight_layout()
    save(fig, "b2_sampling_dist")

    # 3. CI coverage
    rng = np.random.default_rng(11)
    rows = []
    for _ in range(50):
        d = repeat_study(seed=int(rng.integers(1e9)))
        f = smf.ols("time ~ words", d).fit()
        lo, hi = ols_ci(f, "words")
        rows.append((f.params["words"], lo, hi))
    rows = np.array(rows)
    miss = (rows[:, 1] > TRUE["slope"]) | (rows[:, 2] < TRUE["slope"])
    NUMBERS["ci_coverage"] = {"n": 50, "miss": int(miss.sum())}
    fig, ax = plt.subplots(figsize=RIGHT)
    for i, (est, lo, hi) in enumerate(rows):
        col = GREY_DARK if miss[i] else BLUE
        ax.plot(
            [lo, hi],
            [i, i],
            color=col,
            lw=3 if miss[i] else 2.2,
            solid_capstyle="round",
        )
        ax.scatter([est], [i], color=col if miss[i] else BLUE_DARK, s=14, zorder=3)
    ax.axvline(TRUE["slope"], color=SAGE_DARK, lw=2.5, ls="--")
    ax.set_yticks([])
    ax.set_ylabel("50 simulated studies")
    ax.set_xlabel("95% confidence interval for the slope")
    ax.set_title(
        f"{50 - miss.sum()} of 50 intervals contain the true slope", color=BLUE_DARK
    )
    ax.grid(axis="y")
    fig.tight_layout()
    save(fig, "b2_ci_coverage")

    # 4. p-value: the null world
    rng = np.random.default_rng(5)
    null_slopes = []
    for _ in range(2000):
        d = repeat_study(slope=0.0, seed=int(rng.integers(1e9)))
        null_slopes.append(np.polyfit(d["words"], d["time"], 1)[0])
    null_slopes = np.array(null_slopes)
    fig, ax = plt.subplots(figsize=RIGHT)
    ax.hist(null_slopes, bins=45, color=GREY_LIGHT)
    ax.axvline(b_hat, color=BLUE_DARK, lw=3)
    ax.text(
        b_hat - 0.02,
        ax.get_ylim()[1] * 0.95,
        f"our slope\n{b_hat:.2f}",
        color=BLUE_DARK,
        ha="right",
        va="top",
        fontsize=14,
    )
    ax.text(
        0,
        ax.get_ylim()[1] * 1.02,
        "slopes we would see\nif the true slope were 0",
        color=GREY,
        ha="center",
        va="bottom",
        fontsize=14,
    )
    ax.set_xlim(-0.3, 1.0)
    ax.set_xlabel("Estimated slope")
    ax.set_ylabel("Number of studies")
    ax.grid(axis="x")
    fig.tight_layout()
    save(fig, "b2_pvalue")
    NUMBERS["p_value"] = float(fit.pvalues["words"])

    # 5. priors as lines
    rng = np.random.default_rng(4)
    fig, axes = plt.subplots(1, 2, figsize=WIDE, sharey=True)
    for ax, (sa, sb), title in [
        (axes[0], (100, 100), "Vague prior:  slope ~ Normal(0, 100)"),
        (axes[1], (5, 2), "Weakly informative:  slope ~ Normal(0, 2)"),
    ]:
        for _ in range(60):
            ax.plot(
                xs,
                rng.normal(0, sa) + rng.normal(0, sb) * xs,
                color=ROSE,
                alpha=0.3,
                lw=1.5,
            )
        ax.set_title(title, color=ROSE_DARK)
        reading_axes(ax, ylim=(-15, 25))
        if ax is not axes[0]:
            ax.set_ylabel("")
        ax.axhspan(0, 15, color=GREY_BAR, alpha=0.6, zorder=0)
    for ax in axes:
        ax.text(
            12.2,
            14.2,
            "plausible reading times",
            color=GREY,
            fontsize=12,
            ha="right",
            va="top",
            zorder=5,
            bbox=dict(boxstyle="round,pad=0.25", fc="white", ec="none", alpha=0.9),
        )
    fig.tight_layout()
    save(fig, "b2_prior_lines")

    # 6. posterior spaghetti
    ia, sb = draws(idata, "intercept"), draws(idata, "slope")
    rng = np.random.default_rng(1)
    idx = rng.choice(len(ia), 150, replace=False)
    fig, ax = plt.subplots(figsize=RIGHT)
    for j in idx:
        ax.plot(xs, ia[j] + sb[j] * xs, color=ROSE, alpha=0.08, lw=1.5, zorder=1)
    ax.plot([], [], color=ROSE, lw=3, label="150 plausible lines (posterior)")
    ax.plot(
        xs,
        fit.params["Intercept"] + b_hat * xs,
        color=BLUE_DARK,
        lw=2,
        ls="--",
        label="least-squares line",
        zorder=2,
    )
    scatter_data(ax, df)
    ax.legend(loc="upper left")
    reading_axes(ax)
    fig.tight_layout()
    save(fig, "b2_spaghetti")

    # 7. MCMC: trace -> histogram
    post = np.asarray(idata.posterior["slope"].values)  # chain, draw
    fig, (ax1, ax2) = plt.subplots(
        1, 2, figsize=WIDE, sharey=True, gridspec_kw=dict(width_ratios=[3, 1.2])
    )
    for c, col in zip(range(post.shape[0]), (ROSE, ROSE_DARK)):
        ax1.plot(
            np.arange(300),
            post[c, :300],
            color=col,
            lw=1.2,
            alpha=0.9,
            label=f"chain {c + 1}",
        )
    ax1.set_xlabel("Step of the sampler")
    ax1.set_ylabel("Slope")
    ax1.legend(loc="upper right", ncol=2)
    ax1.set_title("The sampler wanders through plausible values…", color=ROSE_DARK)
    ax2.hist(post.ravel(), bins=40, orientation="horizontal", color=ROSE, alpha=0.85)
    ax2.set_xlabel("Count")
    ax2.set_title("…and the visits form the posterior", color=ROSE_DARK)
    fig.tight_layout()
    save(fig, "b2_mcmc")

    # 8. credible interval and P(slope > 0.8)
    lo, hi = interval(sb)
    p_gt = float((sb > 0.8).mean())
    NUMBERS["bayes"] = {
        "slope_mean": r(sb.mean(), 3),
        "slope_ci": [r(lo, 2), r(hi, 2)],
        "intercept_mean": r(ia.mean(), 2),
        "sigma_mean": r(draws(idata, "sigma").mean(), 2),
        "p_slope_gt_0": r((sb > 0).mean(), 3),
        "p_slope_gt_08": r(p_gt, 2),
    }
    fig, ax = plt.subplots(figsize=RIGHT)
    kde = stats.gaussian_kde(sb)
    grid = np.linspace(sb.min(), sb.max(), 400)
    dens = kde(grid)
    ax.plot(grid, dens, color=ROSE_DARK, lw=2.5)
    m = (grid >= lo) & (grid <= hi)
    ax.fill_between(grid[m], dens[m], color=ROSE_LIGHT, alpha=0.8, lw=0)
    m2 = grid > 0.8
    ax.fill_between(
        grid[m2],
        dens[m2],
        color=ROSE,
        alpha=0.75,
        lw=0,
        hatch="",
        label=f"P(slope > 0.8 | data) = {p_gt:.2f}",
    )
    ax.plot([lo, hi], [0.35, 0.35], color=ROSE_DARK, lw=4)
    ax.text(
        (lo + hi) / 2,
        0.9,
        f"95% credible interval\n[{lo:.2f}, {hi:.2f}]",
        ha="center",
        va="bottom",
        color=ROSE_DARK,
        fontsize=14,
    )
    ax.legend(loc="upper right")
    ax.set_xlabel("Slope (minutes per 100 words)")
    ax.set_ylabel("Posterior density")
    ax.set_ylim(0, dens.max() * 1.22)
    ax.grid(axis="x")
    fig.tight_layout()
    save(fig, "b2_credible")

    # 9. intervals side by side
    clo, chi = ols_ci(fit, "words")
    fig, ax = plt.subplots(figsize=(12.0, 1.8))
    ax.plot([clo, chi], [1, 1], color=BLUE, lw=6)
    ax.scatter([b_hat], [1], color=BLUE_DARK, s=60, zorder=3)
    ax.plot([lo, hi], [0, 0], color=ROSE, lw=6)
    ax.scatter([sb.mean()], [0], color=ROSE_DARK, s=60, zorder=3)
    ax.set_yticks([0, 1], ["Bayesian 95% credible", "Frequentist 95% confidence"])
    ax.set_ylim(-0.7, 1.7)
    ax.set_xlim(0.6, 1.0)
    ax.set_xlabel("Slope")
    ax.grid(axis="y")
    fig.tight_layout()
    save(fig, "b2_compare_intervals")

    # 10. when do they disagree? strong prior, growing n
    prior_mu, prior_sd = 0.4, 0.1
    rows = []
    for n, seed in ((8, 21), (40, 226), (400, 33)):
        d = simulate_reading(n=n, seed=seed)
        f = smf.ols("time ~ words", d).fit()
        idn = fit_reading_bayes(d, slope_mu=prior_mu, slope_sigma=prior_sd, seed=2)
        s = draws(idn, "slope")
        rows.append((n, f.params["words"], *ols_ci(f, "words"), s.mean(), *interval(s)))
    NUMBERS["disagree"] = [
        {
            "n": n,
            "ols": r(b, 2),
            "ols_ci": [r(lo1, 2), r(hi1, 2)],
            "bayes": r(m, 2),
            "bayes_ci": [r(lo2, 2), r(hi2, 2)],
        }
        for n, b, lo1, hi1, m, lo2, hi2 in rows
    ]
    fig, ax = plt.subplots(figsize=WIDE)
    ax.axvspan(
        prior_mu - 2 * prior_sd,
        prior_mu + 2 * prior_sd,
        color=ROSE_LIGHT,
        alpha=0.4,
        lw=0,
    )
    ax.text(
        prior_mu,
        2.62,
        "strong prior\nNormal(0.4, 0.1)",
        ha="center",
        va="bottom",
        color=ROSE_DARK,
        fontsize=13,
    )
    ax.axvline(TRUE["slope"], color=SAGE_DARK, lw=2.5, ls="--")
    ax.text(
        TRUE["slope"] + 0.01,
        2.62,
        "true slope",
        color=SAGE_DARK,
        va="bottom",
        fontsize=13,
    )
    for k, (n, b, lo1, hi1, m, lo2, hi2) in enumerate(rows):
        ax.plot([lo1, hi1], [k + 0.15] * 2, color=BLUE, lw=6)
        ax.scatter([b], [k + 0.15], color=BLUE_DARK, s=60, zorder=3)
        ax.plot([lo2, hi2], [k - 0.15] * 2, color=ROSE, lw=6)
        ax.scatter([m], [k - 0.15], color=ROSE_DARK, s=60, zorder=3)
    ax.plot([], [], color=BLUE, lw=6, label="least squares, 95% CI")
    ax.plot([], [], color=ROSE, lw=6, label="posterior, 95% credible interval")
    ax.set_yticks(range(3), [f"n = {n}" for n, *_ in rows])
    ax.set_ylim(-0.6, 3.2)
    ax.set_xlim(0.0, 1.3)
    ax.set_xlabel("Slope (minutes per 100 words)")
    ax.legend(loc="lower right")
    ax.grid(axis="y")
    fig.tight_layout()
    save(fig, "b2_disagree")


# ----------------------------------------------------------------------------
# Block 3 - KidIQ
# ----------------------------------------------------------------------------
HS_COL = {0: GREY_MID, 1: SAGE}
HS_LINE = {0: GREY_DARK, 1: SAGE_DARK}
HS_LAB = {0: "mother did not finish high school", 1: "mother finished high school"}


def kid_scatter(ax, kid, x="mom_iq", alpha=0.7, s=22):
    for hs in (0, 1):
        k = kid[kid.mom_hs == hs]
        ax.scatter(
            k[x],
            k.kid_score,
            color=HS_COL[hs],
            s=s,
            alpha=alpha,
            label=HS_LAB[hs],
            zorder=2,
        )


def fig_b3(kid, idk):
    f_hs = smf.ols("kid_score ~ mom_hs", kid).fit()
    f_iq = smf.ols("kid_score ~ mom_iq", kid).fit()
    f_iqc = smf.ols("kid_score ~ mom_iq_c", kid).fit()
    f_both = smf.ols("kid_score ~ mom_hs + mom_iq_c", kid).fit()
    f_int = smf.ols("kid_score ~ mom_hs * mom_iq_c", kid).fit()

    NUMBERS["kid"] = {
        "n": len(kid),
        "hs_only": {k: r(v, 2) for k, v in f_hs.params.items()},
        "hs_only_ci": [r(v, 1) for v in ols_ci(f_hs, "mom_hs")],
        "iq_raw": {k: r(v, 2) for k, v in f_iq.params.items()},
        "iq_c": {k: r(v, 2) for k, v in f_iqc.params.items()},
        "both": {k: r(v, 2) for k, v in f_both.params.items()},
        "both_ci": {
            k: [r(v, 2) for v in ols_ci(f_both, k)] for k in f_both.params.index
        },
        "both_sigma": r(np.sqrt(f_both.scale), 1),
        "interaction": {k: r(v, 2) for k, v in f_int.params.items()},
        "group_iq": {
            int(k): r(v, 1) for k, v in kid.groupby("mom_hs").mom_iq.mean().items()
        },
        "group_score": {
            int(k): r(v, 1) for k, v in kid.groupby("mom_hs").kid_score.mean().items()
        },
        "group_n": {int(k): int(v) for k, v in kid.mom_hs.value_counts().items()},
    }
    bayes = {}
    for name in ("intercept", "b_hs", "b_iq", "sigma"):
        s = draws(idk, name)
        bayes[name] = {"mean": r(s.mean(), 2), "ci": [r(v, 2) for v in interval(s)]}
    NUMBERS["kid"]["bayes"] = bayes

    # 1. scatter
    fig, ax = plt.subplots(figsize=RIGHT)
    kid_scatter(ax, kid)
    ax.set_xlabel("Mother's IQ")
    ax.set_ylabel("Child's test score")
    ax.legend(loc="lower right", markerscale=1.6)
    fig.tight_layout()
    save(fig, "b3_scatter")

    # 2. binary predictor
    rng = np.random.default_rng(2)
    fig, ax = plt.subplots(figsize=RIGHT)
    for hs in (0, 1):
        k = kid[kid.mom_hs == hs]
        ax.scatter(
            hs + rng.uniform(-0.12, 0.12, len(k)),
            k.kid_score,
            color=HS_COL[hs],
            s=18,
            alpha=0.6,
        )
    means = kid.groupby("mom_hs").kid_score.mean()
    ax.plot([0, 1], means.values, color=BLUE_DARK, lw=3, zorder=3)
    ax.scatter([0, 1], means.values, color=BLUE_DARK, s=140, zorder=4)
    ax.text(
        0.18,
        means[0] - 4,
        f"mean = {means[0]:.1f}\n= intercept",
        color=BLUE_DARK,
        fontsize=14,
        va="top",
    )
    ax.text(
        0.82,
        means[1] + 7,
        f"mean = {means[1]:.1f}",
        color=BLUE_DARK,
        fontsize=14,
        ha="right",
    )
    ax.text(
        0.5,
        128,
        f"slope = {means[1]:.1f} − {means[0]:.1f} = {means[1] - means[0]:.1f}",
        ha="center",
        color=BLUE_DARK,
        fontsize=15,
        fontweight="bold",
    )
    ax.set_xticks([0, 1], ["0 = no", "1 = yes"])
    ax.set_xlim(-0.4, 1.4)
    ax.set_xlabel("mom_hs  (mother finished high school)")
    ax.set_ylabel("Child's test score")
    ax.grid(axis="x")
    fig.tight_layout()
    save(fig, "b3_binary")

    # 3. centering
    fig, axes = plt.subplots(1, 2, figsize=WIDE)
    ax = axes[0]
    ax.scatter(kid.mom_iq, kid.kid_score, color=GREY_MID, s=14, alpha=0.5)
    xx = np.array([0, 140])
    ax.plot(xx, f_iq.params["Intercept"] + f_iq.params["mom_iq"] * xx, color=BLUE, lw=3)
    ax.scatter(
        [0], [f_iq.params["Intercept"]], color=ROSE_DARK, s=100, zorder=4, clip_on=False
    )
    ax.text(
        4,
        f_iq.params["Intercept"] - 14,
        f"intercept = {f_iq.params['Intercept']:.1f}:\nscore of a child whose\nmother has IQ 0 (?!)",
        color=ROSE_DARK,
        fontsize=13,
        va="top",
    )
    ax.set_xlim(0, 145)
    ax.set_ylim(-20, 150)
    ax.set_xlabel("mom_iq")
    ax.set_ylabel("Child's test score")
    ax.set_title("Raw IQ", color=GREY)
    ax = axes[1]
    ax.scatter(kid.mom_iq_c, kid.kid_score, color=GREY_MID, s=14, alpha=0.5)
    xx = np.array([-35, 45])
    ax.plot(
        xx, f_iqc.params["Intercept"] + f_iqc.params["mom_iq_c"] * xx, color=BLUE, lw=3
    )
    ax.scatter([0], [f_iqc.params["Intercept"]], color=ROSE_DARK, s=100, zorder=4)
    ax.axvline(0, color=GREY_LIGHT, lw=1.5, ls=":")
    ax.text(
        2,
        30,
        f"intercept = {f_iqc.params['Intercept']:.1f}:\nscore of a child whose\nmother has IQ 100",
        color=ROSE_DARK,
        fontsize=13,
    )
    ax.set_xlim(-35, 45)
    ax.set_ylim(-20, 150)
    ax.set_xlabel("mom_iq_c = mom_iq − 100")
    ax.set_title("Centered IQ", color=GREY)
    fig.tight_layout()
    save(fig, "b3_centering")

    # 4. parallel lines
    fig, ax = plt.subplots(figsize=RIGHT)
    kid_scatter(ax, kid, x="mom_iq_c", alpha=0.45, s=16)
    xx = np.array([-30, 40])
    p = f_both.params
    for hs in (0, 1):
        ax.plot(
            xx,
            p["Intercept"] + p["mom_hs"] * hs + p["mom_iq_c"] * xx,
            color=HS_LINE[hs],
            lw=3.5,
        )
    x0 = 30
    y0 = p["Intercept"] + p["mom_iq_c"] * x0
    ax.annotate(
        "",
        xy=(x0, y0 + p["mom_hs"]),
        xytext=(x0, y0),
        arrowprops=dict(arrowstyle="<->", color=GREY_DARK, lw=2.5),
        zorder=5,
    )
    ax.annotate(
        f"same gap everywhere:\n{p['mom_hs']:.1f} points",
        xy=(x0, y0 + p["mom_hs"] / 2),
        xytext=(8, 130),
        color=GREY_DARK,
        fontsize=14,
        fontweight="bold",
        zorder=5,
        arrowprops=dict(arrowstyle="-", color=GREY_DARK, lw=1.2),
        bbox=dict(boxstyle="round,pad=0.3", fc="white", ec="none", alpha=0.9),
    )
    ax.set_ylim(15, 150)
    ax.set_xlabel("mom_iq_c  (mother's IQ − 100)")
    ax.set_ylabel("Child's test score")
    ax.legend(loc="lower right", markerscale=1.6)
    fig.tight_layout()
    save(fig, "b3_parallel")

    # 5. why the coefficient changes
    fig, axes = plt.subplots(
        1, 2, figsize=WIDE, gridspec_kw=dict(width_ratios=[1, 1.25])
    )
    ax = axes[0]
    for hs in (0, 1):
        k = kid[kid.mom_hs == hs]
        ax.scatter(
            hs + rng.uniform(-0.12, 0.12, len(k)),
            k.mom_iq,
            color=HS_COL[hs],
            s=16,
            alpha=0.55,
        )
    g = kid.groupby("mom_hs").mom_iq.mean()
    ax.scatter([0, 1], g.values, color=GREY_DARK, s=140, zorder=3)
    for hs in (0, 1):
        ax.text(
            hs + 0.2,
            g[hs],
            f"{g[hs]:.0f}",
            va="center",
            color=GREY_DARK,
            fontsize=15,
            fontweight="bold",
        )
    ax.set_xticks([0, 1], ["no", "yes"])
    ax.set_xlim(-0.4, 1.5)
    ax.set_xlabel("Mother finished high school")
    ax.set_ylabel("Mother's IQ")
    ax.set_title("High-school mothers have higher IQ", color=GREY)
    ax.grid(axis="x")
    ax = axes[1]
    for k_, (lab, f) in enumerate([("mom_hs only", f_hs), ("mom_hs + mom_iq", f_both)]):
        lo, hi = ols_ci(f, "mom_hs")
        ax.plot([lo, hi], [k_, k_], color=BLUE, lw=7)
        ax.scatter([f.params["mom_hs"]], [k_], color=BLUE_DARK, s=80, zorder=3)
        ax.text(
            f.params["mom_hs"],
            k_ + 0.22,
            f"{f.params['mom_hs']:.1f}",
            ha="center",
            color=BLUE_DARK,
            fontsize=15,
            fontweight="bold",
        )
    ax.axvline(0, color=GREY_LIGHT, lw=1.5)
    ax.set_yticks([0, 1], ["mom_hs only", "mom_hs + mom_iq"])
    ax.set_ylim(-0.6, 1.6)
    ax.set_xlabel("Coefficient of mom_hs (95% CI)")
    ax.set_title("So part of the high-school gap was about IQ", color=GREY)
    ax.grid(axis="y")
    fig.tight_layout()
    save(fig, "b3_coef_change")

    # 6. forest: OLS vs Bayes for the combined model
    names = [
        ("Intercept", "intercept", "intercept"),
        ("mom_hs", "b_hs", "mom_hs"),
        ("mom_iq_c", "b_iq", "mom_iq_c"),
    ]
    fig, axes = plt.subplots(3, 1, figsize=(6.4, 4.9))
    for ax, (ols_name, bname, label) in zip(axes, names):
        lo, hi = ols_ci(f_both, ols_name)
        s = draws(idk, bname)
        blo, bhi = interval(s)
        ax.plot([lo, hi], [1, 1], color=BLUE, lw=6)
        ax.scatter([f_both.params[ols_name]], [1], color=BLUE_DARK, s=50, zorder=3)
        ax.plot([blo, bhi], [0, 0], color=ROSE, lw=6)
        ax.scatter([s.mean()], [0], color=ROSE_DARK, s=50, zorder=3)
        ax.set_yticks([])
        ax.set_ylim(-0.7, 1.7)
        ax.set_title(label, fontsize=14, loc="left", pad=2)
        ax.grid(axis="y")
        span = max(hi, bhi) - min(lo, blo)
        ax.set_xlim(min(lo, blo) - 0.25 * span, max(hi, bhi) + 0.25 * span)
    axes[0].plot([], [], color=BLUE, lw=6, label="statsmodels 95% CI")
    axes[0].plot([], [], color=ROSE, lw=6, label="PyMC 95% credible")
    axes[0].legend(loc="center left", bbox_to_anchor=(1.0, 0.5), fontsize=12)
    fig.tight_layout()
    save(fig, "b3_forest")

    # 7. interaction
    fig, ax = plt.subplots(figsize=RIGHT)
    kid_scatter(ax, kid, x="mom_iq_c", alpha=0.45, s=16)
    p = f_int.params
    for hs in (0, 1):
        slope = p["mom_iq_c"] + p["mom_hs:mom_iq_c"] * hs
        icpt = p["Intercept"] + p["mom_hs"] * hs
        ax.plot(xx, icpt + slope * xx, color=HS_LINE[hs], lw=3.5)
        ax.text(
            41,
            icpt + slope * 40,
            f"slope {slope:.2f}",
            color=HS_LINE[hs],
            va="center",
            fontsize=14,
        )
    ax.set_xlim(-32, 52)
    ax.set_xlabel("mom_iq_c  (mother's IQ − 100)")
    ax.set_ylabel("Child's test score")
    ax.legend(loc="lower right", markerscale=1.6)
    fig.tight_layout()
    save(fig, "b3_interaction")


# ----------------------------------------------------------------------------
# Equations
# ----------------------------------------------------------------------------
def equation(name, parts, size=30, label_size=15, height=1.3):
    """Render [(tex, colour, label or None), ...] side by side with labels below."""
    fig = plt.figure(figsize=(14, height))
    renderer = fig.canvas.get_renderer()
    x = 0.0
    for tex, col, label in parts:
        t = fig.text(0, 0.62, tex, fontsize=size, color=col, va="center", ha="left")
        w = t.get_window_extent(renderer).width / fig.bbox.width
        lw = 0.0
        if label:
            lab = fig.text(
                0, 0.08, label, fontsize=label_size, color=col, ha="center", va="bottom"
            )
            lw = lab.get_window_extent(renderer).width / fig.bbox.width + 0.02
        slot = max(w, lw)
        t.set_x(x + (slot - w) / 2)
        if label:
            lab.set_x(x + slot / 2)
        x += slot + 0.008
    fig.savefig(
        OUT / f"{name}.png",
        dpi=220,
        transparent=True,
        bbox_inches="tight",
        pad_inches=0.04,
    )
    plt.close(fig)
    print("  wrote", name)


def equations():
    equation(
        "eq_line",
        [
            (r"$y_i$", GREY, "reading time"),
            (r"$=$", GREY, None),
            (r"$a$", ROSE_DARK, "intercept"),
            (r"$+$", GREY, None),
            (r"$b \, x_i$", BLUE_DARK, "slope × length"),
            (r"$+$", GREY, None),
            (r"$\varepsilon_i$", SAGE_DARK, "error"),
            (
                r"$,\quad \varepsilon_i \sim \mathrm{Normal}(0,\ \sigma)$",
                SAGE_DARK,
                None,
            ),
        ],
    )
    equation(
        "eq_rss",
        [
            (
                r"$\mathrm{RSS}(a, b) = \sum_{i=1}^{n} \left(y_i - (a + b\,x_i)\right)^2$",
                GREY,
                None,
            )
        ],
        height=1.0,
    )
    equation(
        "eq_likelihood",
        [
            (
                r"$p(\mathrm{data} \mid a, b, \sigma) = \prod_{i=1}^{n} \mathrm{Normal}(y_i \mid a + b\,x_i,\ \sigma)$",
                GREY,
                None,
            )
        ],
        size=26,
        height=1.0,
    )
    equation(
        "eq_bayes",
        [
            (r"$p(a, b, \sigma \mid \mathrm{data})$", ROSE_DARK, "posterior"),
            (r"$\propto$", GREY, None),
            (r"$p(\mathrm{data} \mid a, b, \sigma)$", BLUE_DARK, "likelihood"),
            (r"$\times$", GREY, None),
            (r"$p(a, b, \sigma)$", ROSE, "prior"),
        ],
        size=32,
    )
    equation(
        "eq_multi",
        [
            (
                r"$\mathrm{score}_i = a + b_1\,\mathrm{hs}_i + b_2\,(\mathrm{iq}_i - 100) + \varepsilon_i$",
                GREY,
                None,
            )
        ],
        size=28,
        height=1.0,
    )
    equation(
        "eq_interaction",
        [
            (
                r"$\mathrm{score}_i = a + b_1\,\mathrm{hs}_i + b_2\,\mathrm{iq}^c_i + b_3\,\mathrm{hs}_i\,\mathrm{iq}^c_i + \varepsilon_i$",
                GREY,
                None,
            )
        ],
        size=26,
        height=1.0,
    )
    # appendix
    equation(
        "eq_ols_closed",
        [
            (
                r"$\hat b = \frac{\sum_i (x_i - \bar x)(y_i - \bar y)}{\sum_i (x_i - \bar x)^2},"
                r"\qquad \hat a = \bar y - \hat b\,\bar x$",
                GREY,
                None,
            )
        ],
        size=26,
        height=1.4,
    )
    equation(
        "eq_ols_matrix",
        [(r"$\hat\beta = (X^{\top}X)^{-1} X^{\top} y$", GREY, None)],
        size=26,
        height=1.0,
    )
    equation(
        "eq_loglik",
        [
            (
                r"$\log p(\mathrm{data} \mid a, b, \sigma) = -n \log \sigma - \frac{1}{2\sigma^2}\,"
                r"\mathrm{RSS}(a, b) + \mathrm{const}$",
                GREY,
                None,
            )
        ],
        size=24,
        height=1.3,
    )
    equation(
        "eq_ridge",
        [
            (
                r"$-\log p(a, b \mid \mathrm{data}) = \frac{1}{2\sigma^2}\,\mathrm{RSS}(a, b) + "
                r"\frac{1}{2\tau^2}\,b^2 + \mathrm{const}$",
                GREY,
                None,
            )
        ],
        size=24,
        height=1.3,
    )


# ----------------------------------------------------------------------------
# QR codes
# ----------------------------------------------------------------------------
def qr(name, url):
    q = qrcode.QRCode(
        border=1, box_size=12, error_correction=qrcode.constants.ERROR_CORRECT_M
    )
    q.add_data(url)
    q.make(fit=True)
    img = q.make_image(fill_color=GREY, back_color="white")
    img.save(OUT / f"{name}.png")
    print("  wrote", name)


def qr_codes():
    for nb in (
        "01_fitting_a_line",
        "02_uncertainty_two_ways",
        "03_multiple_predictors",
    ):
        qr(f"qr_{nb[:2]}", f"{COLAB}/{nb}.ipynb")
    qr("qr_quiz", QUIZ_URL)
    NUMBERS["urls"] = {
        "nb1": f"{COLAB}/01_fitting_a_line.ipynb",
        "nb2": f"{COLAB}/02_uncertainty_two_ways.ipynb",
        "nb3": f"{COLAB}/03_multiple_predictors.ipynb",
        "quiz": QUIZ_URL,
    }


# ----------------------------------------------------------------------------
def main():
    use_style(14)
    df = simulate_reading()
    fit = smf.ols("time ~ words", df).fit()
    NUMBERS["reading"] = {
        "n": len(df),
        "true": TRUE,
        "ols": {k: r(v, 3) for k, v in fit.params.items()},
        "ols_se": {k: r(v, 3) for k, v in fit.bse.items()},
        "ols_t": {k: r(v, 2) for k, v in fit.tvalues.items()},
        "ols_p": {k: float(v) for k, v in fit.pvalues.items()},
        "ols_ci": {k: [r(v, 3) for v in ols_ci(fit, k)] for k in fit.params.index},
        "ols_sigma": r(np.sqrt(fit.scale), 3),
    }
    print("Fitting Bayesian models…")
    idata = fit_reading_bayes(df)
    kid = pd.read_csv(ROOT / "data" / "kidiq.csv")
    kid["mom_iq_c"] = kid["mom_iq"] - 100
    idk = fit_kid_bayes(kid)

    print("Drawing figures…")
    fig_title_motif()
    fig_b1(df, fit)
    fig_b2(df, fit, idata)
    fig_b3(kid, idk)
    equations()
    qr_codes()
    (OUT / "numbers.json").write_text(json.dumps(NUMBERS, indent=2))
    print("  wrote numbers.json")


if __name__ == "__main__":
    main()
