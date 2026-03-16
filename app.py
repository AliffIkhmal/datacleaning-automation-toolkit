from __future__ import annotations

from io import StringIO

import pandas as pd
import streamlit as st

from core.cleaner_router import get_cleaner, get_tool_options
from core.schema_detector import detect_schema


PREVIEW_ROW_LIMIT = 100


@st.cache_data(show_spinner=False)
def load_csv(uploaded_file: bytes) -> pd.DataFrame:
    return pd.read_csv(StringIO(uploaded_file.decode("utf-8")))


def render_schema_summary(schema: dict[str, object]) -> None:
    schema_df = pd.DataFrame(
        {
            "Schema Type": [
                "Numeric Columns",
                "Categorical Columns",
                "Potential Date Columns",
                "Identifier Columns",
            ],
            "Columns": [
                ", ".join(schema["numeric_columns"]) or "None detected",
                ", ".join(schema["categorical_columns"]) or "None detected",
                ", ".join(schema["potential_date_columns"]) or "None detected",
                ", ".join(schema["identifier_columns"]) or "None detected",
            ],
        }
    )
    st.dataframe(schema_df, use_container_width=True, hide_index=True)


def main() -> None:
    st.set_page_config(page_title="Data Automation Toolkit", layout="wide")
    st.title("Data Automation Toolkit")
    st.caption(
        "Select an industry cleaner, inspect detected schema, run automated cleaning, and download the output."
    )

    tool_options = get_tool_options()
    selected_tool = st.selectbox("Select a tool", options=tool_options)
    cleaner = get_cleaner(selected_tool)

    st.info(cleaner.description)
    if not cleaner.implemented:
        st.warning(
            "This cleaner is scaffolded for future expansion. Running it returns the original dataset with a placeholder report."
        )

    uploaded_file = st.file_uploader("Upload CSV dataset", type=["csv"])
    if uploaded_file is None:
        st.info("Upload a CSV file to begin.")
        return

    try:
        raw_df = load_csv(uploaded_file.getvalue())
    except Exception as error:
        st.error(f"Failed to read CSV file: {error}")
        return

    if raw_df.empty:
        st.error("The uploaded dataset is empty.")
        return

    schema = detect_schema(raw_df)

    preview_column, schema_column = st.columns([1.8, 1.2])
    with preview_column:
        st.subheader(f"Dataset Preview (first {PREVIEW_ROW_LIMIT} rows)")
        st.dataframe(raw_df.head(PREVIEW_ROW_LIMIT), use_container_width=True)

    with schema_column:
        st.subheader("Detected Schema")
        if schema["detected_industry"]:
            st.success(f"Detected industry: **{schema['detected_industry']}**")
        render_schema_summary(schema)

    st.subheader("Suggested Cleaning Rules")
    suggested_rules_df = pd.DataFrame(schema["suggested_rules"])
    if suggested_rules_df.empty:
        st.info("No column-name rule suggestions were generated for this dataset.")
    else:
        st.dataframe(suggested_rules_df, use_container_width=True, hide_index=True)

    if st.button("Run Cleaning", type="primary"):
        try:
            result = cleaner.run(raw_df)
        except Exception as error:
            st.error(f"Cleaning failed: {error}")
            return

        st.success("Cleaning completed.")

        for message in result.messages:
            st.info(message)

        st.subheader("Cleaning Report")
        st.dataframe(result.report_df, use_container_width=True, hide_index=True)

        if result.issues_df is not None and not result.issues_df.empty:
            st.subheader("Detected Issues")
            st.dataframe(result.issues_df, use_container_width=True)

        st.subheader(f"Cleaned Dataset Preview (first {PREVIEW_ROW_LIMIT} rows)")
        st.dataframe(result.cleaned_df.head(PREVIEW_ROW_LIMIT), use_container_width=True)

        st.download_button(
            label="Download Cleaned Dataset",
            data=result.cleaned_df.to_csv(index=False).encode("utf-8"),
            file_name=result.output_filename,
            mime="text/csv",
        )


if __name__ == "__main__":
    main()
