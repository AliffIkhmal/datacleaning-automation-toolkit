import unittest

import pandas as pd

from core.cleaner_router import get_cleaner, run_cleaner
from core.schema_detector import detect_industry, detect_schema, resolve_columns
from core.industry_schemas import SALES_SCHEMA, MANUFACTURING_SCHEMA, LOGISTICS_SCHEMA, ECOMMERCE_SCHEMA


class SchemaDetectorTests(unittest.TestCase):
    def test_detect_schema_returns_expected_groups_and_rules(self):
        df = pd.DataFrame(
            {
                "Employee ID": ["E001", "E002", "E003", "E004"],
                "Employee Name": ["Alya", "Ben", "Cara", "Dan"],
                "Salary": [5000, 5000, 5200, 5200],
                "Age": [24, 30, 28, 35],
                "Hire Date": ["2024-01-01", "2024-01-02", "2024-02-15", "2024-03-01"],
                "Department": ["HR", "HR", "IT", "Finance"],
            }
        )

        schema = detect_schema(df)

        self.assertIn("Salary", schema["numeric_columns"])
        self.assertIn("Age", schema["numeric_columns"])
        self.assertIn("Department", schema["categorical_columns"])
        self.assertIn("Hire Date", schema["potential_date_columns"])
        self.assertIn("Employee ID", schema["identifier_columns"])

        suggested_pairs = {
            (item["Column"], item["Suggested Rule"])
            for item in schema["suggested_rules"]
        }
        self.assertIn(("Salary", "Outlier detection"), suggested_pairs)
        self.assertIn(("Age", "Range validation"), suggested_pairs)
        self.assertIn(("Employee ID", "Duplicate detection"), suggested_pairs)
        self.assertIn(("Hire Date", "Date formatting"), suggested_pairs)

    def test_detect_schema_includes_detected_industry(self):
        df = pd.DataFrame(
            {
                "Sales_ID": ["S1", "S2"],
                "Order_ID": ["O1", "O2"],
                "Customer_ID": ["C1", "C2"],
                "Revenue": [100, 200],
                "Quantity_Sold": [1, 2],
                "Order_Date": ["2024-01-01", "2024-02-01"],
            }
        )
        schema = detect_schema(df)
        self.assertEqual(schema["detected_industry"], "Sales")


class IndustryDetectionTests(unittest.TestCase):
    def test_detect_hr_industry(self):
        df = pd.DataFrame(
            {
                "Employee_ID": ["E1"], "Name": ["Ali"], "Gender": ["Male"],
                "Age": [30], "Salary": [5000], "Performance_Rating": [4],
            }
        )
        self.assertEqual(detect_industry(df), "HR")

    def test_detect_sales_industry(self):
        df = pd.DataFrame(
            {
                "Sales_ID": ["S1"], "Order_ID": ["O1"], "Customer_ID": ["C1"],
                "Revenue": [500], "Quantity_Sold": [10], "Order_Date": ["2024-01-01"],
            }
        )
        self.assertEqual(detect_industry(df), "Sales")

    def test_detect_manufacturing_industry(self):
        df = pd.DataFrame(
            {
                "Production_Order_ID": ["PO1"], "Batch_ID": ["B1"],
                "Machine_ID": ["M1"], "Produced_Quantity": [100],
                "Defect_Rate": [2.5], "Production_Date": ["2024-01-01"],
            }
        )
        self.assertEqual(detect_industry(df), "Manufacturing")

    def test_detect_logistics_industry(self):
        df = pd.DataFrame(
            {
                "Shipment_ID": ["SH1"], "Tracking_Number": ["T1"],
                "Order_ID": ["O1"], "Weight_KG": [25.0],
                "Distance_KM": [150], "Delivery_Status": ["Delivered"],
                "Ship_Date": ["2024-01-01"],
            }
        )
        self.assertEqual(detect_industry(df), "Logistics")

    def test_detect_ecommerce_industry(self):
        df = pd.DataFrame(
            {
                "Order_ID": ["O1"], "Customer_ID": ["C1"], "Product_ID": ["P1"],
                "Quantity": [2], "Unit_Price": [29.99],
                "Order_Value": [59.98], "Order_Date": ["2024-01-01"],
            }
        )
        self.assertEqual(detect_industry(df), "E-commerce")

    def test_unrecognised_dataset_returns_none(self):
        df = pd.DataFrame({"ColA": [1], "ColB": [2], "ColC": ["x"]})
        self.assertIsNone(detect_industry(df))

    def test_resolve_columns_uses_aliases(self):
        df = pd.DataFrame({"qty_sold": [10], "total_sales": [500]})
        col_map = resolve_columns(df, SALES_SCHEMA)
        self.assertEqual(col_map["Quantity_Sold"], "qty_sold")
        self.assertEqual(col_map["Revenue"], "total_sales")


class CleanerRouterTests(unittest.TestCase):
    def test_get_cleaner_returns_hr_cleaner(self):
        cleaner = get_cleaner("HR Data Cleaner")

        self.assertTrue(cleaner.implemented)
        self.assertEqual(cleaner.tool_name, "HR Data Cleaner")

    def test_get_cleaner_returns_sales_cleaner(self):
        cleaner = get_cleaner("Sales Data Cleaner")

        self.assertTrue(cleaner.implemented)
        self.assertEqual(cleaner.tool_name, "Sales Data Cleaner")

    def test_all_cleaners_are_implemented(self):
        for label in ("HR Data Cleaner", "Sales Data Cleaner",
                       "Manufacturing Data Cleaner", "Logistics Data Cleaner",
                       "E-commerce Data Cleaner"):
            cleaner = get_cleaner(label)
            self.assertTrue(cleaner.implemented, f"{label} should be implemented")

    def test_run_cleaner_uses_existing_hr_cleaner_pipeline(self):
        df = pd.DataFrame(
            {
                "Name": ["Siti Aminah", "Muhammad Firdaus"],
                "Gender": [None, None],
                "Salary": [15000, 120000],
                "Age": [25, 31],
                "Performance Rating": [4, 5],
                "Overtime Hours": [2, 4],
            }
        )

        result = run_cleaner("HR Data Cleaner", df)

        self.assertEqual(result.output_filename, "cleaned_hr_dataset.csv")
        self.assertIn("Total Rows", result.report_df["Metric"].tolist())
        self.assertEqual(result.cleaned_df.loc[0, "Gender"], "Female")
        self.assertLess(int(result.cleaned_df.loc[1, "Salary"]), 100000)


class SalesCleanerTests(unittest.TestCase):
    def test_sales_cleaner_processes_dataset(self):
        df = pd.DataFrame(
            {
                "Sales_ID": ["S1", "S2", "S3", "S3"],
                "Revenue": [500, 1200, -300, -300],
                "Quantity_Sold": [5, 10, 3, 3],
                "Region": ["east", "WEST", "north", "north"],
                "Order_Date": ["01/15/2024", "2024-02-20", "March 1, 2024", "March 1, 2024"],
            }
        )

        result = run_cleaner("Sales Data Cleaner", df)

        self.assertEqual(result.output_filename, "cleaned_sales_dataset.csv")
        self.assertEqual(result.stats["duplicates_removed"], 1)
        self.assertGreater(result.stats["negatives_corrected"], 0)
        # Region should be title-cased
        self.assertIn("East", result.cleaned_df["Region"].values)

    def test_sales_cleaner_fills_missing(self):
        df = pd.DataFrame(
            {
                "Sales_ID": ["S1", "S2", "S3"],
                "Revenue": [500, None, 700],
                "Region": ["East", None, "West"],
            }
        )
        result = run_cleaner("Sales Data Cleaner", df)
        self.assertGreater(result.stats["missing_values_fixed"], 0)
        self.assertFalse(result.cleaned_df["Revenue"].isna().any())


class ManufacturingCleanerTests(unittest.TestCase):
    def test_manufacturing_cleaner_processes_dataset(self):
        df = pd.DataFrame(
            {
                "Production_Order_ID": ["PO1", "PO2", "PO3"],
                "Produced_Quantity": [100, -50, 200],
                "Defect_Rate": [2.5, 150, 1.0],
                "Shift": ["morning", "NIGHT", "afternoon"],
                "Production_Date": ["2024-01-01", "2024/02/15", "March 10, 2024"],
            }
        )

        result = run_cleaner("Manufacturing Data Cleaner", df)

        self.assertEqual(result.output_filename, "cleaned_manufacturing_dataset.csv")
        self.assertGreater(result.stats["negatives_corrected"], 0)
        # Defect rate 150 should be clipped to 100
        self.assertGreater(result.stats["range_values_clipped"], 0)
        self.assertIn("Morning", result.cleaned_df["Shift"].values)


class LogisticsCleanerTests(unittest.TestCase):
    def test_logistics_cleaner_processes_dataset(self):
        df = pd.DataFrame(
            {
                "Shipment_ID": ["SH1", "SH2", "SH3"],
                "Weight_KG": [25.5, -10.0, 50.0],
                "Freight_Cost": [120, 250, 80],
                "Delivery_Status": ["delivered", "IN TRANSIT", "returned"],
                "Ship_Date": ["2024-01-05", "2024/03/12", "Jan 20, 2024"],
            }
        )

        result = run_cleaner("Logistics Data Cleaner", df)

        self.assertEqual(result.output_filename, "cleaned_logistics_dataset.csv")
        self.assertGreater(result.stats["negatives_corrected"], 0)
        self.assertIn("Delivered", result.cleaned_df["Delivery_Status"].values)


class EcommerceCleanerTests(unittest.TestCase):
    def test_ecommerce_cleaner_processes_dataset(self):
        df = pd.DataFrame(
            {
                "Order_ID": ["O1", "O2", "O3", "O3"],
                "Quantity": [2, -1, 5, 5],
                "Unit_Price": [29.99, 15.50, 49.00, 49.00],
                "Order_Value": [59.98, 15.50, 245.00, 245.00],
                "Order_Status": ["completed", "PENDING", "cancelled", "cancelled"],
                "Order_Date": ["2024-01-01", "2024/02/14", "March 5, 2024", "March 5, 2024"],
            }
        )

        result = run_cleaner("E-commerce Data Cleaner", df)

        self.assertEqual(result.output_filename, "cleaned_ecommerce_dataset.csv")
        self.assertEqual(result.stats["duplicates_removed"], 1)
        self.assertGreater(result.stats["negatives_corrected"], 0)
        self.assertIn("Completed", result.cleaned_df["Order_Status"].values)


if __name__ == "__main__":
    unittest.main()