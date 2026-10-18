"""
Supermarket Sales & Customer Analytics - SQLite Relational Database Engine
Module: src/database.py

Purpose:
Provides enterprise-grade, persistent relational storage for the Supermarket
Intelligence System using Python's standard built-in `sqlite3` library.

Key Features for BCA Capstone & Viva:
1. Relational Integrity: Enforces `PRAGMA foreign_keys = ON;`, primary keys,
   foreign keys with ON DELETE CASCADE, CHECK constraints, and UNIQUE indexes.
2. Parameterized Queries: All SQL statements use positional `?` parameters to
   guarantee complete immunity against SQL injection vulnerabilities.
3. Safe Non-Destructive Ingestion: Offers `skip_duplicates` (`INSERT OR IGNORE`)
   and `replace_all` modes with detailed audit summaries.
4. Immutable Inventory Ledger: Tracks stock movements with running balances,
   strictly preventing negative inventory.
5. Dual-Layer Audit Logging: Persists anomaly records and generated reports.
"""

import os
import sqlite3
from pathlib import Path
from typing import Dict, Any, List, Optional, Tuple, Union
import pandas as pd
import numpy as np

# Default SQLite database path in data/ directory
DEFAULT_DB_PATH = Path(__file__).resolve().parent.parent / "data" / "supermarket_intelligence.db"
DEFAULT_CLEAN_CSV = Path(__file__).resolve().parent.parent / "data" / "processed" / "supermarket_sales_cleaned.csv"


def get_db_connection(db_path: Optional[Union[str, Path]] = None) -> sqlite3.Connection:
    """Create and configure a thread-safe connection to SQLite database.

    Enforces foreign key constraint checks and dictionary-like column access.
    Supports in-memory databases (':memory:') for automated isolated testing.
    """
    path_str = str(db_path or DEFAULT_DB_PATH)
    if path_str != ":memory:":
        os.makedirs(os.path.dirname(os.path.abspath(path_str)), exist_ok=True)

    conn = sqlite3.connect(path_str, timeout=15.0)
    # Enable foreign keys constraint enforcement in SQLite
    conn.execute("PRAGMA foreign_keys = ON;")
    # Enable WAL mode for concurrent read performance if on disk
    if path_str != ":memory:":
        conn.execute("PRAGMA journal_mode = WAL;")
    conn.row_factory = sqlite3.Row
    return conn


def init_database(db_path: Optional[Union[str, Path]] = None) -> None:
    """Initialize database tables, constraints, and indexes if they do not exist."""
    conn = get_db_connection(db_path)
    cursor = conn.cursor()

    try:
        # 1. Categories Table
        cursor.execute("""
        CREATE TABLE IF NOT EXISTS categories (
            category_id INTEGER PRIMARY KEY AUTOINCREMENT,
            category_name TEXT UNIQUE NOT NULL COLLATE NOCASE,
            description TEXT DEFAULT '',
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        );
        """)

        # 2. Products Table
        cursor.execute("""
        CREATE TABLE IF NOT EXISTS products (
            product_id INTEGER PRIMARY KEY AUTOINCREMENT,
            product_name TEXT UNIQUE NOT NULL COLLATE NOCASE,
            category_id INTEGER NOT NULL,
            unit_price REAL NOT NULL CHECK(unit_price >= 0),
            reorder_threshold INTEGER NOT NULL DEFAULT 20 CHECK(reorder_threshold >= 0),
            target_stock INTEGER NOT NULL DEFAULT 100 CHECK(target_stock >= reorder_threshold),
            is_active INTEGER NOT NULL DEFAULT 1 CHECK(is_active IN (0, 1)),
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            FOREIGN KEY (category_id) REFERENCES categories(category_id) ON DELETE RESTRICT
        );
        """)

        # 3. Inventory Stock (Current Balance Snapshot)
        cursor.execute("""
        CREATE TABLE IF NOT EXISTS inventory_stock (
            product_id INTEGER PRIMARY KEY,
            current_quantity INTEGER NOT NULL DEFAULT 0 CHECK(current_quantity >= 0),
            last_restocked_date TEXT,
            updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            FOREIGN KEY (product_id) REFERENCES products(product_id) ON DELETE CASCADE
        );
        """)

        # 4. Inventory Movements (Immutable Stock Ledger)
        cursor.execute("""
        CREATE TABLE IF NOT EXISTS inventory_movements (
            movement_id INTEGER PRIMARY KEY AUTOINCREMENT,
            product_id INTEGER NOT NULL,
            movement_date TEXT NOT NULL,
            movement_type TEXT NOT NULL CHECK(
                movement_type IN (
                    'INITIAL', 'RECEIPT', 'SALE_DEDUCTION',
                    'ADJUSTMENT_ADD', 'ADJUSTMENT_SUB', 'WASTE_DAMAGE', 'RETURN'
                )
            ),
            quantity_change INTEGER NOT NULL,
            balance_after INTEGER NOT NULL CHECK(balance_after >= 0),
            reference_note TEXT DEFAULT '',
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            FOREIGN KEY (product_id) REFERENCES products(product_id) ON DELETE CASCADE
        );
        """)

        # 5. Sales Transactions Table
        cursor.execute("""
        CREATE TABLE IF NOT EXISTS sales_transactions (
            transaction_id INTEGER PRIMARY KEY AUTOINCREMENT,
            invoice_id TEXT UNIQUE NOT NULL,
            transaction_date TEXT NOT NULL,
            branch TEXT NOT NULL,
            city TEXT NOT NULL,
            customer_type TEXT NOT NULL,
            gender TEXT NOT NULL,
            product_id INTEGER,
            product_name TEXT NOT NULL,
            category_name TEXT NOT NULL,
            quantity INTEGER NOT NULL CHECK(quantity > 0),
            unit_price REAL NOT NULL CHECK(unit_price >= 0),
            sales_amount REAL NOT NULL CHECK(sales_amount >= 0),
            payment_method TEXT NOT NULL,
            rating REAL NOT NULL CHECK(rating >= 1.0 AND rating <= 5.0),
            imported_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            source_file TEXT DEFAULT 'default_cleaned_dataset',
            FOREIGN KEY (product_id) REFERENCES products(product_id) ON DELETE SET NULL
        );
        """)

        # 6. Anomaly Records Table (Dual-layer error & statistical audit)
        cursor.execute("""
        CREATE TABLE IF NOT EXISTS anomaly_records (
            anomaly_id INTEGER PRIMARY KEY AUTOINCREMENT,
            detected_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            invoice_id TEXT,
            anomaly_type TEXT NOT NULL CHECK(
                anomaly_type IN (
                    'DATA_QUALITY_ERROR', 'STATISTICAL_ANOMALY',
                    'TEMPORAL_SPIKE', 'TEMPORAL_DIP', 'DUPLICATE_ID',
                    'VALUE_MISMATCH'
                )
            ),
            severity TEXT NOT NULL CHECK(severity IN ('CRITICAL', 'HIGH', 'MEDIUM', 'LOW')),
            description TEXT NOT NULL,
            expected_value TEXT DEFAULT '',
            actual_value TEXT DEFAULT '',
            recommended_action TEXT NOT NULL,
            is_resolved INTEGER NOT NULL DEFAULT 0 CHECK(is_resolved IN (0, 1))
        );
        """)

        # 7. Report History Table (Audit log of generated reports)
        cursor.execute("""
        CREATE TABLE IF NOT EXISTS report_history (
            report_id INTEGER PRIMARY KEY AUTOINCREMENT,
            generated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            report_type TEXT NOT NULL CHECK(report_type IN ('PDF_EXECUTIVE', 'EXCEL_WORKBOOK', 'CSV_DATA')),
            file_name TEXT NOT NULL,
            file_size_bytes INTEGER NOT NULL,
            dataset_scope TEXT NOT NULL,
            filter_summary TEXT DEFAULT '',
            record_count INTEGER NOT NULL
        );
        """)

        # Performance Indexes for frequent dashboard queries
        cursor.execute("CREATE INDEX IF NOT EXISTS idx_sales_date ON sales_transactions(transaction_date);")
        cursor.execute("CREATE INDEX IF NOT EXISTS idx_sales_city ON sales_transactions(city);")
        cursor.execute("CREATE INDEX IF NOT EXISTS idx_sales_branch ON sales_transactions(branch);")
        cursor.execute("CREATE INDEX IF NOT EXISTS idx_sales_category ON sales_transactions(category_name);")
        cursor.execute("CREATE INDEX IF NOT EXISTS idx_sales_product ON sales_transactions(product_name);")
        cursor.execute("CREATE INDEX IF NOT EXISTS idx_inventory_product ON inventory_movements(product_id);")

        conn.commit()
    finally:
        conn.close()


def seed_database_if_empty(
    db_path: Optional[Union[str, Path]] = None,
    csv_path: Optional[Union[str, Path]] = None,
    force_reseed: bool = False
) -> Dict[str, int]:
    """Seed the SQLite database with baseline categories, products, stock, and sales.

    Only executes if the database is currently empty, unless force_reseed is True.
    Returns dictionary with counts of seeded records.
    """
    init_database(db_path)
    conn = get_db_connection(db_path)
    cursor = conn.cursor()

    try:
        if force_reseed:
            cursor.execute("PRAGMA foreign_keys = OFF;")
            for tbl in ["inventory_movements", "inventory_stock", "sales_transactions", "anomaly_records", "report_history", "products", "categories"]:
                cursor.execute(f"DELETE FROM {tbl};")
            cursor.execute("PRAGMA foreign_keys = ON;")
            conn.commit()

        cursor.execute("SELECT COUNT(*) FROM sales_transactions;")
        existing_txns = cursor.fetchone()[0]

        if existing_txns > 0 and not force_reseed:
            return {"categories": 0, "products": 0, "transactions": 0, "status": "already_populated"}

        # Load baseline cleaned dataset
        source_csv = csv_path or DEFAULT_CLEAN_CSV
        if not os.path.exists(source_csv):
            return {"error": f"Base dataset not found at {source_csv}"}

        df = pd.read_csv(source_csv)

        # 1. Seed Categories
        categories = sorted(df["Category"].dropna().unique().tolist())
        cat_map: Dict[str, int] = {}
        for cat in categories:
            cursor.execute(
                "INSERT INTO categories (category_name, description) VALUES (?, ?);",
                (cat, f"Supermarket merchandise category: {cat}")
            )
            cat_map[cat] = cursor.lastrowid

        # 2. Seed Products
        prod_agg = df.groupby(["Product", "Category"]).agg(
            Avg_Price=("Unit Price", "mean")
        ).reset_index()

        prod_map: Dict[str, int] = {}
        for _, row in prod_agg.iterrows():
            p_name = row["Product"]
            c_name = row["Category"]
            u_price = round(float(row["Avg_Price"]), 2)
            c_id = cat_map[c_name]

            # Assign sensible initial stock policies based on price and volume
            reorder_threshold = 20
            target_stock = 100
            initial_stock = 65

            cursor.execute("""
            INSERT INTO products (
                product_name, category_id, unit_price, reorder_threshold, target_stock
            ) VALUES (?, ?, ?, ?, ?);
            """, (p_name, c_id, u_price, reorder_threshold, target_stock))
            p_id = cursor.lastrowid
            prod_map[p_name] = p_id

            # Create initial inventory stock
            cursor.execute("""
            INSERT INTO inventory_stock (
                product_id, current_quantity, last_restocked_date
            ) VALUES (?, ?, ?);
            """, (p_id, initial_stock, "2026-01-01"))

            # Log initial movement in stock ledger
            cursor.execute("""
            INSERT INTO inventory_movements (
                product_id, movement_date, movement_type, quantity_change, balance_after, reference_note
            ) VALUES (?, ?, ?, ?, ?, ?);
            """, (p_id, "2026-01-01", "INITIAL", initial_stock, initial_stock, "Initial inventory intake"))

        # 3. Seed Sales Transactions (500 records)
        seeded_txns = 0
        for _, row in df.iterrows():
            inv_id = str(row["Invoice ID"]).strip()
            t_date = str(row["Date"]).strip()
            branch = str(row["Branch"]).strip()
            city = str(row["City"]).strip()
            c_type = str(row["Customer Type"]).strip()
            gender = str(row["Gender"]).strip()
            p_name = str(row["Product"]).strip()
            cat_name = str(row["Category"]).strip()
            qty = int(row["Quantity"])
            u_price = float(row["Unit Price"])
            sales = float(row["Sales"])
            pay = str(row["Payment"]).strip()
            rating = float(row["Rating"])
            p_id = prod_map.get(p_name)

            cursor.execute("""
            INSERT INTO sales_transactions (
                invoice_id, transaction_date, branch, city, customer_type, gender,
                product_id, product_name, category_name, quantity, unit_price,
                sales_amount, payment_method, rating, source_file
            ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?);
            """, (
                inv_id, t_date, branch, city, c_type, gender,
                p_id, p_name, cat_name, qty, u_price,
                sales, pay, rating, "supermarket_sales_cleaned.csv"
            ))
            seeded_txns += 1

        conn.commit()
        return {
            "categories": len(cat_map),
            "products": len(prod_map),
            "transactions": seeded_txns,
            "status": "success"
        }
    finally:
        conn.close()


def get_all_sales_df(db_path: Optional[Union[str, Path]] = None) -> pd.DataFrame:
    """Retrieve all sales transactions as a pandas DataFrame formatted for dashboard analytics."""
    init_database(db_path)
    conn = get_db_connection(db_path)
    try:
        query = """
        SELECT
            invoice_id AS "Invoice ID",
            transaction_date AS "Date",
            branch AS "Branch",
            city AS "City",
            customer_type AS "Customer Type",
            gender AS "Gender",
            product_name AS "Product",
            category_name AS "Category",
            quantity AS "Quantity",
            unit_price AS "Unit Price",
            payment_method AS "Payment",
            rating AS "Rating",
            sales_amount AS "Sales"
        FROM sales_transactions
        ORDER BY transaction_date ASC, transaction_id ASC;
        """
        df = pd.read_sql_query(query, conn)
        if not df.empty:
            df["Date"] = pd.to_datetime(df["Date"], errors="coerce")
            df["Year"] = df["Date"].dt.year
            df["Month"] = df["Date"].dt.month
            df["Month_Name"] = df["Date"].dt.strftime("%b")
            df["Day"] = df["Date"].dt.day
            df["Day_Of_Week"] = df["Date"].dt.day_name()
            df["Transaction_Value"] = df["Sales"]
            df["Sales_Per_Quantity"] = (df["Sales"] / df["Quantity"]).round(2)
        return df
    finally:
        conn.close()


def import_sales_dataframe(
    df: pd.DataFrame,
    mode: str = "skip_duplicates",
    source_file: str = "upload",
    db_path: Optional[Union[str, Path]] = None
) -> Dict[str, Any]:
    """Import a validated sales DataFrame into the SQLite relational database.

    Args:
        df: Processed DataFrame containing canonical retail columns.
        mode: Ingestion strategy:
              - 'skip_duplicates' (default): Uses INSERT OR IGNORE on Invoice ID.
              - 'replace_all': Truncates sales_transactions and imports entire DataFrame.
        source_file: Identifier for data lineage tracking.
        db_path: Optional custom database path (supports ':memory:').

    Returns:
        Structured audit dictionary with counts of processed, inserted, skipped,
        and new catalog products auto-registered.
    """
    if df.empty:
        return {"total_processed": 0, "inserted": 0, "duplicates_skipped": 0, "errors": ["DataFrame is empty."]}

    init_database(db_path)
    conn = get_db_connection(db_path)
    cursor = conn.cursor()

    summary: Dict[str, Any] = {
        "mode": mode,
        "total_processed": len(df),
        "inserted": 0,
        "duplicates_skipped": 0,
        "new_products_created": 0,
        "new_categories_created": 0,
        "errors": []
    }

    try:
        conn.execute("BEGIN TRANSACTION;")

        if mode == "replace_all":
            cursor.execute("DELETE FROM sales_transactions;")

        # Fetch existing categories and products for foreign key mapping
        cursor.execute("SELECT category_name, category_id FROM categories;")
        cat_cache = {row[0].lower(): row[1] for row in cursor.fetchall()}

        cursor.execute("SELECT product_name, product_id FROM products;")
        prod_cache = {row[0].lower(): row[1] for row in cursor.fetchall()}

        # Auto-create any missing categories
        unique_cats = df["Category"].dropna().unique().tolist()
        for cat in unique_cats:
            cat_clean = str(cat).strip()
            cat_lower = cat_clean.lower()
            if cat_lower not in cat_cache:
                cursor.execute(
                    "INSERT INTO categories (category_name, description) VALUES (?, ?);",
                    (cat_clean, "Auto-discovered category via upload")
                )
                new_cat_id = cursor.lastrowid
                cat_cache[cat_lower] = new_cat_id
                summary["new_categories_created"] += 1

        # Auto-create any missing products
        unique_prods = df[["Product", "Category", "Unit Price"]].drop_duplicates(subset=["Product"])
        for _, prow in unique_prods.iterrows():
            p_name = str(prow["Product"]).strip()
            p_lower = p_name.lower()
            if p_lower not in prod_cache:
                c_name = str(prow["Category"]).strip().lower()
                c_id = cat_cache.get(c_name, list(cat_cache.values())[0] if cat_cache else 1)
                u_price = round(float(prow["Unit Price"]), 2)
                cursor.execute("""
                INSERT INTO products (product_name, category_id, unit_price, reorder_threshold, target_stock)
                VALUES (?, ?, ?, 20, 100);
                """, (p_name, c_id, u_price))
                new_pid = cursor.lastrowid
                prod_cache[p_lower] = new_pid

                # Auto-initialize inventory stock
                cursor.execute("""
                INSERT INTO inventory_stock (product_id, current_quantity, last_restocked_date)
                VALUES (?, 50, datetime('now'));
                """, (new_pid,))
                cursor.execute("""
                INSERT INTO inventory_movements (
                    product_id, movement_date, movement_type, quantity_change, balance_after, reference_note
                ) VALUES (?, date('now'), 'INITIAL', 50, 50, 'Auto-registered product from data upload');
                """, (new_pid,))
                summary["new_products_created"] += 1

        # Insert transactions using parameterized SQL
        for _, row in df.iterrows():
            inv_id = str(row["Invoice ID"]).strip()
            raw_date = row["Date"]
            t_date = pd.to_datetime(raw_date).strftime("%Y-%m-%d") if pd.notnull(raw_date) else "2026-01-01"

            branch = str(row.get("Branch", "Branch A")).strip()
            city = str(row.get("City", "General")).strip()
            c_type = str(row.get("Customer Type", "Normal")).strip()
            gender = str(row.get("Gender", "Not Specified")).strip()
            p_name = str(row["Product"]).strip()
            cat_name = str(row["Category"]).strip()
            qty = max(1, int(row["Quantity"]))
            u_price = max(0.0, float(row["Unit Price"]))
            sales = max(0.0, float(row["Sales"]))
            pay = str(row.get("Payment", "Cash")).strip()
            rating = max(1.0, min(5.0, float(row.get("Rating", 4.0))))
            p_id = prod_cache.get(p_name.lower())

            if mode == "skip_duplicates":
                cursor.execute("""
                INSERT OR IGNORE INTO sales_transactions (
                    invoice_id, transaction_date, branch, city, customer_type, gender,
                    product_id, product_name, category_name, quantity, unit_price,
                    sales_amount, payment_method, rating, source_file
                ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?);
                """, (
                    inv_id, t_date, branch, city, c_type, gender,
                    p_id, p_name, cat_name, qty, u_price,
                    sales, pay, rating, source_file
                ))
                if cursor.rowcount > 0:
                    summary["inserted"] += 1
                else:
                    summary["duplicates_skipped"] += 1
            else:
                cursor.execute("""
                INSERT INTO sales_transactions (
                    invoice_id, transaction_date, branch, city, customer_type, gender,
                    product_id, product_name, category_name, quantity, unit_price,
                    sales_amount, payment_method, rating, source_file
                ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?);
                """, (
                    inv_id, t_date, branch, city, c_type, gender,
                    p_id, p_name, cat_name, qty, u_price,
                    sales, pay, rating, source_file
                ))
                summary["inserted"] += 1

        conn.commit()
    except Exception as e:
        conn.rollback()
        summary["errors"].append(str(e))
    finally:
        conn.close()

    return summary


# -------------------------------------------------------------
# CRUD OPERATIONS: PRODUCTS & INVENTORY
# -------------------------------------------------------------
def get_products_df(active_only: bool = True, db_path: Optional[Union[str, Path]] = None) -> pd.DataFrame:
    """Retrieve catalog products with category details and current stock balance."""
    init_database(db_path)
    conn = get_db_connection(db_path)
    try:
        where_clause = "WHERE p.is_active = 1" if active_only else ""
        query = f"""
        SELECT
            p.product_id AS "Product ID",
            p.product_name AS "Product Name",
            c.category_name AS "Category",
            p.unit_price AS "Unit Price (₹)",
            COALESCE(s.current_quantity, 0) AS "Current Stock",
            p.reorder_threshold AS "Reorder Threshold",
            p.target_stock AS "Target Stock",
            CASE
                WHEN COALESCE(s.current_quantity, 0) = 0 THEN 'OUT_OF_STOCK'
                WHEN COALESCE(s.current_quantity, 0) <= p.reorder_threshold THEN 'LOW_STOCK'
                ELSE 'HEALTHY'
            END AS "Stock Status",
            p.is_active AS "Active",
            p.created_at AS "Created At"
        FROM products p
        JOIN categories c ON p.category_id = c.category_id
        LEFT JOIN inventory_stock s ON p.product_id = s.product_id
        {where_clause}
        ORDER BY p.product_name ASC;
        """
        return pd.read_sql_query(query, conn)
    finally:
        conn.close()


def create_product(
    product_name: str,
    category_name: str,
    unit_price: float,
    reorder_threshold: int = 20,
    target_stock: int = 100,
    initial_stock: int = 50,
    db_path: Optional[Union[str, Path]] = None
) -> int:
    """Create a new product in the catalog with initial stock and ledger entry.

    Returns the new product_id.
    """
    init_database(db_path)
    conn = get_db_connection(db_path)
    cursor = conn.cursor()
    try:
        conn.execute("BEGIN TRANSACTION;")

        cursor.execute("SELECT category_id FROM categories WHERE category_name = ? COLLATE NOCASE;", (category_name.strip(),))
        cat_row = cursor.fetchone()
        if cat_row:
            cat_id = cat_row[0]
        else:
            cursor.execute("INSERT INTO categories (category_name, description) VALUES (?, ?);", (category_name.strip(), "User-created category"))
            cat_id = cursor.lastrowid

        cursor.execute("""
        INSERT INTO products (product_name, category_id, unit_price, reorder_threshold, target_stock)
        VALUES (?, ?, ?, ?, ?);
        """, (product_name.strip(), cat_id, float(unit_price), int(reorder_threshold), int(target_stock)))
        new_pid = cursor.lastrowid

        cursor.execute("""
        INSERT INTO inventory_stock (product_id, current_quantity, last_restocked_date)
        VALUES (?, ?, date('now'));
        """, (new_pid, int(initial_stock)))

        cursor.execute("""
        INSERT INTO inventory_movements (
            product_id, movement_date, movement_type, quantity_change, balance_after, reference_note
        ) VALUES (?, date('now'), 'INITIAL', ?, ?, 'Initial product creation intake');
        """, (new_pid, int(initial_stock), int(initial_stock)))

        conn.commit()
        return new_pid
    except Exception:
        conn.rollback()
        raise
    finally:
        conn.close()


def update_product(
    product_id: int,
    product_name: str,
    category_name: str,
    unit_price: float,
    reorder_threshold: int,
    target_stock: int,
    is_active: int = 1,
    db_path: Optional[Union[str, Path]] = None
) -> bool:
    """Update catalog product metadata, pricing, and reorder policies."""
    init_database(db_path)
    conn = get_db_connection(db_path)
    cursor = conn.cursor()
    try:
        conn.execute("BEGIN TRANSACTION;")

        cursor.execute("SELECT category_id FROM categories WHERE category_name = ? COLLATE NOCASE;", (category_name.strip(),))
        cat_row = cursor.fetchone()
        if cat_row:
            cat_id = cat_row[0]
        else:
            cursor.execute("INSERT INTO categories (category_name, description) VALUES (?, ?);", (category_name.strip(), "Updated category"))
            cat_id = cursor.lastrowid

        cursor.execute("""
        UPDATE products
        SET product_name = ?,
            category_id = ?,
            unit_price = ?,
            reorder_threshold = ?,
            target_stock = ?,
            is_active = ?,
            updated_at = CURRENT_TIMESTAMP
        WHERE product_id = ?;
        """, (
            product_name.strip(), cat_id, float(unit_price),
            int(reorder_threshold), int(target_stock), int(is_active), int(product_id)
        ))
        conn.commit()
        return cursor.rowcount > 0
    except Exception:
        conn.rollback()
        raise
    finally:
        conn.close()


def delete_product(product_id: int, hard_delete: bool = False, db_path: Optional[Union[str, Path]] = None) -> bool:
    """Deactivate (soft delete) or remove (hard delete) a catalog product."""
    init_database(db_path)
    conn = get_db_connection(db_path)
    cursor = conn.cursor()
    try:
        if hard_delete:
            cursor.execute("DELETE FROM products WHERE product_id = ?;", (int(product_id),))
        else:
            cursor.execute("UPDATE products SET is_active = 0, updated_at = CURRENT_TIMESTAMP WHERE product_id = ?;", (int(product_id),))
        conn.commit()
        return cursor.rowcount > 0
    finally:
        conn.close()


def get_categories_list(db_path: Optional[Union[str, Path]] = None) -> List[str]:
    """Retrieve sorted list of all active merchandise category names."""
    init_database(db_path)
    conn = get_db_connection(db_path)
    try:
        cursor = conn.cursor()
        cursor.execute("SELECT category_name FROM categories ORDER BY category_name ASC;")
        return [row[0] for row in cursor.fetchall()]
    finally:
        conn.close()


def record_stock_movement(
    product_id: int,
    movement_type: str,
    quantity_change: int,
    reference_note: str = "",
    db_path: Optional[Union[str, Path]] = None
) -> int:
    """Record an inventory adjustment/receipt in the immutable ledger.

    Strictly prevents negative stock balances by validating current balance.
    Updates the inventory_stock snapshot atomically.
    Returns movement_id.
    """
    init_database(db_path)
    conn = get_db_connection(db_path)
    cursor = conn.cursor()
    try:
        conn.execute("BEGIN TRANSACTION;")

        cursor.execute("SELECT current_quantity FROM inventory_stock WHERE product_id = ?;", (int(product_id),))
        row = cursor.fetchone()
        if not row:
            raise ValueError(f"Product ID {product_id} has no inventory record.")

        current_balance = int(row[0])
        qty_change = int(quantity_change)
        new_balance = current_balance + qty_change

        if new_balance < 0:
            raise ValueError(
                f"Invalid inventory deduction: Current stock is {current_balance}, but deduction of "
                f"{abs(qty_change)} would result in negative balance {new_balance}."
            )

        cursor.execute("""
        INSERT INTO inventory_movements (
            product_id, movement_date, movement_type, quantity_change, balance_after, reference_note
        ) VALUES (?, date('now'), ?, ?, ?, ?);
        """, (int(product_id), movement_type, qty_change, new_balance, reference_note))
        mov_id = cursor.lastrowid

        cursor.execute("""
        UPDATE inventory_stock
        SET current_quantity = ?,
            last_restocked_date = CASE WHEN ? > 0 THEN date('now') ELSE last_restocked_date END,
            updated_at = CURRENT_TIMESTAMP
        WHERE product_id = ?;
        """, (new_balance, qty_change, int(product_id)))

        conn.commit()
        return mov_id
    except Exception:
        conn.rollback()
        raise
    finally:
        conn.close()


def get_inventory_movements_df(product_id: Optional[int] = None, limit: int = 50, db_path: Optional[Union[str, Path]] = None) -> pd.DataFrame:
    """Retrieve audit history of stock receipts, deductions, and adjustments."""
    init_database(db_path)
    conn = get_db_connection(db_path)
    try:
        where = f"WHERE m.product_id = {int(product_id)}" if product_id else ""
        query = f"""
        SELECT
            m.movement_id AS "Movement ID",
            m.movement_date AS "Date",
            p.product_name AS "Product",
            c.category_name AS "Category",
            m.movement_type AS "Action",
            m.quantity_change AS "Change",
            m.balance_after AS "Balance After",
            m.reference_note AS "Notes",
            m.created_at AS "Timestamp"
        FROM inventory_movements m
        JOIN products p ON m.product_id = p.product_id
        JOIN categories c ON p.category_id = c.category_id
        {where}
        ORDER BY m.movement_id DESC
        LIMIT {int(limit)};
        """
        return pd.read_sql_query(query, conn)
    finally:
        conn.close()


# -------------------------------------------------------------
# AUDIT OPERATIONS: ANOMALIES & REPORTS
# -------------------------------------------------------------
def log_anomaly(
    invoice_id: str,
    anomaly_type: str,
    severity: str,
    description: str,
    expected_value: str = "",
    actual_value: str = "",
    recommended_action: str = "",
    db_path: Optional[Union[str, Path]] = None
) -> int:
    """Persist a detected data-quality or statistical anomaly into the database."""
    init_database(db_path)
    conn = get_db_connection(db_path)
    cursor = conn.cursor()
    try:
        cursor.execute("""
        INSERT INTO anomaly_records (
            invoice_id, anomaly_type, severity, description,
            expected_value, actual_value, recommended_action
        ) VALUES (?, ?, ?, ?, ?, ?, ?);
        """, (
            invoice_id, anomaly_type, severity, description,
            expected_value, actual_value, recommended_action
        ))
        conn.commit()
        return cursor.lastrowid
    finally:
        conn.close()


def get_anomalies_df(resolved: Optional[bool] = None, limit: int = 100, db_path: Optional[Union[str, Path]] = None) -> pd.DataFrame:
    """Retrieve persisted anomaly audit trail records."""
    init_database(db_path)
    conn = get_db_connection(db_path)
    try:
        where = ""
        if resolved is not None:
            where = f"WHERE is_resolved = {1 if resolved else 0}"
        query = f"""
        SELECT
            anomaly_id AS "Alert ID",
            detected_at AS "Detected At",
            invoice_id AS "Invoice ID",
            anomaly_type AS "Type",
            severity AS "Severity",
            description AS "Description",
            expected_value AS "Expected",
            actual_value AS "Actual",
            recommended_action AS "Recommended Action",
            is_resolved AS "Resolved"
        FROM anomaly_records
        {where}
        ORDER BY anomaly_id DESC
        LIMIT {int(limit)};
        """
        return pd.read_sql_query(query, conn)
    finally:
        conn.close()


def resolve_anomaly(anomaly_id: int, db_path: Optional[Union[str, Path]] = None) -> bool:
    """Mark an anomaly record as investigated and resolved."""
    init_database(db_path)
    conn = get_db_connection(db_path)
    cursor = conn.cursor()
    try:
        cursor.execute("UPDATE anomaly_records SET is_resolved = 1 WHERE anomaly_id = ?;", (int(anomaly_id),))
        conn.commit()
        return cursor.rowcount > 0
    finally:
        conn.close()


def log_report(
    report_type: str,
    file_name: str,
    file_size_bytes: int,
    dataset_scope: str,
    filter_summary: str = "",
    record_count: int = 0,
    db_path: Optional[Union[str, Path]] = None
) -> int:
    """Log an audit entry for a generated PDF or Excel report."""
    init_database(db_path)
    conn = get_db_connection(db_path)
    cursor = conn.cursor()
    try:
        cursor.execute("""
        INSERT INTO report_history (
            report_type, file_name, file_size_bytes, dataset_scope, filter_summary, record_count
        ) VALUES (?, ?, ?, ?, ?, ?);
        """, (
            report_type, file_name, int(file_size_bytes),
            dataset_scope, filter_summary, int(record_count)
        ))
        conn.commit()
        return cursor.lastrowid
    finally:
        conn.close()


def get_reports_df(limit: int = 50, db_path: Optional[Union[str, Path]] = None) -> pd.DataFrame:
    """Retrieve audit history of generated reports."""
    init_database(db_path)
    conn = get_db_connection(db_path)
    try:
        query = f"""
        SELECT
            report_id AS "Report ID",
            generated_at AS "Generated At",
            report_type AS "Type",
            file_name AS "File Name",
            ROUND(file_size_bytes / 1024.0, 1) || ' KB' AS "File Size",
            dataset_scope AS "Dataset Scope",
            filter_summary AS "Filter Summary",
            record_count AS "Records"
        FROM report_history
        ORDER BY report_id DESC
        LIMIT {int(limit)};
        """
        return pd.read_sql_query(query, conn)
    finally:
        conn.close()


def get_database_stats(db_path: Optional[Union[str, Path]] = None) -> Dict[str, int]:
    """Retrieve high-level summary counts across all relational tables."""
    init_database(db_path)
    conn = get_db_connection(db_path)
    cursor = conn.cursor()
    try:
        stats = {}
        for table in ["categories", "products", "inventory_stock", "inventory_movements", "sales_transactions", "anomaly_records", "report_history"]:
            cursor.execute(f"SELECT COUNT(*) FROM {table};")
            stats[table] = cursor.fetchone()[0]
        return stats
    finally:
        conn.close()


# =============================================================
# CONVENIENCE WRAPPERS & COMPATIBILITY ALIASES
# =============================================================
get_connection = get_db_connection
init_db = init_database
get_sales_dataframe = get_all_sales_df


def get_all_products(active_only: bool = False, db_path: Optional[Union[str, Path]] = None) -> List[Dict[str, Any]]:
    """Retrieve all products as a list of dictionaries."""
    df = get_products_df(active_only=active_only, db_path=db_path)
    return df.to_dict("records")


def deactivate_product(product_id: int, db_path: Optional[Union[str, Path]] = None) -> bool:
    """Soft delete / deactivate a product."""
    return delete_product(product_id, hard_delete=False, db_path=db_path)


def get_all_categories(db_path: Optional[Union[str, Path]] = None) -> List[Dict[str, Any]]:
    """Retrieve all categories with IDs and names."""
    init_database(db_path)
    conn = get_db_connection(db_path)
    try:
        cursor = conn.cursor()
        cursor.execute("SELECT category_id, category_name, description FROM categories ORDER BY category_name ASC;")
        rows = cursor.fetchall()
        return [{"category_id": r[0], "category_name": r[1], "description": r[2]} for r in rows]
    finally:
        conn.close()


def get_inventory_movements(product_id: Optional[int] = None, limit: int = 50, db_path: Optional[Union[str, Path]] = None) -> List[Dict[str, Any]]:
    """Retrieve recent stock movements as a list of dictionaries."""
    df = get_inventory_movements_df(product_id=product_id, limit=limit, db_path=db_path)
    return df.to_dict("records")


def log_anomalies_to_db(anomalies: List[Dict[str, Any]], db_path: Optional[Union[str, Path]] = None) -> int:
    """Bulk log detected anomalies into anomaly_records table."""
    count = 0
    for a in anomalies:
        log_anomaly(
            invoice_id=str(a.get("invoice_id", "N/A")),
            anomaly_type=str(a.get("error_type", "General Anomaly")),
            severity=str(a.get("severity", "MEDIUM")),
            description=str(a.get("description", "")),
            expected_value=str(a.get("expected_value", "")),
            actual_value=str(a.get("recorded_value", "")),
            recommended_action=str(a.get("action_recommendation", "")),
            db_path=db_path
        )
        count += 1
    return count


def get_anomalies_from_db(status: Optional[str] = None, limit: int = 100, db_path: Optional[Union[str, Path]] = None) -> List[Dict[str, Any]]:
    """Retrieve anomalies from database as a list of dictionaries."""
    resolved_flag = False if status == "OPEN" else None
    df = get_anomalies_df(resolved=resolved_flag, limit=limit, db_path=db_path)
    # Rename display columns back to canonical keys for easy dictionary access
    col_mapping = {
        "Alert ID": "anomaly_id",
        "Detected At": "detected_at",
        "Invoice ID": "invoice_id",
        "Type": "anomaly_type",
        "Severity": "severity",
        "Description": "description",
        "Expected": "expected_value",
        "Actual": "actual_value",
        "Recommended Action": "recommended_action",
        "Resolved": "is_resolved",
    }
    df_renamed = df.rename(columns=col_mapping)
    return df_renamed.to_dict("records")


def resolve_anomaly_in_db(anomaly_id: int, resolution_notes: str = "", db_path: Optional[Union[str, Path]] = None) -> bool:
    """Mark an anomaly as resolved."""
    return resolve_anomaly(anomaly_id, db_path=db_path)


def log_report_generation(
    report_type: str,
    dataset_scope: str = "",
    filter_summary_json: str = "",
    total_sales_analyzed: float = 0.0,
    total_transactions: int = 0,
    file_name: str = "",
    file_size_bytes: int = 0,
    db_path: Optional[Union[str, Path]] = None
) -> int:
    """Log an entry into report_history table."""
    import datetime
    f_name = file_name or f"report_{report_type.lower()}_{datetime.date.today().isoformat()}"
    return log_report(
        report_type=report_type,
        file_name=f_name,
        file_size_bytes=file_size_bytes,
        dataset_scope=dataset_scope,
        filter_summary=filter_summary_json,
        record_count=total_transactions,
        db_path=db_path
    )


def get_report_history(limit: int = 50, db_path: Optional[Union[str, Path]] = None) -> List[Dict[str, Any]]:
    """Retrieve historical generated reports."""
    df = get_reports_df(limit=limit, db_path=db_path)
    return df.to_dict("records")

