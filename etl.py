from pathlib import Path
import sqlite3
import pandas as pd

BASE_DIR = Path(__file__).resolve().parent
SOURCE_FILE = BASE_DIR / "data" / "retail_sales.csv"
REJECTED_FILE = BASE_DIR / "data" / "rejected_rows.csv"
DATABASE_FILE = BASE_DIR / "retail_warehouse.db"
SCHEMA_FILE = BASE_DIR / "sql" / "schema.sql"

REQUIRED_COLUMNS = [
    "transaction_id", "order_date", "customer_id", "customer_name",
    "city", "product_id", "product_name", "category", "quantity", "unit_price"
]


def extract_data():
    """Extract raw retail transactions from CSV."""
    return pd.read_csv(SOURCE_FILE)


def clean_data(raw_data):
    """Validate records, separate rejected rows and calculate revenue."""
    data = raw_data.copy()

    missing_columns = [col for col in REQUIRED_COLUMNS if col not in data.columns]
    if missing_columns:
        raise ValueError(f"Required columns are missing: {missing_columns}")

    data["order_date"] = pd.to_datetime(data["order_date"], errors="coerce")
    data["quantity"] = pd.to_numeric(data["quantity"], errors="coerce")
    data["unit_price"] = pd.to_numeric(data["unit_price"], errors="coerce")

    valid_mask = (
        data[REQUIRED_COLUMNS].notna().all(axis=1)
        & data["quantity"].gt(0)
        & data["unit_price"].ge(0)
    )

    rejected = data.loc[~valid_mask].copy()
    clean = data.loc[valid_mask].copy()

    # Keep only one record for each transaction ID.
    duplicate_mask = clean.duplicated(subset=["transaction_id"], keep="first")
    rejected = pd.concat([rejected, clean.loc[duplicate_mask]], ignore_index=True)
    clean = clean.loc[~duplicate_mask].copy()

    clean["revenue"] = clean["quantity"] * clean["unit_price"]
    clean["order_date"] = clean["order_date"].dt.strftime("%Y-%m-%d")

    return clean, rejected


def create_and_load_warehouse(clean_data):
    """Create dimension tables and load the sales fact table."""
    with sqlite3.connect(DATABASE_FILE) as connection:
        connection.execute("PRAGMA foreign_keys = ON")
        connection.executescript(SCHEMA_FILE.read_text(encoding="utf-8"))

        # Dimension tables: unique descriptive records.
        customers = (
            clean_data[["customer_id", "customer_name", "city"]]
            .drop_duplicates(subset=["customer_id"])
            .sort_values("customer_id")
        )
        products = (
            clean_data[["product_id", "product_name", "category"]]
            .drop_duplicates(subset=["product_id"])
            .sort_values("product_id")
        )

        date_values = sorted(clean_data["order_date"].unique())
        dates = pd.DataFrame({"full_date": date_values})
        date_series = pd.to_datetime(dates["full_date"])
        dates["year"] = date_series.dt.year
        dates["month"] = date_series.dt.month
        dates["day"] = date_series.dt.day

        customers.to_sql("dim_customer_stage", connection, if_exists="replace", index=False)
        products.to_sql("dim_product_stage", connection, if_exists="replace", index=False)
        dates.to_sql("dim_date_stage", connection, if_exists="replace", index=False)

        connection.execute("""
            INSERT OR REPLACE INTO dim_customer (customer_id, customer_name, city)
            SELECT customer_id, customer_name, city FROM dim_customer_stage
        """)
        connection.execute("""
            INSERT OR REPLACE INTO dim_product (product_id, product_name, category)
            SELECT product_id, product_name, category FROM dim_product_stage
        """)
        connection.execute("""
            INSERT OR REPLACE INTO dim_date (full_date, year, month, day)
            SELECT full_date, year, month, day FROM dim_date_stage
        """)

        fact_rows = clean_data[
            ["transaction_id", "order_date", "customer_id", "product_id",
             "quantity", "unit_price", "revenue"]
        ].copy()
        fact_rows.to_sql("fact_stage", connection, if_exists="replace", index=False)

        connection.execute("""
            INSERT OR REPLACE INTO fact_sales
            (transaction_id, date_key, customer_key, product_key,
             quantity, unit_price, revenue)
            SELECT
                f.transaction_id,
                d.date_key,
                c.customer_key,
                p.product_key,
                f.quantity,
                f.unit_price,
                f.revenue
            FROM fact_stage f
            JOIN dim_date d ON d.full_date = f.order_date
            JOIN dim_customer c ON c.customer_id = f.customer_id
            JOIN dim_product p ON p.product_id = f.product_id
        """)

        connection.executescript("""
            DROP TABLE IF EXISTS dim_customer_stage;
            DROP TABLE IF EXISTS dim_product_stage;
            DROP TABLE IF EXISTS dim_date_stage;
            DROP TABLE IF EXISTS fact_stage;
        """)


def show_report():
    """Run a simple business report using SQL joins and aggregation."""
    query = """
        SELECT p.category,
               SUM(f.quantity) AS units_sold,
               ROUND(SUM(f.revenue), 2) AS revenue
        FROM fact_sales f
        JOIN dim_product p ON f.product_key = p.product_key
        GROUP BY p.category
        ORDER BY revenue DESC;
    """
    with sqlite3.connect(DATABASE_FILE) as connection:
        report = pd.read_sql_query(query, connection)
        print("\nRevenue by product category:")
        print(report.to_string(index=False))

        print("\nWarehouse table counts:")
        for table in ("dim_customer", "dim_product", "dim_date", "fact_sales"):
            count = connection.execute(f"SELECT COUNT(*) FROM {table}").fetchone()[0]
            print(f"{table}: {count}")


def main():
    raw_data = extract_data()
    clean, rejected = clean_data(raw_data)
    rejected.to_csv(REJECTED_FILE, index=False)
    create_and_load_warehouse(clean)

    print(f"Rows extracted: {len(raw_data)}")
    print(f"Valid rows loaded: {len(clean)}")
    print(f"Rejected rows saved: {len(rejected)}")
    print(f"Database created: {DATABASE_FILE.name}")
    show_report()


if __name__ == "__main__":
    main()
