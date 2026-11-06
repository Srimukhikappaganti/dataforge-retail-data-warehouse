# RetailPulse: Sales Data Pipeline & Warehouse

A practical, interview-friendly Data Engineering project built with Python, Pandas, SQL and SQLite.

## Project objective
Turn raw retail transaction data into clean, structured warehouse tables that can support business reporting.

## Architecture
`retail_sales.csv` -> Extract -> Validate/Clean -> Transform -> Load -> SQLite Star Schema -> SQL Reports

## Implemented features
- Read raw transaction data from CSV with Pandas.
- Check required fields, missing values, duplicate transaction IDs, invalid quantities and negative prices.
- Save rejected records separately for review.
- Calculate transaction revenue.
- Create a simple Star Schema:
  - `fact_sales`
  - `dim_customer`
  - `dim_product`
  - `dim_date`
- Load dimension and fact tables into SQLite.
- Run SQL reports for revenue by category, monthly revenue and top customers.

## Tech stack
- Python
- Pandas
- SQL
- SQLite
- Git / GitHub

## Run locally
Python 3.10+ is recommended.

```bash
python -m venv .venv
```

Windows:
```bash
.venv\Scripts\activate
```

macOS/Linux:
```bash
source .venv/bin/activate
```

Install dependencies and run:
```bash
pip install -r requirements.txt
python etl.py
```

The script creates `retail_warehouse.db` and `data/rejected_rows.csv`.

## How to explain the Star Schema
`fact_sales` stores measurable business events such as quantity and revenue. The dimension tables store descriptive information about customers, products and dates. The fact table connects to each dimension using keys, making reporting queries easier to write.

## Interview explanation
"I built a retail sales ETL pipeline using Python, Pandas, SQL and SQLite. I extracted transaction data from a CSV file, validated records, handled missing and duplicate data, and calculated revenue. I then designed a simple Star Schema with a sales fact table and customer, product and date dimension tables. Finally, I loaded the tables into SQLite and wrote SQL queries to analyse monthly revenue, category performance and customer sales. This project helped me understand ETL, data quality, dimensional modelling and analytical SQL."

## Important scope note
This project implements a small local SQLite warehouse and a basic Star Schema. It does not implement a cloud warehouse, production orchestration, slowly changing dimensions, or a full enterprise-scale pipeline. These can be future enhancements.
