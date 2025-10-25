"""DrawFigure action implementation used across the tutorial."""

from __future__ import annotations

import ast
import re
from typing import Iterable, List, Optional

import matplotlib.pyplot as plt
from agentlite.actions.BaseAction import BaseAction


class DrawFigure(BaseAction):
    """Render a bar chart for provided names, values, and optional trust scores."""

    def __init__(self) -> None:
        action_name = "DrawFigure"
        action_desc = "Using this action to draw a bar figure for input statistics"
        params_doc = {
            "names": "the bar names. A list of names.",
            "values": "the bar value. A list of numbers.",
            "trust_scores": "(optional) trustworthiness scores for each value. A list of numbers between 0 and 1.",
        }
        super().__init__(action_name=action_name, action_desc=action_desc, params_doc=params_doc)

    def __call__(
        self,
        names: Iterable[str],
        values: Iterable[object],
        trust_scores: Optional[Iterable[object]] = None,
    ) -> str:
        norm_names = [str(n) for n in names]
        parsed_values, unresolved_token_found = self._normalize_values(values)
        parsed_trust_scores = self._normalize_trust_scores(trust_scores)
        self._plot(norm_names, parsed_values, parsed_trust_scores, unresolved_token_found)
        return "Successfully draw the bar figure!"

    def _normalize_values(self, values: Iterable[object]) -> tuple[List[float], bool]:
        parsed_values: List[float] = []
        unresolved_token_found = False
        for value in values:
            if isinstance(value, str) and re.search(r"[A-Za-z]", value) and not re.search(r"\d", value):
                unresolved_token_found = True
                parsed_values.append(0.0)
                continue
            number = self._to_number(value)
            if number is None:
                try:
                    number = float(str(value))
                except Exception:  # pragma: no cover - defensive for tutor usage
                    number = 0.0
            parsed_values.append(number)
        return parsed_values, unresolved_token_found

    def _normalize_trust_scores(self, trust_scores: Optional[Iterable[object]]) -> Optional[List[float]]:
        if trust_scores is None:
            return None
        parsed_scores: List[float] = []
        for score in trust_scores:
            try:
                parsed_scores.append(float(score))
            except (TypeError, ValueError):
                parsed_scores.append(0.0)
        return parsed_scores

    def _to_number(self, value: object) -> Optional[float]:
        if isinstance(value, (int, float)):
            return float(value)
        if isinstance(value, str):
            return self._parse_numeric_string(value)
        return None

    def _parse_numeric_string(self, raw: str) -> Optional[float]:
        text = raw.strip()
        lower = text.lower()
        multiplier = 1.0
        if "million" in lower:
            multiplier = 1e6
        elif "thousand" in lower:
            multiplier = 1e3
        digits = re.sub(r"[^0-9eE+\-.]+", "", text)
        if not digits:
            try:
                return float(ast.literal_eval(text)) * multiplier
            except Exception:  # pragma: no cover - defensive
                return None
        try:
            return float(digits) * multiplier
        except Exception:  # pragma: no cover - defensive
            return None

    def _plot(
        self,
        names: List[str],
        values: List[float],
        trust_scores: Optional[List[float]],
        unresolved_token_found: bool,
    ) -> None:
        min_len = min(len(names), len(values))
        if len(names) != len(values):
            names = names[:min_len]
            values = values[:min_len]
        print("DrawFigure: names=", names)
        print("DrawFigure: values=", values)
        if trust_scores:
            print("DrawFigure: trust_scores=", trust_scores)
        fig, ax = plt.subplots(figsize=(8, 5))
        bars = ax.bar(names, values, alpha=0.8)
        for index, (bar, value) in enumerate(zip(bars, values)):
            height = bar.get_height()
            label_text = self._format_value_label(value)
            ax.text(
                bar.get_x() + bar.get_width() / 2.0,
                height,
                label_text,
                ha="center",
                va="bottom",
                fontsize=10,
                fontweight="bold",
            )
            if trust_scores and index < len(trust_scores):
                trust_text = f"Trust: {trust_scores[index]:.2f}"
                ax.text(
                    bar.get_x() + bar.get_width() / 2.0,
                    height * 0.1,
                    trust_text,
                    ha="center",
                    va="bottom",
                    fontsize=8,
                    style="italic",
                    color="white",
                    bbox={"boxstyle": "round,pad=0.3", "facecolor": "black", "alpha": 0.6},
                )
        ax.set_xlabel("Values (unresolved tokens ignored)" if unresolved_token_found else "Region")
        ax.set_ylabel("Population")
        ax.set_title("Population Comparison with Trustworthiness Scores")
        plt.tight_layout()
        plt.show()

    def _format_value_label(self, value: float) -> str:
        if value >= 1e6:
            return f"{value / 1e6:.1f}M"
        if value >= 1e3:
            return f"{value / 1e3:.1f}K"
        return f"{value:.0f}"
