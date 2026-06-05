"""
import_from_excel.py
────────────────────
Standalone script to bulk-import training data from an Excel workbook
into the Training Tracker database (SQLite locally or PostgreSQL on cloud).

Expected Excel sheets
─────────────────────
  • Employees        → columns: Employee Name, Department, Hire Date
  • Courses          → columns: Course Name, Category, Duration Hours, Due Within Days
  • Training_Records → columns: Employee Name, Course Name, Status,
                                Completion Date, Assigned Date   (all optional except first two)

Usage
─────
  # Import from default file (training_db.xlsx in same folder)
  python import_from_excel.py

  # Import from a specific file
  python import_from_excel.py --file path/to/your_file.xlsx

  # Append instead of replace (keep existing DB rows)
  python import_from_excel.py --mode append

  # Dry-run – preview without writing
  python import_from_excel.py --dry-run

  # Point to a PostgreSQL database
  DATABASE_URL=postgresql://user:pass@host/db python import_from_excel.py
"""

import os
import sys
import argparse
from datetime import date, datetime
from pathlib import Path

try:
    import pandas as pd
except ImportError:
    sys.exit("pandas is required: pip install pandas openpyxl")

try:
    from sqlalchemy import create_engine, text
    from sqlalchemy.pool import StaticPool
except ImportError:
    sys.exit("SQLAlchemy is required: pip install sqlalchemy")

# ─── Config ───────────────────────────────────────────────────────────────────

DEFAULT_EXCEL = Path(__file__).parent / "training_db.xlsx"
DB_PATH       = Path(__file__).parent / "training_tracker.db"
DATABASE_URL  = os.getenv("DATABASE_URL", "").strip()


# ─── DB helpers ───────────────────────────────────────────────────────────────

def build_engine():
    url = DATABASE_URL
    if url.startswith("postgres://"):
        url = url.replace("postgres://", "postgresql+psycopg2://", 1)
    elif url.startswith("postgresql://") and "+psycopg2" not in url:
        url = url.replace("postgresql://", "postgresql+psycopg2://", 1)
    if not url:
        return create_engine(
            f"sqlite:///{DB_PATH}",
            connect_args={"check_same_thread": False},
            poolclass=StaticPool,
        )
    return create_engine(url, pool_pre_ping=True)


def ensure_tables(conn, is_sqlite):
    _exec(conn, is_sqlite, """
        CREATE TABLE IF NOT EXISTS employees (
            employee_id   TEXT PRIMARY KEY,
            employee_name TEXT UNIQUE NOT NULL,
            department    TEXT NOT NULL,
            hire_date     TEXT NOT NULL
        )""")
    _exec(conn, is_sqlite, """
        CREATE TABLE IF NOT EXISTS courses (
            course_id       TEXT PRIMARY KEY,
            course_name     TEXT UNIQUE NOT NULL,
            category        TEXT NOT NULL,
            duration_hours  REAL NOT NULL,
            due_within_days INTEGER NOT NULL
        )""")
    _exec(conn, is_sqlite, """
        CREATE TABLE IF NOT EXISTS training_records (
            record_id       TEXT PRIMARY KEY,
            employee_name   TEXT NOT NULL,
            course_name     TEXT NOT NULL,
            status          TEXT NOT NULL,
            assigned_date   TEXT NOT NULL,
            completion_date TEXT,
            created_at      TEXT DEFAULT CURRENT_TIMESTAMP
        )""")


def _exec(conn, is_sqlite, sql, params=()):
    if is_sqlite:
        conn.exec_driver_sql(sql, params) if params else conn.exec_driver_sql(sql)
    else:
        if params:
            parts = sql.split("?")
            named = {}
            rebuilt = parts[0]
            for i, v in enumerate(params):
                key = f"p{i}"
                named[key] = v
                rebuilt += f":{key}" + parts[i + 1]
            conn.execute(text(rebuilt), named)
        else:
            conn.execute(text(sql))


def count(conn, is_sqlite, table):
    row = _exec(conn, is_sqlite, f"SELECT COUNT(*) FROM {table}") \
        if False else conn.exec_driver_sql(f"SELECT COUNT(*) FROM {table}") \
        if is_sqlite else conn.execute(text(f"SELECT COUNT(*) FROM {table}"))
    return row.fetchone()[0]


# ─── Column finder ────────────────────────────────────────────────────────────

def pick(df, candidates):
    lmap = {str(c).strip().lower(): c for c in df.columns}
    for cand in candidates:
        if cand.lower() in lmap:
            return lmap[cand.lower()]
    return None


# ─── Importers ────────────────────────────────────────────────────────────────

def import_employees(conn, is_sqlite, df, mode, dry_run):
    name_col = pick(df, ["Employee Name", "Employee_Name", "Name", "Employee"])
    dept_col = pick(df, ["Department", "Dept"])
    hire_col = pick(df, ["Hire Date", "Hire_Date", "Start Date", "Join Date"])

    if not name_col:
        print("  ⚠  Employees sheet: cannot find Name column — skipped.")
        return 0

    if mode == "replace" and not dry_run:
        _exec(conn, is_sqlite, "DELETE FROM employees")

    # Get existing count for ID generation
    existing = conn.exec_driver_sql("SELECT COUNT(*) FROM employees").fetchone()[0] \
        if is_sqlite else conn.execute(text("SELECT COUNT(*) FROM employees")).fetchone()[0]

    rows = df.dropna(subset=[name_col]).copy()
    rows[name_col] = rows[name_col].astype(str).str.strip()
    rows = rows[rows[name_col] != ""]

    inserted = skipped = 0
    for i, row in enumerate(rows.itertuples(index=False), 1):
        rm = dict(zip(rows.columns, row))
        emp_name   = str(rm[name_col]).strip()
        department = str(rm.get(dept_col, "Other") or "Other").strip() if dept_col else "Other"
        hd         = pd.to_datetime(rm.get(hire_col), errors="coerce") if hire_col else pd.NaT
        hire_txt   = hd.strftime("%Y-%m-%d") if pd.notna(hd) else date.today().strftime("%Y-%m-%d")
        eid        = f"EMP{str(existing + i).zfill(3)}"

        if dry_run:
            print(f"    [DRY] Employee: {emp_name} | {department} | {hire_txt}")
            inserted += 1
            continue
        try:
            _exec(conn, is_sqlite,
                  "INSERT INTO employees VALUES (?,?,?,?)",
                  (eid, emp_name, department or "Other", hire_txt))
            inserted += 1
        except Exception:
            skipped += 1  # unique constraint – already exists

    return inserted, skipped


def import_courses(conn, is_sqlite, df, mode, dry_run):
    name_col = pick(df, ["Course Name", "Course_Name", "Course", "Training"])
    cat_col  = pick(df, ["Category", "Type"])
    dur_col  = pick(df, ["Duration Hours", "Duration_Hours", "Duration"])
    due_col  = pick(df, ["Due Within Days", "Due_Within_Days", "Due Days"])

    if not name_col:
        print("  ⚠  Courses sheet: cannot find Name column — skipped.")
        return 0, 0

    if mode == "replace" and not dry_run:
        _exec(conn, is_sqlite, "DELETE FROM courses")

    existing = conn.exec_driver_sql("SELECT COUNT(*) FROM courses").fetchone()[0] \
        if is_sqlite else conn.execute(text("SELECT COUNT(*) FROM courses")).fetchone()[0]

    rows = df.dropna(subset=[name_col]).copy()
    rows[name_col] = rows[name_col].astype(str).str.strip()
    rows = rows[rows[name_col] != ""]

    inserted = skipped = 0
    for i, row in enumerate(rows.itertuples(index=False), 1):
        rm       = dict(zip(rows.columns, row))
        crs_name = str(rm[name_col]).strip()
        category = str(rm.get(cat_col, "Other") or "Other").strip() if cat_col else "Other"
        try:    duration = float(rm.get(dur_col, 1) or 1) if dur_col else 1.0
        except: duration = 1.0
        try:    due_days = int(rm.get(due_col, 30) or 30) if due_col else 30
        except: due_days = 30
        cid = f"CRS{str(existing + i).zfill(3)}"

        if dry_run:
            print(f"    [DRY] Course: {crs_name} | {category} | {duration}h | due {due_days}d")
            inserted += 1
            continue
        try:
            _exec(conn, is_sqlite,
                  "INSERT INTO courses VALUES (?,?,?,?,?)",
                  (cid, crs_name, category or "Other", duration, due_days))
            inserted += 1
        except Exception:
            skipped += 1

    return inserted, skipped


def import_records(conn, is_sqlite, df, mode, dry_run):
    emp_col    = pick(df, ["Employee Name", "Employee_Name", "Employee"])
    course_col = pick(df, ["Course Name", "Course_Name", "Course"])
    status_col = pick(df, ["Status", "Training Status"])
    comp_col   = pick(df, ["Completion Date", "Completion_Date", "Date"])
    asgn_col   = pick(df, ["Assigned Date", "Assigned_Date", "Enrollment Date"])

    if not emp_col or not course_col:
        print("  ⚠  Training_Records sheet: cannot find Employee or Course column — skipped.")
        return 0, 0

    if mode == "replace" and not dry_run:
        _exec(conn, is_sqlite, "DELETE FROM training_records")

    existing = conn.exec_driver_sql("SELECT COUNT(*) FROM training_records").fetchone()[0] \
        if is_sqlite else conn.execute(text("SELECT COUNT(*) FROM training_records")).fetchone()[0]

    rows = df.dropna(subset=[emp_col, course_col]).copy()
    inserted = skipped = 0

    for i, row in enumerate(rows.itertuples(index=False), 1):
        rm         = dict(zip(rows.columns, row))
        emp_name   = str(rm[emp_col]).strip()
        crs_name   = str(rm[course_col]).strip()
        status     = str(rm.get(status_col, "Not Started") or "Not Started").strip() if status_col else "Not Started"
        comp_dt    = pd.to_datetime(rm.get(comp_col), errors="coerce") if comp_col else pd.NaT
        asgn_dt    = pd.to_datetime(rm.get(asgn_col), errors="coerce") if asgn_col else pd.NaT
        comp_txt   = comp_dt.strftime("%Y-%m-%d") if pd.notna(comp_dt) else ""
        asgn_txt   = asgn_dt.strftime("%Y-%m-%d") if pd.notna(asgn_dt) else date.today().strftime("%Y-%m-%d")
        rid        = f"REC{str(existing + i).zfill(4)}"

        if dry_run:
            print(f"    [DRY] Record: {emp_name} → {crs_name} | {status} | {asgn_txt}")
            inserted += 1
            continue
        try:
            _exec(conn, is_sqlite,
                  "INSERT INTO training_records VALUES (?,?,?,?,?,?,CURRENT_TIMESTAMP)",
                  (rid, emp_name, crs_name, status, asgn_txt, comp_txt))
            inserted += 1
        except Exception:
            skipped += 1

    return inserted, skipped


# ─── Main ─────────────────────────────────────────────────────────────────────

def main():
    parser = argparse.ArgumentParser(description="Import Excel data into Training Tracker DB")
    parser.add_argument("--file",    default=str(DEFAULT_EXCEL), help="Path to Excel file")
    parser.add_argument("--mode",    default="append", choices=["append", "replace"],
                        help="append = keep existing rows; replace = clear table first")
    parser.add_argument("--dry-run", action="store_true", help="Preview without writing to DB")
    parser.add_argument("--sheet",   default="all", choices=["all", "employees", "courses", "records"],
                        help="Which sheet(s) to import")
    args = parser.parse_args()

    excel_path = Path(args.file)
    if not excel_path.exists():
        sys.exit(f"File not found: {excel_path}")

    print(f"\n{'='*58}")
    print(f"  Training Tracker — Excel Import Tool")
    print(f"{'='*58}")
    print(f"  File   : {excel_path.name}")
    print(f"  Mode   : {args.mode.upper()}  {'(DRY RUN — no changes written)' if args.dry_run else ''}")
    print(f"  DB     : {'PostgreSQL' if DATABASE_URL else f'SQLite ({DB_PATH.name})'}")
    print(f"{'='*58}\n")

    # Load workbook
    xls = pd.ExcelFile(excel_path)
    available = {s.lower(): s for s in xls.sheet_names}

    engine   = build_engine()
    is_sqlite = engine.url.get_backend_name() == "sqlite"

    with engine.connect() as conn:
        trans = conn.begin()
        try:
            ensure_tables(conn, is_sqlite)

            # Employees
            if args.sheet in ("all", "employees"):
                sheet_name = available.get("employees")
                if sheet_name:
                    df = pd.read_excel(excel_path, sheet_name=sheet_name)
                    ins, skip = import_employees(conn, is_sqlite, df, args.mode, args.dry_run)
                    print(f"  Employees      → inserted: {ins}  |  skipped (duplicate): {skip}")
                else:
                    print("  Employees      → sheet not found in workbook")

            # Courses
            if args.sheet in ("all", "courses"):
                sheet_name = available.get("courses")
                if sheet_name:
                    df = pd.read_excel(excel_path, sheet_name=sheet_name)
                    ins, skip = import_courses(conn, is_sqlite, df, args.mode, args.dry_run)
                    print(f"  Courses        → inserted: {ins}  |  skipped (duplicate): {skip}")
                else:
                    print("  Courses        → sheet not found in workbook")

            # Training Records
            if args.sheet in ("all", "records"):
                for candidate in ("training_records", "records", "training records"):
                    sheet_name = available.get(candidate)
                    if sheet_name:
                        break
                if sheet_name:
                    df = pd.read_excel(excel_path, sheet_name=sheet_name)
                    ins, skip = import_records(conn, is_sqlite, df, args.mode, args.dry_run)
                    print(f"  Training Records → inserted: {ins}  |  skipped: {skip}")
                else:
                    print("  Training Records → sheet not found in workbook")

            if not args.dry_run:
                trans.commit()
                print(f"\n  ✅  Import complete. Database updated successfully.")
            else:
                trans.rollback()
                print(f"\n  ℹ  Dry run complete. No data was written.")

        except Exception as e:
            trans.rollback()
            print(f"\n  ❌  Import failed: {e}")
            sys.exit(1)

    print(f"{'='*58}\n")


if __name__ == "__main__":
    main()
