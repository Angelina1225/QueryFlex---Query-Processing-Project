# QueryFlex — Query Processing Project

QueryFlex is a Python-based query processing system that translates extended SQL (eSQL) queries into standard SQL and executes them against a PostgreSQL database. It supports 6 predefined queries over a `sales` table and includes a test suite that compares eSQL and SQL results for correctness validation.

---

## Prerequisites

- Python 3.8+
- PostgreSQL (with the `sales` table already loaded)
- pip

---

## Setup

### 1. Configure your PostgreSQL connection

Before running anything, open `generator.py` and `sql.py` and insert your personal PostgreSQL credentials under the connection section:

```python
conn = psycopg2.connect(
    host="YOUR_HOST",
    database="YOUR_DATABASE",
    user="YOUR_USERNAME",
    password="YOUR_PASSWORD"
)
```

### 2. Install dependencies

```bash
pip install -r requirements.txt
```

### 3. Navigate to the project directory

```bash
cd Code
```

---

## Usage

> **Note:** The `sales` table must already be loaded in your PostgreSQL database before running any of the commands below.

### Run the eSQL Generator

Processes an extended SQL query and produces the MF table result:

```bash
python generator.py
```

You will be prompted to enter a query number between **1 and 6**.

---

### Run the SQL Query

Executes the equivalent standard SQL query and produces the MF table result:

```bash
python sql.py
```

You will be prompted to enter a query number between **1 and 6**.

---

### Run the Test Suite

Runs pytest to compare the output of `generator.py` (eSQL) against `sql.py` (SQL) and verifies that the results match:

```bash
pytest -s test_generator.py
```

You will be prompted to enter a query number between **1 and 6**.

---

## Project Structure

```
QueryFlex---Query-Processing-Project/
│
├── Code/
│   ├── generator.py          # eSQL processor — generates the MF table using extended SQL logic
│   ├── sql.py                # Standard SQL processor — generates the MF table using SQL
│   ├── queries.py            # Definitions for all 6 supported queries
│   ├── QueryProcessor.py     # Core query processing engine
│   ├── _generated.py         # Auto-generated output from the generator (do not edit manually)
│   ├── test_generator.py     # Pytest suite comparing eSQL vs SQL results
│   └── inputs/               # Input data files
│
└── requirements.txt          # Python dependencies
```

---

## Supported Queries

QueryFlex supports **6 predefined queries** (numbered 1–6), each targeting the `sales` table. When running any script, you will be asked to select which query to execute.

---

## How It Works

| Script | Approach | Output |
|---|---|---|
| `generator.py` | Extended SQL (eSQL) — processes queries using custom MF (multi-feature) table logic | MF table |
| `sql.py` | Standard PostgreSQL SQL | MF table |
| `test_generator.py` | Runs both and compares results | Pass / Fail |

The test suite (`test_generator.py`) validates correctness by asserting that the eSQL and SQL approaches produce identical results for the same query number.
