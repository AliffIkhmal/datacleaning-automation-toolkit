from __future__ import annotations

from abc import ABC, abstractmethod
from dataclasses import dataclass, field

import pandas as pd


@dataclass
class CleaningResult:
    cleaned_df: pd.DataFrame
    report_df: pd.DataFrame
    stats: dict[str, object]
    issues_df: pd.DataFrame | None = None
    output_filename: str = "cleaned_dataset.csv"
    messages: list[str] = field(default_factory=list)


class BaseCleaner(ABC):
    tool_name: str = "Generic Cleaner"
    description: str = "Generic data cleaning tool."
    implemented: bool = False

    @abstractmethod
    def run(self, df: pd.DataFrame) -> CleaningResult:
        raise NotImplementedError