# Automated HR Data Cleaning & Preprocessing System

## Suggested Project Structure

```text
HRdata_cleaning/
├─ app.py
├─ requirements.txt
├─ README.md
└─ hr_cleaning/
   ├─ __init__.py
   ├─ cleaner.py
   └─ report.py
```

## Basic Architecture Diagram (Explanation)

```text
[User]
   │ Upload CSV / Click "Run Cleaning"
   ▼
[Streamlit UI: app.py]
   │
   ├─ Reads CSV with pandas
   ├─ Shows preview + detected dtypes
   ├─ Calls cleaning service
   ▼
[Data Cleaning Module: cleaner.py]
   │
   ├─ Remove duplicates
   ├─ Fill missing values (median/mode)
   ├─ Correct negatives (Age, Salary, Overtime_Hours)
   ├─ Standardize categorical values
   ├─ Convert Hire_Date to YYYY-MM-DD
   └─ Detect Salary outliers (IQR)
   │
   ▼
[Reporting Module: report.py]
   └─ Builds summary metrics table
   │
   ▼
[Streamlit UI: app.py]
   ├─ Displays cleaning report
   ├─ Displays outlier rows
   └─ Provides cleaned CSV download
```

## Run Locally

1. Install dependencies:
   ```bash
   pip install -r requirements.txt
   ```
2. Start app:
   ```bash
   streamlit run app.py
   ```

## Handling New Datasets With Different Column Names

The cleaner supports canonical HR fields with alias matching (for example `Salary`, `Age`, `Performance_Rating`).

If a new dataset uses different headers, developers can pass a custom alias map to `clean_hr_data` instead of changing the cleaning rules:

```python
from hr_cleaning.cleaner import clean_hr_data

column_aliases = {
   "Name": {"Employee Full Name"},
   "Gender": {"Sex"},
   "Salary": {"Monthly Income"},
   "Age": {"Employee Age"},
   "Performance_Rating": {"Perf Score"},
   "Overtime_Hours": {"OT"},
}

cleaned_df, stats, outliers_df = clean_hr_data(
   raw_df,
   strict_mode=True,
   column_aliases=column_aliases,
)
```

Notes:
- Aliases are case-insensitive and punctuation-insensitive.
- Runtime aliases are merged with built-in defaults.
- You only add new names in the alias map; cleaning logic stays unchanged.
