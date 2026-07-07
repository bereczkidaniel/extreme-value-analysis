# Extreme Value Analysis and Portfolio Optimization for US Equities

A reproducible study of tail risk and pair-wise portfolio construction on a
sector-diversified basket of ten US large-cap stocks. The workflow fits
$\alpha$-stable, GEV and GPD distributions to the return / loss series,
compares five copula families for bivariate dependence, and combines the
two into copula-with-GPD-margins Monte Carlo estimates of joint tail risk.
Portfolio construction uses `tseries::portfolio.optim` (minimum variance)
and `fPortfolio::minriskPortfolio` (minimum 10%-tail CVaR); the PSY test
from `psymonitor` screens the selected pair for explosive price episodes.

Data comes from Yahoo Finance via [`yfinance`](https://pypi.org/project/yfinance/);
the rest of the analysis is R Markdown.

---

## Contents

- [Basket](#basket)
- [Methods](#methods)
- [Sample outputs](#sample-outputs)
- [Repository layout](#repository-layout)
- [How to run](#how-to-run)
- [Notes on runtime and package availability](#notes-on-runtime-and-package-availability)
- [License](#license)

---

## Basket

Ten large-cap US equities, two per sector across five sectors:

| Sector | Ticker 1 | Ticker 2 |
|---|---|---|
| Technology | AAPL (Apple) | MSFT (Microsoft) |
| Financials | JPM (JPMorgan Chase) | BAC (Bank of America) |
| Healthcare | JNJ (Johnson & Johnson) | PFE (Pfizer) |
| Energy | XOM (ExxonMobil) | CVX (Chevron) |
| Consumer Staples | PG (Procter & Gamble) | KO (Coca-Cola) |

The default date range is **2015-01-01 to 2024-12-31** (~10 years of daily
observations). Both the ticker list and the date range are configurable at
the top of `data_download.py`.

---

## Methods

**Univariate tail modelling.**

- $\alpha$-stable distribution fitting via `stableFit` (McCulloch's
  quantile estimator and MLE).
- Generalized extreme value (GEV) distribution fitted to block maxima of
  losses via `blockMaxima` + `gev.fit`; block-size sensitivity is checked
  across weekly / monthly / quarterly windows.
- Generalized Pareto (GPD) distribution fitted via the Peaks-Over-Threshold
  method; threshold selection uses the mean residual life plot
  (`evd::mrlplot`) and the threshold-choice plot (`evd::tcplot`).
- Goodness of fit: Michael's stabilized PP-plot, chi-squared test with
  parameter-count-corrected degrees of freedom, the built-in `ks.test`,
  and `gev.diag` / `gpd.diag` diagnostic panels.
- Value-at-Risk at the 99% level from four models (empirical, stable, GEV,
  GPD) with 95% bootstrap confidence intervals via `boot::boot` and
  `boot::boot.ci`; profile-likelihood intervals illustrated via `gev.prof`.

**Bivariate analysis.**

- Pair-wise portfolio construction across all 28 pairs of the remaining
  eight candidates after dropping the two riskiest stocks:
  - minimum-variance portfolio via `tseries::portfolio.optim`,
  - minimum 10%-tail CVaR portfolio via `fPortfolio::minriskPortfolio`
    (Rglpk solver).
- Bivariate extreme-value model (`fbvevd`) with symmetric logistic
  dependence on Fréchet-transformed margins; nonparametric Pickands
  dependence function (`abvnonpar`).
- Copula fits and comparison across Gaussian, Student-$t$, Gumbel, Clayton,
  and Frank families (`fitCopula`, `gofCopula` with Kendall-process
  $S_n$-statistic, Rosenblatt transform via `rtrafo`).
- Joint tail risk: probability of simultaneous VaR$_{99}$ breach, portfolio
  VaR$_{95/99/99.5}$, and CVaR$_{90}$ via $10^5$-sample Monte Carlo from
  the fitted copula with piecewise (empirical + GPD tail) marginals.

**Bubble diagnostic.** PSY (Phillips-Shi-Yu) test on the price series of
the selected pair with `psymonitor::PSY` and wild-multiplier bootstrap
critical values via `cvPSYwmboot`.

**Stability check.** All univariate fits are recomputed on the second half
of the sample; Kendall's $\tau$ measures the persistence of the risk
ranking.

---

## Sample outputs

*The figures below are illustrative samples generated from synthetic data
with realistic properties (heavy tails, volatility clustering,
cross-sectional correlation). They are overwritten by real analysis output
whenever `stock_analysis.Rmd` is knit, via the `export-figures` chunk at
the end of the report.*

### 1. Log-return time series

![Log-return time series for all ten stocks](figures/returns_timeseries.png)

Standard equity-return stylized facts are visible: approximately zero
mean, heavy tails, and volatility clustering. Empirical excess kurtosis is
well above zero for every stock.

### 2. Stable distribution fits

![Return histograms with fitted stable density](figures/stable_fits.png)

The fitted $\alpha$-stable density (blue) matches the body of the
empirical distribution; the tail behaviour drives the risk parameters
$\alpha$ and $\beta$ that feed the risk ranking.

### 3. Goodness of fit -- Michael's stabilized PP-plot

![Michael stabilized PP-plot](figures/michael_pp.png)

Under a correct model the plotted points lie on the diagonal. Small
deviations at the tail ends are consistent with sampling variability.

### 4. GPD threshold selection

![Threshold-choice plot](figures/tcplot.png)

`evd::tcplot` shows the fitted GPD shape $\xi$ and modified scale
$\sigma^\ast$ as functions of the threshold with 95% confidence bands. The
threshold is set at the 95% empirical quantile where both parameters
stabilize.

### 5. Copula comparison

![Empirical pseudo-observations vs simulated copulas](figures/copula_scatter.png)

The upper-left panel shows the empirical pseudo-observations for the
selected pair; the remaining panels show samples drawn from each fitted
copula. The best model is selected by the `gofCopula` p-value.

### 6. Portfolio frontier and pair selection

![Pairwise minimum-variance portfolios](figures/portfolio_frontier.png)

Every pair of the eight remaining stocks defines a small efficient
frontier (grey); the minimum-variance point of each pair is marked in
blue, individual stocks in red. The selected pair (smallest 10%-tail
CVaR of the CVaR-optimal portfolio) is highlighted in the report.

### 7. PSY bubble test

![PSY bubble test statistics for the selected pair](figures/psy_test.png)

Recursive BSADF statistic against the 95% wild-multiplier bootstrap
critical value. Windows in which BSADF exceeds the critical value indicate
explosive price behaviour compatible with a bubble.

---

## Repository layout

```
.
├── README.md                    # This file
├── LICENSE                      # MIT
├── requirements.txt             # Python dependencies
├── .gitignore
├── data_download.py             # yfinance downloader -> data/stock_prices.csv
├── generate_sample_figures.py   # Creates illustrative README figures
├── stock_analysis.Rmd           # Main analysis (R Markdown)
├── data/
│   └── stock_prices.csv         # (gitignored; produced by data_download.py)
└── figures/                     # Figures embedded in README + rendered report
    ├── returns_timeseries.png
    ├── stable_fits.png
    ├── michael_pp.png
    ├── tcplot.png
    ├── copula_scatter.png
    ├── portfolio_frontier.png
    └── psy_test.png
```

---

## How to run

**1. Clone and install Python dependencies.**

```bash
git clone <your-fork-url>
cd <repo-name>
python -m pip install -r requirements.txt
```

**2. Download prices.**

```bash
python data_download.py
```

This writes `data/stock_prices.csv` with adjusted daily closes for the ten
tickers over the configured date range.

**3. Install R packages.** In an R console:

```r
need <- c(
  "fBasics", "stabledist", "fExtremes", "evir", "ismev", "evd",
  "POT", "gsl", "copula", "boot", "tseries", "fPortfolio", "Rglpk",
  "timeSeries", "knitr", "rmarkdown"
)
install.packages(setdiff(need, rownames(installed.packages())))
```

The `psymonitor` package is archived on CRAN, install it from the archive:

```r
install.packages(
  "https://cran.r-project.org/src/contrib/Archive/psymonitor/psymonitor_0.0.2.tar.gz",
  repos = NULL, type = "source"
)
```

Note the system dependency of `copula`:

- Linux (Debian/Ubuntu): `sudo apt-get install libgsl-dev`
- macOS (Homebrew): `brew install gsl`
- Windows: the CRAN binary of `gsl` bundles the library; no extra step
  needed. If Rtools is missing when installing `psymonitor`, download it
  from <https://cran.rstudio.com/bin/windows/Rtools/>.

**4. Knit the report.** In RStudio, open `stock_analysis.Rmd` and click
**Knit**, or from a terminal:

```bash
Rscript -e 'rmarkdown::render("stock_analysis.Rmd")'
```

This produces `stock_analysis.html` and refreshes the PNGs in `figures/`.

---

## Notes on runtime and package availability

- The full knit takes roughly **10-20 minutes** on a modern laptop; chunk
  caching (`cache=TRUE`) makes subsequent knits fast.
- The slowest operations are (i) `stableFit(..., type="mle")` for each of
  the ten return series and (ii) `cvPSYwmboot` for the two selected
  stocks. Both are cached.
- To make development faster you can:
  - lower `B_boot` from 200 to e.g. 100 for the VaR bootstrap intervals,
  - lower `N_gof` from 100 to e.g. 50 for `gofCopula`,
  - lower `nboot` from 99 to e.g. 50 for the PSY test critical values,
  - switch `useParallel = FALSE` to `TRUE` in the PSY call
    (already the default in this repository).
- Rendering under `pdf_document` requires `latex_engine: xelatex` because
  the document contains characters (dashes, accented names) that
  `pdflatex` does not handle out of the box. HTML output is the default
  and has no Unicode issues.

---

## License

MIT -- see `LICENSE`.
