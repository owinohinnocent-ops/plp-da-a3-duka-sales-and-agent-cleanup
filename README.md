# Duka Sales Exploration and Agent Network Clean-Up

## Project overview
This repository contains two PLP data analytics engagements:
1. **Duka Electronics:** exploration of 1,000 synthetic orders generated with seed `2026`.
2. **Mobile money agent network:** audit and cleaning of a synthetic transaction extract generated with seed `44`.

## Key Duka findings
- Total sales revenue: **KES 71,792,500**.
- Highest-revenue branch: **Nairobi** (KES 26,106,100; 376 orders).
- Highest-revenue product: **Laptop** (KES 41,535,000).
- Highest-unit product: **Tablet** (691 units).
- Weekend orders: **277**; weekday orders: **723**.
- Best revenue month: **2026-04** (KES 13,518,300); worst: **2026-06** (KES 10,903,400); best month is **23.98%** higher relative to worst.

## Agent data-cleaning findings
- Raw transaction rows: **612**; unique transactions after deduplication: **600**.
- Duplicate transaction IDs removed: **12**.
- Missing/non-numeric amounts imputed: **20**.
- Transactions linked to unknown agent IDs: **7**.
- IQR outlier flags: **53**. Outliers are flagged, not deleted; KES 250,000 entries require source verification.

## Repository structure
```text
.
├── generate_data.py
├── cleaning_pipeline.py
├── duka_sales_exploration.ipynb
├── agent_cleanup.ipynb
├── requirements.txt
├── README.md
├── excel/
│   └── duka_branch_summary.xlsx
└── outputs/
    ├── premium_online_coast_capital.csv
    ├── agent_transactions_clean.csv
    └── agent_data_quality_audit.csv
```

## Reproduce the project
Use Python 3.10+ (Python 3.14 should also work) and install dependencies:

```bash
python -m pip install -r requirements.txt
python generate_data.py
```

Then open the two notebooks in Jupyter or VS Code and run all cells from top to bottom. Run them from the repository root so the relative file paths resolve. The generator creates the raw files `duka_sales.csv`, `agents.csv`, and `agent_transactions.csv`; these raw generated CSVs are intentionally not committed.

## Excel workbook
`excel/duka_branch_summary.xlsx` contains:
- A branch revenue summary using `SUMIFS`.
- A region lookup using `XLOOKUP`.
- A branch-by-channel revenue cross-tab using `SUMIFS` formulas.

The branch-by-channel sheet is a formula-driven pivot-style summary. If the assessor specifically requires a native Excel PivotTable object, open the workbook, select the **Sales Data** table, choose **Insert → PivotTable**, put `branch` in Rows, `channel` in Columns and `revenue` in Values (Sum). Refresh formulas in Excel and compare the branch grand total with the pandas notebook result.

## Cleaning decisions
- Duplicate `txn_id` values are removed, keeping the first occurrence.
- Transaction types are standardised to `Deposit` and `Withdrawal`; unrecognised values are retained as `Unknown` for review.
- Missing or non-numeric amounts are median-imputed within transaction type and flagged in `amount_imputed`.
- IQR outliers are flagged in `is_outlier`, not deleted. KES 250,000 values should be investigated against source records and applicable transaction limits.
- Transactions are left-joined to the agent register. Unknown agent IDs are preserved and assigned county `Unknown`.

## GitHub submission
Commit the source files, notebooks, `excel/` and `outputs/`. Do **not** commit the raw generated files `duka_sales.csv`, `agents.csv`, or `agent_transactions.csv`.
