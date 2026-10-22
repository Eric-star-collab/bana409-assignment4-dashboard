# Northstar Team — Weekly Sales Review

This is my individual dashboard project for BANA409 Assignment 4. Northstar is the project/team label, not a claim of membership in an actual class group. The dashboard is designed around one recurring decision: which store and product line the regional sales manager should investigate at the Monday sales review.

## Step 1 — Dataset and decision-maker

- Source: [Supermarket Sales Dataset by Fares Ashraf on Kaggle](https://www.kaggle.com/datasets/faresashraf1001/supermarket-sales), version 2, updated September 19, 2024. The downloaded file is `SuperMarket Analysis.csv`; it is included unchanged as `data/supermarket_sales.csv`.
- The Kaggle page describes historical supermarket-chain transactions in Myanmar. There are 1,000 rows and 17 columns, covering January 1–March 30, 2019, with one invoice transaction per row and three city locations. The CSV is about 140 KB, so no sampling or aggregation was necessary for the committed source.
- Collection procedures and independent real-versus-synthetic provenance are not documented sufficiently to verify authenticity. I treat this as a historical demonstration rather than audited business evidence. The source page lists Apache 2.0; see `DATA_SOURCE.md` and `LICENSE-DATA.txt`.
- The one intended viewer is a regional supermarket sales manager. This person can ask a store manager to investigate a decline, review promotion execution, and check whether a product line was unavailable. The data cannot support automatic stock replenishment because inventory and supplier lead times are absent.

## Step 2 — Why a dashboard

The manager reviews it every Monday morning, after the most recent full Sunday has closed. If the manager sees weekly sales fall more than 15% against the preceding complete week, they will contact the selected store manager that day, identify the product lines contributing to the decline, and request an availability/promotion check before proposing a response.

Without a consolidated view, a plausible current workflow is downloading three store spreadsheets and manually reconciling date ranges, tax treatment and product categories. That workflow creates a risk of comparing a partial week with a complete one. This is a design assumption about the intended user, not an observed time-and-motion study; I do not assign invented dollar savings to it.

A weekly email could communicate the all-store headline, but the follow-up question requires switching stores and comparing product-line changes without asking an analyst for another report. That repeated drill-down justifies a small dashboard. An alert is appropriate for a threshold breach, but it should link to the dashboard for diagnosis; it does not replace the comparative view.

## Step 3 — What matters and page order

I explored shape, dtypes, missing values, duplicates, amount distributions, weekly sales, category sales and arithmetic identities in the executed `dashboard-eda.ipynb`.

The top row contains exactly three KPIs, side by side using `st.columns` and `st.metric`:

1. Tax-inclusive sales in USD, with the change against the prior complete week. This identifies whether a follow-up is needed.
2. Unique invoice count. This separates a transaction-volume problem from a basket-size problem.
3. Average transaction amount, calculated as sales divided by transaction count. This provides the other half of that diagnosis.

The middle contains exactly two charts: the most recent eight complete weekly sales totals, and each product line's dollar contribution to the week-over-week change. The trend distinguishes a persistent decline from a one-week fluctuation; the category comparison helps assign an investigation. Dollar changes remain defined even when a previous category total is zero.

The two filters are store/city and complete week. The regional manager needs the former to contact the responsible store and the latter to review a particular weekly meeting. Product, payment, gender and battery-like numeric sliders would add complexity without helping this decision. The bottom contains a collapsed transaction audit table and CSV download so the store manager can locate the invoices behind a disputed number.

I deliberately cut payment-method charts: payment-processing policy is outside this sales-review decision. I also cut gender/customer-type breakdowns because this snapshot provides no campaign exposure or credible incremental effect, so those splits would not identify a defensible action. Finally, I excluded the attractive-looking 'gross income' KPI because its values equal the tax field, making a profit label misleading.

Important limitations and handling:

- `Sales` includes 5% tax; the app labels this explicitly. The identities `Sales = cogs + Tax 5%` and `gross income = Tax 5%` hold, so I do not interpret the latter as profit.
- `Branch` labels in this particular version are Alex/Cairo/Giza, while `City` lists Myanmar cities. I retain the raw file unchanged, use City as the store selector, and disclose the inconsistent label semantics.
- All rows have complete fields and unique invoice IDs in this snapshot. That does not establish that all business transactions or closure days were recorded. A date without a recorded invoice cannot be proved to be a genuine zero-sales day.
- The first and last calendar weeks are partial. Only weeks fully within the observed date span are selectable, and the first complete week has no complete prior-week comparator. Its change chart and warning are suppressed. No artificial zero week is added.
- Sales declines are descriptive; without inventory, weather or promotion data, the dashboard cannot identify their cause.

Top-to-bottom sketch: title and viewer/purpose → period/refresh disclosure → store/week scope → three headline metrics → review signal → weekly trend and product-line change → collapsed transaction evidence → source notes. The manager sees the decision signal before detail; the latter remains available without crowding the first screen.

## Step 4 — Refresh, review and action

The production data would refresh nightly from the point-of-sale system after all stores close. The manager reviews the most recent complete week on Monday; nightly refresh and weekly review are different requirements. Real-time refresh would add operational work without changing the weekly follow-up cadence.

The monitored measure is full-week sales for a store compared with the previous full week. A fall exceeding 15% triggers a same-day call, after checking transaction volume and category contributions. The 15% threshold is a provisional operating rule, not a threshold optimized or statistically validated on these three months; a production pilot should calibrate it for holidays and normal variability.

A one-day delay on Monday can postpone a follow-up; a week of stale data can cause the manager to address a decline that has already reversed or miss a persistent problem. I cannot quantify that cost from this dataset. In production the app should show the latest successful source-load timestamp and a stale-data status after a missed nightly load. The current app clearly states that its CSV is a frozen Kaggle snapshot and does not pretend to refresh live.

## Step 5 — Run and deploy

The project includes `pyproject.toml`, a committed `uv.lock`, and `.python-version`, following the course's uv project workflow. It targets Python 3.14 as required by the exercise.

```bash
uv sync
uv run streamlit run app.py
```

Alternatively: `python -m pip install -r requirements.txt` then `python -m streamlit run app.py`.

Create a **public repository under your own GitHub account**, upload this folder's contents at its root, then open [Streamlit Community Cloud](https://share.streamlit.io/), choose the repository's `main` branch and `app.py`, and set Python **3.14** under Advanced settings. Deploy from your own Streamlit account. Copy both verified URLs into the first markdown cell of `phone-trade-in.ipynb`. Read and adapt this README to reflect your own understanding before submitting; do not claim classroom teamwork or personal decisions you cannot explain.

## Verification

`dashboard-eda.ipynb` contains executed source checks and charts. Local automated Streamlit AppTest checks initial rendering, a city/week selection, and the earliest-week no-comparator state. The app does not train models or need any credentials at runtime.
