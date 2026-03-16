from __future__ import annotations

from typing import Mapping

import pandas as pd


def prettify_metric_name(metric_name: str) -> str:
    return metric_name.replace("_", " ").strip().title()


def build_report_dataframe(stats: Mapping[str, object]) -> pd.DataFrame:
    rows = []
    for metric, value in stats.items():
        rows.append({"Metric": prettify_metric_name(metric), "Value": value})
    return pd.DataFrame(rows)