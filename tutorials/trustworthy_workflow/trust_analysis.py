"""Utilities for trust score handling and population extraction."""

from __future__ import annotations

import ast
import csv
import os
from typing import Dict, Tuple

import pandas as pd

from .action_wikipediaSearch import extract_population, extract_population_values, print_population_debug

__all__ = [
    "load_trust_scores",
    "display_trust_score_report",
    "extract_population",
    "extract_population_values",
    "print_population_debug",
]


def load_trust_scores(csv_path: str) -> Tuple[Dict[str, float], Dict[str, dict]]:
    """Load trust scores and original search rows from the CSV log."""
    trust_scores: Dict[str, float] = {}
    search_rows: Dict[str, dict] = {}
    if not os.path.exists(csv_path):
        print("No trust score CSV found.")
        return trust_scores, search_rows
    with open(csv_path, newline="") as csv_file:
        reader = csv.DictReader(csv_file)
        for row in reader:
            if "Wikipedia_Search" not in row.get("action_name", ""):
                continue
            params = row.get("action_params", "")
            trust_score = row.get("trust_score", "")
            print(f"  {params}: Trust = {trust_score}")
            try:
                trust_scores[params] = float(trust_score)
            except (TypeError, ValueError):
                pass
            try:
                params_dict = ast.literal_eval(params)
            except (ValueError, SyntaxError):  # pragma: no cover - defensive
                continue
            if isinstance(params_dict, dict):
                query = params_dict.get("query", "")
                if query:
                    search_rows[query] = row
    return trust_scores, search_rows


def display_trust_score_report(csv_path: str) -> None:
    """Print the trust score CSV contents and a concise per-action summary."""
    print("📋 Full Trust Score CSV Contents:\n")
    print("=" * 120)
    if not os.path.exists(csv_path):
        print(f"❌ CSV file not found at: {csv_path}")
        return
    df = pd.read_csv(csv_path)
    pd.set_option("display.max_columns", None)
    pd.set_option("display.max_colwidth", None)
    pd.set_option("display.width", None)
    print(f"\nTotal rows: {len(df)}\n")
    print(df.to_string(index=False))
    print("\n" + "=" * 120)
    print("\n📊 Trust Score Summary by Action:\n")
    wiki_searches = df[df["action_name"] == "Wikipedia_Search"]
    if len(wiki_searches) == 0:
        print("No Wikipedia searches found in the CSV.")
        return
    for index, row in wiki_searches.iterrows():
        print(f"\n🔍 Search {index + 1}:")
        print(f"   Query: {row['action_params']}")
        print(f"   Trust Score: {row['trust_score']:.4f}")
        print(f"   Step: {row['step']}")
        raw_action = row.get("raw_action")
        if isinstance(raw_action, str):
            print(f"   Raw Action: {raw_action[:100]}...")
        finish_response = row.get("finish_response")
        if isinstance(finish_response, str):
            print(f"   Response: {finish_response[:200]}...")
