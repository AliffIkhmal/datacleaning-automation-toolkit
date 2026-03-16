from __future__ import annotations

import pandas as pd

from tools.hr_cleaning.cleaner import clean_hr_data
from tools.hr_cleaning.report import generate_cleaning_report
from tools.base import BaseCleaner, CleaningResult


class HRCleaner(BaseCleaner):
    tool_name = "HR Data Cleaner"
    description = "Uses the existing HR cleaning rules for employee-oriented datasets."
    implemented = True

    def run(self, df: pd.DataFrame) -> CleaningResult:
        cleaned_df, stats, outliers_df = clean_hr_data(df)
        report_df = generate_cleaning_report(stats)
        messages = []
        if not outliers_df.empty:
            messages.append("Salary outliers were detected and handled using the existing HR rules.")

        return CleaningResult(
            cleaned_df=cleaned_df,
            report_df=report_df,
            stats=stats,
            issues_df=outliers_df,
            output_filename="cleaned_hr_dataset.csv",
            messages=messages,
        )