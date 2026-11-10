# Linear regression, two ways — course plan (draft)

Hands-on class: linear regression from a frequentist and a Bayesian perspective.

## Decisions so far

| | |
|---|---|
| Title | **Session 1 - Linear regressions** |
| Language | English (slides, notebooks, quiz). |
| Audience | Beginners in statistics and coding. Intuition, pictures and simulation first; notebooks are "run, read, modify". |
| Stack | Python: `statsmodels` (frequentist) + `PyMC` / `ArviZ` (Bayesian). |
| Running notebooks | Google Colab: "Open in Colab" badges, data loaded from this GitHub repo. |
| Format | 3 alternating blocks (short slides, then a notebook), a break, a final quiz with debrief. |
| Scope | Simple regression (backbone) → uncertainty & inference → multiple predictors. Prediction/model checking and prior predictive checks are out of scope (one slide on priors only). |
| Data | Simulated data with known truth (blocks 1–2), then ROS **KidIQ** (block 3). |
| Slides | Editable `.pptx` generated with python-pptx in the style of `sources/Aarhus Agentic Meetup.pptx`. |
| Quiz | Standalone HTML multiple-choice quiz with instant corrections and a final score. Runs entirely in the browser; no answers are collected. |
| Solutions | Separate solution notebooks in `notebooks/solutions/`, released after class. |

## Learning objectives

By the end, participants can:

1. Explain what intercept, slope and residual SD (σ) mean in a fitted line.
2. Describe least squares as "the line with the smallest squared residuals", and say that maximum likelihood gives the same line.
3. Correctly interpret a standard error, a 95% confidence interval and a p-value.
4. Explain a posterior as "many plausible lines", and read a credible interval and P(slope > 0).
5. Fit the same model with `statsmodels` and `PyMC` and compare the results side by side.
6. Interpret coefficients in a model with two predictors (one binary, one continuous), including why coefficients change when a predictor is added.

## Running order

| Activity | Material |
|---|---|
| Welcome, goals, everyone opens Notebook 1 in Colab and runs the setup cell | Slides intro |
| **Block 1 — Drawing a line through data** | Slides §1 |
| Hands-on | `01_fitting_a_line.ipynb` |
| **Block 2 — How sure are we? Two answers** | Slides §2 |
| Hands-on | `02_uncertainty_two_ways.ipynb` |
| Break | |
| **Block 3 — More than one predictor** | Slides §3 |
| Hands-on | `03_multiple_predictors.ipynb` |
| Quiz (individual) | `quiz/index.html` |
| Debrief of the most-missed questions, wrap-up, where to go next | Slides outro |

Block 2 is the densest because it also introduces Bayes. The p-value demo can move from the slides into the notebook if needed.

## Running examples

- **Simulated: reading time vs text length** (blocks 1–2). `x` = text length (hundreds of words), `y` = reading time (minutes). True values: intercept 0.5, slope 0.8, σ 1.0, n = 40. The intercept is interpretable and the ground truth is visible, so participants can check parameter recovery, run sampling-distribution simulations and test CI coverage.
- **ROS KidIQ** (block 3). 434 children: `kid_score` (cognitive test score at age 3–4), `mom_hs` (mother finished high school, 0/1), `mom_iq`. This is the ROS ch. 10 example, so known answers are available (≈ 26 + 6·mom_hs + 0.6·mom_iq). Copied to `data/kidiq.csv`.

## Block 1 — Drawing a line through data (≈10 slides)

| # | Slide | Visual |
|---|---|---|
| 1.1 | Section header | — |
| 1.2 | Why regression? Describe · Predict · Explain | 3 numbered cards |
| 1.3 | Our example: reading time vs text length | Scatter |
| 1.4 | Anatomy of a line: intercept and slope | Annotated line |
| 1.5 | Data don't sit on the line: the error term and σ | Line with Normal curves drawn along it |
| 1.6 | Which line is best? Residuals | Scatter with residual segments |
| 1.7 | Least squares: smallest sum of squared residuals | Squares drawn on residuals, 2 candidate lines + their RSS |
| 1.8 | A second road to the same line: maximum likelihood | Bell curves; one small equation; "same line if errors are Normal" |
| 1.9 | Reading the output | `statsmodels` summary with only coef and std err highlighted |
| 1.10 | Hands-on 1 | Colab link and QR code, 3-item task list |

**Notebook 1 — `01_fitting_a_line.ipynb`**
1. Setup cell: install if missing, imports, shared plot style.
2. Simulate the data (function given, true values shown) and plot it.
3. **Guess the line**: `ipywidgets` sliders for intercept/slope, with live residuals and RSS. Who gets the lowest RSS?
4. Fit with `smf.ols("time ~ words", df)` and compare with the truth and with their own guess.
5. ✏️ Change n and σ, refit, and describe what happens to the estimates.
6. ✏️ Predict the reading time for a 1000-word text.

## Block 2 — How sure are we? Two answers (≈13 slides)

| # | Slide | Visual |
|---|---|---|
| 2.1 | Section header | — |
| 2.2 | Two meanings of probability (recap from the intro deck) | Two-column card: long-run frequency vs degree of belief |
| 2.3 | If we collected new data… | 3 datasets → 3 different lines |
| 2.4 | Sampling distribution and standard error | Histogram of 1000 simulated slopes |
| 2.5 | What a 95% confidence interval means | 50 CIs, the ~5% that miss the truth highlighted |
| 2.6 | p-value: what it is and what it isn't | "Null world" simulation histogram plus observed slope |
| 2.7 | The Bayesian route: prior × likelihood → posterior | Bayes anatomy, same layout as the intro deck |
| 2.8 | What a prior on a slope means | Lines drawn from a wild vs a weak prior |
| 2.9 | From one best line to thousands of plausible lines | Posterior "spaghetti" plot |
| 2.10 | MCMC in one picture | Trace → histogram; "R-hat ≈ 1 means OK" |
| 2.11 | Credible interval and P(slope > 0 \| data) | Posterior density, shaded area |
| 2.12 | Side by side | Table: estimate, interval, what is random, how to read it |
| 2.13 | When do they disagree? | Small n + informative prior vs OLS |
| 2.14 | Hands-on 2 | Task list |

**Notebook 2 — `02_uncertainty_two_ways.ipynb`**
1. Re-simulate 1000 datasets, collect the slopes, and compare their SD with the reported SE.
2. Coverage experiment: 100 CIs, count how many miss the truth.
3. p-value by simulation, setting the true slope to 0.
4. PyMC model (code given, annotated line by line) and sampling (2 chains × 1000 draws, fast on Colab).
5. Check `az.summary` (r_hat), `az.plot_posterior`, and the spaghetti plot.
6. ✏️ Compute P(slope > 0) and P(slope > 1) from the samples.
7. Side-by-side table of the OLS and posterior summaries.
8. ✏️ Set n = 8 and use a strong prior: when do the two approaches diverge?

## Block 3 — More than one predictor (≈8 slides)

| # | Slide | Visual |
|---|---|---|
| 3.1 | Section header | — |
| 3.2 | Real data: KidIQ | Scatter coloured by `mom_hs` |
| 3.3 | A binary predictor: the slope is a difference in means | Two group means plus a connecting line |
| 3.4 | A continuous predictor, and centering for an interpretable intercept | Before/after centering |
| 3.5 | Both together: two parallel lines, "holding the other constant" | Parallel lines |
| 3.6 | Why the `mom_hs` coefficient drops from ≈12 to ≈6 | Correlated predictors diagram |
| 3.7 | Same model, both ways | Code side by side plus a forest plot (OLS CI vs posterior HDI) |
| 3.8 | Teaser: interactions | Non-parallel lines; "next steps" |
| 3.9 | Hands-on 3 | Task list |

**Notebook 3 — `03_multiple_predictors.ipynb`**
1. Load KidIQ from the repo's raw GitHub URL and explore it.
2. `kid_score ~ mom_hs` with `statsmodels`: interpret the coefficient.
3. `kid_score ~ mom_iq_c` (centered): interpret the intercept.
4. Both predictors with `statsmodels` **and** PyMC: compare in a table and a forest plot.
5. Plot the two parallel lines with posterior uncertainty bands.
6. ✏️ Explain why the `mom_hs` coefficient changed.
7. Bonus: add the interaction and see that the lines are no longer parallel.

Pacing: only the combined model is fitted in PyMC, to keep sampling time down for beginners.

## Outro slides
- Quiz slide (link and QR code).
- What we learned: 3 cards, one per block.
- Where to go next: *Regression and Other Stories* (Gelman, Hill & Vehtari), *Statistical Rethinking* (McElreath), PyMC examples gallery, Bambi for formula-style Bayesian models.
- Appendix (optional, for the curious): OLS closed form, OLS = MLE under Normal errors, Normal prior on the slope ≈ ridge penalty.

## Quiz — `quiz/index.html`

A single self-contained HTML file. 15 questions, 4 options each. Instant feedback on every answer with a 1–2 sentence explanation and a pointer to the slide/notebook section. Progress bar and final score, with the option to retry the missed questions. Some questions show a `statsmodels` table, an `az.summary` row or a small plot to interpret.

Draft questions (✔ = correct answer):

**Block 1 — Fitting a line**
1. In `time = 0.5 + 0.8·words`, what does 0.8 mean? ✔ Expected extra minutes per extra 100 words.
2. What does least squares minimise? ✔ The sum of squared vertical distances between points and the line.
3. A residual is… ✔ observed y − predicted y.
4. σ = 1.2 minutes means… ✔ a typical observation is about 1.2 min away from the line.
5. With `mom_iq` uncentered, the intercept is… ✔ the predicted score for a mother with IQ 0, which is not meaningful, hence centering.

**Block 2 — Uncertainty**

6. The standard error of the slope is… ✔ the spread of slope estimates across hypothetical repeated samples.
7. 95% CI = [0.6, 1.0]. Which statement is correct? ✔ "95% of intervals built this way contain the true slope." Distractor: "95% probability the slope is in [0.6, 1.0]", which is the *credible* interval reading.
8. p = 0.003 for the slope means… ✔ if the true slope were 0, data this extreme would be rare. Distractor: "0.3% chance the null is true".
9. In the Bayesian view, what is uncertain? ✔ The parameters; the observed data are fixed.
10. How do you get P(slope > 0) from posterior samples? ✔ The proportion of samples > 0.
11. With lots of data and weak priors, posterior mean vs OLS estimate? ✔ Nearly identical.
12. Multiplying the sample size by 4 makes the interval… ✔ about half as wide.
13. r_hat = 1.00 means… ✔ the chains agree, with no sign of sampling problems.

**Block 3 — Multiple predictors**

14. `kid_score = 26 + 6·mom_hs + 0.6·mom_iq`: what does 6 mean? ✔ The average difference between children whose mothers did/didn't finish high school, *comparing mothers with the same IQ*.
15. Why does the `mom_hs` coefficient drop from 12 to 6 when `mom_iq` is added? ✔ The two predictors are correlated; part of the high-school gap is explained by IQ.

**Not collected for now**: the quiz sends nothing anywhere. For the debrief, ask for a show of hands on the questions people found hardest. Live class results (e.g. an anonymous Google Sheet backend plus a dashboard page) can be added later; the quiz will be structured so that a "report this answer" hook can be plugged in without rewriting it.

## Design system (from the template)

- **Base file**: the template `.pptx` is loaded as the python-pptx base, so the theme, master and 16:9 format are kept. Its 13 slides are removed and new slides are built on the Blank layout with the template's components.
- **Title slide**: event line, then title "Session 1 - Linear regressions", then presenter and affiliation as in the template ("Nicolas Legrand", "Aarhus NLP – Center for Humanities Computing – Aarhus University").
- **Type**: Lao UI everywhere (kept as in the template). Titles 44 pt at (0.36″, 0.22″), subtitles 20 pt at (0.46″, 1.06″), body 14–16 pt, references 10.5 pt at the bottom. Consolas for code.
- **Colours**: text `#595959`, cards `#F2F2F2`, decorative bars `#EDEDED`. Accents: rose `#BC6D86` (dark `#855669`, tint `#DFAFBA`), blue `#92B0D0`, sage `#8BB57C` (tints `#D9EAD3` / `#B5D3AA`).
- **Perspective tags**: slides carry a neutral grey FREQUENTIST / BAYESIAN / BOTH VIEWS tag.
- **Components reused from the template**: title slide with the "token bar" motif, numbered step circles plus grey cards (as in the "Method" slide), quote/callout rounded box, two-column comparison.
- **Figures**: one matplotlib style (fonts, palette, no top/right spines, light grid) shared by `slides/figures.py` and the notebook setup cell, so slide and notebook plots look the same.
- **Equations**: few, rendered with matplotlib mathtext as high-res images in `#595959`.
- **Speaker notes** on every slide: talking points.

## Repository layout

```
README.md                         course overview, schedule, Colab badges
PLAN.md                           this file
data/kidiq.csv
slides/
  style.py                        palette + matplotlib style (single source of truth)
  figures.py                      generates slides/figures/*.png
  build_slides.py                 python-pptx → slides/session1_linear_regressions.pptx
notebooks/
  01_fitting_a_line.ipynb         exercise versions: outputs stripped, "✏️ Your turn" scaffolds
  02_uncertainty_two_ways.ipynb
  03_multiple_predictors.ipynb
  solutions/
    01_fitting_a_line_solutions.ipynb
    02_uncertainty_two_ways_solutions.ipynb
    03_multiple_predictors_solutions.ipynb
quiz/
  index.html                      the quiz (GitHub Pages)
```

- The solution notebooks are the single source. A small script derives the exercise versions by replacing cells tagged `solution` with their scaffold, so the two never drift apart.

- New dependencies: `statsmodels`, `pandas`, `ipywidgets`, and as dev-only: `python-pptx`, `qrcode`, `nbformat`, `nbclient`.
- New Makefile targets: `figures`, `slides`, `notebooks` and `check-notebooks` (executes the solution notebooks, then rebuilds the exercises).
- The existing `bayesian_intro.ipynb` and intro PDF stay as they are and are linked as optional pre-reading.

## Status (built 2026-11-10)

All materials are built; the event line uses the proposed default. Differences from the draft above:

- **Deck**: 50 slides instead of ~40. Added: "What a 95% CI is not" (five misreadings with corrections; sources: Wikipedia, ROS §1.5/§4.2/§4.4, Methods 2 week 3), the three animation slides, "Getting set up" (Colab steps + how the notebooks work),
  "Writing the model" (maths ↔ PyMC code, line by line), a break slide, and an appendix section
  divider. Slides carry a FREQUENTIST / BAYESIAN / BOTH VIEWS tag in the top-right corner.
- **Quiz**: the final 15 questions are in `quiz/index.html` (4 / 6 / 5 per block). Compared with
  the draft: the "×4 data → half width", "posterior ≈ OLS with lots of data" and r_hat questions
  were replaced by "prior vs data with 8 and 400 texts", a binary-predictor group-mean question,
  and an interaction question with a figure. Later, the "P(slope > 0.8) from posterior draws"
  and centering questions were replaced by "a CI that includes 0" and "a causal newspaper
  headline about the high-school coefficient".
- **Scientific review fixes (2026-11-10)**: "repeating the study" now keeps the same 40 texts
  and draws new reading times (`repeat_study()` in `slides/figures.py` and Notebook 2), so the
  simulated spread (0.054) matches the standard error from statsmodels (0.053); slides 17–22
  figures, animation 2, Notebook 2 and quiz Q5 were updated. Also: "statistical confounds" →
  "adjusting for a second predictor"; a note on impossible negative reading times (Normal
  errors); "rule out absurdly large values" on the priors slide; the texts are read carefully
  for a comprehension test (125 words/min), so the colleague's 250 words/min prior comes from a
  different situation. The deck was patched in place (it is edited by hand now, so
  `make slides` would overwrite those edits).
- **Notebook style**: Colab cannot import `slides/style.py`, so each notebook's setup cell
  repeats the palette inline.
- **Environment**: PyMC was upgraded to 6.4 (PyTensor 3.3, ArviZ 1.3): older PyTensor fails to
  compile on this Mac (Apple clang 21 rejects `-ld64`). The notebooks avoid version-specific
  ArviZ plotting and were verified with both PyMC 6.4/ArviZ 1.3 and PyMC 5.28/ArviZ 0.23.
  `bayesian_intro.ipynb` uses ArviZ 0.x functions (`az.plot_posterior`, `hdi_prob=`) that no
  longer exist in ArviZ 1.x.

### Before the class

1. Push to GitHub `master` so the Colab links and the KidIQ data URL resolve.
2. Enable GitHub Pages (deploy from `master`, root) so the quiz URL and QR code work.
3. Keep `notebooks/solutions/` out of the public repo until after class.
4. Open the deck in PowerPoint and skim it: the layout was checked with an approximate renderer,
   not PowerPoint itself.
5. Open `quiz/index.html` in a browser once.
6. Run `make check-notebooks` to execute the solution notebooks and store their outputs.

## Concept animations (built 2026-11-10)

Status: all three are built and rendered (`animations/renders/`), embedded in the deck (slides
10, 19 and 38, autoplay + loop) and shown as GIFs in the notebooks. Changes made during the build:

- **Dataset reseeded**: the main simulated dataset moved from seed 59 to **seed 226** (same true
  values 0.5 / 0.8 / 1.0), because seed 59 contained an impossible negative reading time
  (−1.06 min) that the plots' y-axes had hidden. The slides, notebook answers and quiz were
  updated. Larger simulated samples (n = 400 or 4000, and the σ = 3 exercise) can still contain
  a few negative times: the Normal model allows them. Animation 2 shows the points only of
  studies without one.
- **Animation 3 was redesigned** (30 s, two panels, live numbers): see its section below.
  It shows "controlling for IQ" as flattening the IQ slope in a score-vs-IQ scatterplot, with
  each child's adjustment carried over to the high-school comparison.
- **Rendering**: `make animations` (`animations/render.py`) uses `hyperframes render`;
  `--via-snapshots` captures the same frames with `hyperframes snapshot` + FFmpeg where a
  local render server is not allowed (this is how the committed renders were made).

The spec as planned:

One silent, looping animation per block that captures the block's main idea.

| | |
|---|---|
| Framework | **HyperFrames** (HeyGen, Apache 2.0): HTML/JS compositions with a seekable timeline, rendered to MP4 by headless Chrome + FFmpeg. Remotion was ruled out: its current terms exclude educational institutions from the free licence. |
| Rendering | Run locally (`npx hyperframes render`); this sandbox cannot launch Chrome. Needs Node 22+ and FFmpeg. |
| Format | 1920 × 1080 (full slide, 16:9), 30 fps, 25 s (animation 3: 30 s), H.264 MP4, seamless loop (each ends by fading back to its first frame). |
| Text | None, except axis titles and tick labels. Shapes only: lines, points, bells, brackets, markers. |
| Style | White background and the course palette; same fonts as the quiz. |
| Data | Precomputed in Python (`animations/make_data.py` → JSON) with the same seeds as the slides and notebooks, so every point and line matches the static figures. |
| In the deck | Each on its own full-bleed slide with no title, set to start automatically and loop. |
| In the notebooks | A lighter GIF version (960 × 540, ~12 fps) in a markdown cell of the matching section, loaded from the repo's raw GitHub URL so it shows in Colab and on GitHub. |

### 1. Where data come from (Block 1)

The model *y = a + b·x + ε* in motion, ending on least squares. Data: the 40 simulated texts (seed 226). Placed after the slide "Points don't sit on the line".

| Time | What happens |
|---|---|
| 0–3 s | Axes fade in; the true line (green, dashed) draws from left to right. |
| 3–6 s | Four bell curves (green, translucent) grow sideways along the line, showing the noise σ. |
| 6–15 s | The 40 points appear one by one on the true line at their own x, each sliding vertically to its observed y, as if drawn from the bell. |
| 15–17 s | The bells fade; only the green line and the grey points remain. |
| 17–20 s | The least-squares line (blue) sweeps in, close to but not on the green line. |
| 20–23 s | Residuals flash as thin grey vertical ticks from each point to the blue line, then fade. |
| 23–25 s | Everything fades back to the empty axes → loop. |

Notebook: Notebook 1, section 1 "The data".

### 2. Repeat the study (Block 2)

Where the standard error comes from: the spread of estimates over imagined repeated studies.

Layout: data panel (left, ~60%) and a histogram of estimated slopes (right). A green line marks the true slope 0.8 in both panels. Data: 200 simulated studies with fixed seeds.

| Time | What happens |
|---|---|
| 0–8 s | Studies 1–5, about 1.5 s each: 40 new grey points flash in, their least-squares line (blue) draws, the points fade, and the line stays as a faint trace. The study's slope drops as a small block onto the histogram. |
| 8–22 s | Studies 6–200, accelerating: the traces form a blue fan around the green line, and the histogram fills into a bell shape around 0.8. |
| 22–24 s | A double-headed bracket (±1 SD, no label) appears under the histogram: the standard error. |
| 24–25 s | Fade → loop. |

Placed after the slide "New data, new line" (before "The standard error"). Notebook: Notebook 2, section 2.

### 3. Holding the other constant (Block 3)

What "controlling for mother's IQ" does to the high-school gap (11.8 → 6.0 points). Data: KidIQ (434 children).

**As built (redesign):** 30 s; two panels sharing one vertical scale; live labels for the slope and the gaps (the only animation with numbers).

| Time | What happens |
|---|---|
| 0–6 s | Full width: two jittered columns of children (no / yes high school; grey / green), their mean dots, and the gap bracket (blue) labelled 11.8. |
| 6–9 s | The columns slide into a right-hand panel, and a mother's-IQ axis builds on the left. |
| 8.6–12 s | A copy of each child flies from its column to its place in the left scatterplot (score vs mother's IQ). Triangles mark each group's mean IQ (92 vs 102). |
| 12.6–15 s | The two-predictor model's IQ slope (0.56, high school held constant) draws through the pivot (mean IQ 100, mean score 86.8). A label shows "slope 0.56". A dashed ghost of the 11.8 bracket appears. |
| 15.6–21.6 s | **Controlling**: the slope rotates to 0.00 around IQ 100. Every child moves by −0.56 × (IQ − 100), in both panels at once. The group means slide (no: 77.5 → 82.1, yes: 89.3 → 88.1), and the gap label counts 11.8 → 6.0, exactly the `mom_hs` coefficient. |
| 21.6–27.4 s | Hold: the 6.0 bracket next to the dashed 11.8 ghost, sharing a base. |
| 27.4–30 s | Fade; the layout returns to the opening → seamless loop. |

Checked on rendered frames, within 1 px: final means 82.12 / 88.07, gap 5.95, ghost 11.77, slope line flat at 86.80.

Placed after the slide "Two predictors" (before "Why did it shrink?"). Notebook: Notebook 3, section 4.

### Files and build

```
animations/
  make_data.py                    seeds/data → */data.json
  01_where_data_come_from/        HyperFrames composition (index.html + data.json)
  02_repeat_the_study/
  03_holding_constant/
  renders/                        *.mp4 (deck) and *.gif (notebooks)
```

- `make animations` exports the data, renders the three MP4s, and converts them to GIFs with ffmpeg.
- `make slides` embeds the MP4s.
- PowerPoint playback (start automatically, loop until stopped) is set in the slide XML. If a PowerPoint version ignores it, it is two clicks in Playback.
