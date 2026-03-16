from __future__ import annotations

from typing import Dict

import pandas as pd

from tools.base import BaseCleaner, CleaningResult
from tools.ecommerce.ecommerce_cleaner import EcommerceCleaner
from tools.hr_cleaning.hr_cleaner import HRCleaner
from tools.logistics.logistics_cleaner import LogisticsCleaner
from tools.manufacturing.manufacturing_cleaner import ManufacturingCleaner
from tools.sales.sales_cleaner import SalesCleaner


TOOL_REGISTRY: Dict[str, BaseCleaner] = {
    "HR Data Cleaner": HRCleaner(),
    "Sales Data Cleaner": SalesCleaner(),
    "Manufacturing Data Cleaner": ManufacturingCleaner(),
    "Logistics Data Cleaner": LogisticsCleaner(),
    "E-commerce Data Cleaner": EcommerceCleaner(),
}


def get_tool_options() -> list[str]:
    return list(TOOL_REGISTRY.keys())


def get_cleaner(selected_tool: str) -> BaseCleaner:
    try:
        return TOOL_REGISTRY[selected_tool]
    except KeyError as error:
        available = ", ".join(TOOL_REGISTRY.keys())
        raise ValueError(
            f"Unsupported tool '{selected_tool}'. Available tools: {available}."
        ) from error


def run_cleaner(selected_tool: str, df: pd.DataFrame) -> CleaningResult:
    cleaner = get_cleaner(selected_tool)
    return cleaner.run(df)