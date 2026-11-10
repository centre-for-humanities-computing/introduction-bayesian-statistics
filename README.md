# Introduction to Bayesian Statistics

Teaching material from the Center for Humanities Computing, Aarhus University.

## Session 1 - Linear regressions

A hands-on class on linear regression from a **frequentist** and a **Bayesian** perspective,
for participants new to statistics and coding.

| | Block | Notebook |
|---|---|---|
| | Welcome and setup | |
| 1 | Drawing a line through data: least squares, maximum likelihood | [![Open In Colab](https://colab.research.google.com/assets/colab-badge.svg)](https://colab.research.google.com/github/centre-for-humanities-computing/introduction-bayesian-statistics/blob/master/notebooks/01_fitting_a_line.ipynb) Fitting a line |
| 2 | How sure are we? Standard errors, confidence intervals and p-values; priors, posteriors and credible intervals | [![Open In Colab](https://colab.research.google.com/assets/colab-badge.svg)](https://colab.research.google.com/github/centre-for-humanities-computing/introduction-bayesian-statistics/blob/master/notebooks/02_uncertainty_two_ways.ipynb) Uncertainty, two ways |
| | Break | |
| 3 | More than one predictor: binary predictors, centering, interpretation | [![Open In Colab](https://colab.research.google.com/assets/colab-badge.svg)](https://colab.research.google.com/github/centre-for-humanities-computing/introduction-bayesian-statistics/blob/master/notebooks/03_multiple_predictors.ipynb) More than one predictor |
| | [Quiz](https://centre-for-humanities-computing.github.io/introduction-bayesian-statistics/quiz/) (15 questions, instant corrections) and debrief | |

### Materials

| Path | Content |
|---|---|
| `slides/session1_linear_regressions.pptx` | Slide deck (50 slides incl. 3 animation slides, speaker notes) |
| `notebooks/*.ipynb` | Exercise notebooks for participants |
| `notebooks/solutions/*_solutions.ipynb` | Solution notebooks (the source of the exercise versions) |
| `quiz/index.html` | Self-contained quiz; nothing is recorded |
| `animations/` | Three silent, looping concept animations (one per block), made with [HyperFrames](https://github.com/heygen-com/hyperframes) |
| `animations/renders/` | Rendered animations: MP4 (embedded in the deck) and GIF (shown in the notebooks) |
| `data/kidiq.csv` | KidIQ data from *Regression and Other Stories* |

### Running locally

```bash
make jupyterlab
```

This requires PyMC ≥ 6.4 (PyTensor ≥ 3.3) on recent macOS: older PyTensor versions pass the
`-ld64` linker flag, which Apple clang 21 no longer accepts. The notebooks also run with
PyMC 5 / ArviZ 0.x, which some Colab images still ship.

### References

- Gelman, A., Hill, J., & Vehtari, A. (2020). *Regression and Other Stories*. Cambridge University Press.
- McElreath, R. (2020). *Statistical Rethinking* (2nd ed.). CRC Press.
