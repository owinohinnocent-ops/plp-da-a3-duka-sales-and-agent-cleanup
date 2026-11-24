"""Reproducible cleaning pipeline for the mobile-money agent dataset."""

import numpy as np
import pandas as pd


def clean_agent_data(txns, agents):
    """
    Clean mobile-money transactions and join the agent register.

    Parameters
    ----------
    txns : pandas.DataFrame
        Raw transaction extract.
    agents : pandas.DataFrame
        Agent register.

    Returns
    -------
    clean_df : pandas.DataFrame
        Deduplicated, standardised and enriched transactions.
    log : pandas.DataFrame
        Cleaning actions and affected-row counts.
    """
    clean = txns.copy()
    register = agents.copy()
    log_rows = []

    def record(issue, dimension, column, affected):
        log_rows.append({
            "issue": issue,
            "dimension": dimension,
            "column": column,
            "rows_affected": int(affected)
        })

    # Uniqueness: txn_id is the transaction key; retain first occurrence.
    duplicate_mask = clean.duplicated(subset=["txn_id"], keep="first")
    record("Duplicate transaction IDs removed", "Uniqueness", "txn_id", duplicate_mask.sum())
    clean = clean.loc[~duplicate_mask].copy()

    # Consistency: normalise whitespace/case and map to the two valid categories.
    original_type = clean["txn_type"].copy()
    norm_type = original_type.astype("string").str.strip().str.casefold()
    type_map = {"deposit": "Deposit", "withdrawal": "Withdrawal"}
    clean["txn_type"] = norm_type.map(type_map)
    invalid_type = clean["txn_type"].isna()
    record("Missing or unrecognised transaction type", "Consistency", "txn_type", invalid_type.sum())
    # The supplied generator only contains valid categories after normalisation.
    # If future invalid types occur, retain the row and label it for review.
    clean.loc[invalid_type, "txn_type"] = "Unknown"

    # Validity/completeness: numeric coercion, then median imputation within type.
    amount_raw = clean["amount"].copy()
    amount_num = pd.to_numeric(amount_raw, errors="coerce")
    invalid_amount = amount_num.isna()
    record("Missing or non-numeric amount values", "Completeness/Validity", "amount", invalid_amount.sum())
    clean["amount"] = amount_num
    clean["amount_imputed"] = clean["amount"].isna()
    medians = clean.groupby("txn_type")["amount"].transform("median")
    overall_median = clean["amount"].median()
    clean["amount"] = clean["amount"].fillna(medians).fillna(overall_median)

    # IQR outlier flags: flag but do not delete extreme transactions.
    q1 = clean["amount"].quantile(0.25)
    q3 = clean["amount"].quantile(0.75)
    iqr = q3 - q1
    lower = q1 - 1.5 * iqr
    upper = q3 + 1.5 * iqr
    clean["is_outlier"] = (clean["amount"] < lower) | (clean["amount"] > upper)
    record("IQR-flagged suspicious amounts", "Validity/Accuracy", "amount", clean["is_outlier"].sum())
    record("KES 250,000 values retained for verification", "Accuracy", "amount", (clean["amount"] == 250000).sum())

    # Parse both ISO and slash-separated dates.
    raw_dates = clean["txn_date"].astype("string")
    parsed = pd.to_datetime(raw_dates, format="mixed", errors="coerce")
    bad_dates = parsed.isna()
    record("Unparseable transaction dates", "Validity", "txn_date", bad_dates.sum())
    clean["txn_date"] = parsed

    # Merge register using a left join so no transaction disappears.
    clean = clean.merge(register[["agent_id", "county"]], on="agent_id", how="left", validate="many_to_one")
    unknown = clean["county"].isna()
    record("Transactions linked to unknown agent IDs", "Completeness", "agent_id/county", unknown.sum())
    clean["county"] = clean["county"].fillna("Unknown")

    # ISO date output is represented as datetime in-memory and ISO on CSV export.
    clean["txn_date"] = pd.to_datetime(clean["txn_date"])
    clean = clean.sort_values(["txn_date", "txn_id"]).reset_index(drop=True)
    log = pd.DataFrame(log_rows, columns=["issue", "dimension", "column", "rows_affected"])
    return clean, log
