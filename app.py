import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
import os
from datetime import datetime, date, timedelta
from pathlib import Path
from io import BytesIO
from contextlib import contextmanager
import random
from sqlalchemy import create_engine, text

# ═══════════════════════════════════════════════════════════════
# CONFIGURATION
# ═══════════════════════════════════════════════════════════════

DB_PATH = Path("training_tracker.db")
EXCEL_SOURCE_PATH = Path("training_db.xlsx")
DATABASE_URL = os.getenv("DATABASE_URL", "").strip()
APP_ACCESS_CODE = os.getenv("APP_ACCESS_CODE", "").strip()
STATUS_OPTIONS = ["Completed", "In Progress", "Not Started", "Overdue"]
STATUS_COLORS = {
    "Completed": "#00c853",
    "In Progress": "#ff9100",
    "Not Started": "#78909c",
    "Overdue": "#ff1744",
}
STATUS_ICONS = {
    "Completed": "&#9989;",
    "In Progress": "&#9203;",
    "Not Started": "&#9898;",
    "Overdue": "&#128308;",
}
DEPARTMENTS = [
    "Engineering", "Finance", "HR", "IT", "Legal",
    "Marketing", "Operations", "Sales", "Other",
]
CATEGORIES = [
    "Compliance", "Technical", "Soft Skills",
    "Leadership", "Onboarding", "Other",
]

# ═══════════════════════════════════════════════════════════════
# PREMIUM CSS THEME
# ═══════════════════════════════════════════════════════════════

THEME_CSS = """
<style>
/* ── Global ────────────────────────────────────────────── */
@import url('https://fonts.googleapis.com/css2?family=Inter:wght@300;400;500;600;700;800&display=swap');

.stApp {
    font-family: 'Inter', sans-serif;
}
.block-container {
    padding-top: 1.5rem;
    padding-bottom: 2rem;
    max-width: 1200px;
}

/* ── Sidebar ── Dark Gradient ─────────────────────────── */
section[data-testid="stSidebar"] {
    background: linear-gradient(180deg, #0f0c29 0%, #302b63 50%, #24243e 100%) !important;
}
section[data-testid="stSidebar"] * {
    color: #c8c8e0 !important;
}
section[data-testid="stSidebar"] h1,
section[data-testid="stSidebar"] h2,
section[data-testid="stSidebar"] h3 {
    color: #ffffff !important;
    font-weight: 700 !important;
}
section[data-testid="stSidebar"] .stRadio label {
    color: #e0e0f0 !important;
    font-weight: 500 !important;
    font-size: 0.95rem !important;
    padding: 0.3rem 0 !important;
    transition: all 0.2s ease;
}
section[data-testid="stSidebar"] .stRadio label:hover {
    color: #ffffff !important;
    padding-left: 0.3rem !important;
}
section[data-testid="stSidebar"] hr {
    border-color: rgba(255,255,255,0.08) !important;
}
section[data-testid="stSidebar"] .stCaption {
    background: rgba(255,255,255,0.05);
    border-radius: 0.75rem;
    padding: 0.75rem !important;
    border: 1px solid rgba(255,255,255,0.06);
}

/* ── Metric Cards ─────────────────────────────────────── */
div[data-testid="stMetric"] {
    background: white;
    border-radius: 1rem;
    padding: 1.25rem 1.5rem;
    box-shadow: 0 2px 16px rgba(0,0,0,0.06);
    border: 1px solid rgba(0,0,0,0.04);
    transition: transform 0.2s ease, box-shadow 0.2s ease;
}
div[data-testid="stMetric"]:hover {
    transform: translateY(-3px);
    box-shadow: 0 8px 25px rgba(0,0,0,0.1);
}
div[data-testid="stMetric"] label {
    color: #6b7280 !important;
    font-weight: 600 !important;
    font-size: 0.8rem !important;
    text-transform: uppercase;
    letter-spacing: 0.5px;
}
div[data-testid="stMetric"] [data-testid="stMetricValue"] {
    font-weight: 800 !important;
    font-size: 2rem !important;
    color: #1a1a2e !important;
}

/* ── Forms ─────────────────────────────────────────────── */
[data-testid="stForm"] {
    background: white;
    padding: 2rem 2.5rem;
    border-radius: 1.25rem;
    box-shadow: 0 4px 20px rgba(0,0,0,0.06);
    border: 1px solid rgba(0,0,0,0.04);
}

/* ── Submit Button ─────────────────────────────────────── */
.stFormSubmitButton > button {
    background: linear-gradient(135deg, #667eea 0%, #764ba2 100%) !important;
    color: white !important;
    border: none !important;
    border-radius: 0.75rem !important;
    padding: 0.7rem 2.5rem !important;
    font-weight: 700 !important;
    font-size: 1rem !important;
    letter-spacing: 0.5px;
    box-shadow: 0 4px 18px rgba(102, 126, 234, 0.35);
    transition: all 0.3s cubic-bezier(0.4,0,0.2,1) !important;
}
.stFormSubmitButton > button:hover {
    transform: translateY(-2px) !important;
    box-shadow: 0 8px 25px rgba(102, 126, 234, 0.45) !important;
}
.stFormSubmitButton > button:active {
    transform: translateY(0) !important;
}

/* ── Regular Buttons ───────────────────────────────────── */
.stButton > button {
    border-radius: 0.75rem !important;
    font-weight: 600 !important;
    padding: 0.5rem 1.5rem !important;
    transition: all 0.3s ease !important;
    border: 2px solid #667eea !important;
    color: #667eea !important;
    background: white !important;
}
.stButton > button:hover {
    background: #667eea !important;
    color: white !important;
    transform: translateY(-1px) !important;
}
button[kind="primary"] {
    background: linear-gradient(135deg, #ff6b6b 0%, #ee5a24 100%) !important;
    color: white !important;
    border: none !important;
}

/* ── Download Buttons ──────────────────────────────────── */
.stDownloadButton > button {
    background: linear-gradient(135deg, #11998e 0%, #38ef7d 100%) !important;
    color: white !important;
    border: none !important;
    border-radius: 0.75rem !important;
    font-weight: 700 !important;
    box-shadow: 0 4px 15px rgba(17, 153, 142, 0.3);
    transition: all 0.3s ease !important;
}
.stDownloadButton > button:hover {
    transform: translateY(-2px) !important;
    box-shadow: 0 6px 20px rgba(17, 153, 142, 0.4) !important;
}

/* ── Tabs ──────────────────────────────────────────────── */
.stTabs [data-baseweb="tab-list"] {
    gap: 0.25rem;
    background: white;
    border-radius: 1rem;
    padding: 0.35rem;
    box-shadow: 0 2px 10px rgba(0,0,0,0.04);
    border: 1px solid rgba(0,0,0,0.04);
}
.stTabs [data-baseweb="tab"] {
    border-radius: 0.75rem;
    padding: 0.6rem 1.5rem;
    font-weight: 600;
    font-size: 0.9rem;
}
.stTabs [aria-selected="true"] {
    background: linear-gradient(135deg, #667eea 0%, #764ba2 100%) !important;
    color: white !important;
    box-shadow: 0 4px 12px rgba(102, 126, 234, 0.3);
}

/* ── Alerts ────────────────────────────────────────────── */
.stSuccess { border-radius: 0.75rem; }
.stWarning { border-radius: 0.75rem; }
.stError   { border-radius: 0.75rem; }
.stInfo    { border-radius: 0.75rem; }

/* ── DataFrames ────────────────────────────────────────── */
[data-testid="stDataFrame"] {
    border-radius: 0.75rem;
    overflow: hidden;
    box-shadow: 0 2px 10px rgba(0,0,0,0.05);
}

/* ── Select boxes / Inputs ─────────────────────────────── */
.stSelectbox > div > div,
.stTextInput > div > div > input,
.stNumberInput > div > div > input,
.stDateInput > div > div > input {
    border-radius: 0.6rem !important;
    border: 2px solid #e0e0e0 !important;
    transition: border-color 0.2s ease !important;
}
.stSelectbox > div > div:focus-within,
.stTextInput > div > div > input:focus,
.stNumberInput > div > div > input:focus {
    border-color: #667eea !important;
    box-shadow: 0 0 0 3px rgba(102, 126, 234, 0.15) !important;
}

/* ── Multiselect ───────────────────────────────────────── */
.stMultiSelect > div > div {
    border-radius: 0.6rem !important;
}
span[data-baseweb="tag"] {
    background: linear-gradient(135deg, #667eea 0%, #764ba2 100%) !important;
    border-radius: 0.5rem !important;
    color: white !important;
}

/* ── Divider ───────────────────────────────────────────── */
hr {
    border: none;
    height: 1px;
    background: linear-gradient(90deg, transparent 0%, #d0d0e0 50%, transparent 100%);
    margin: 1.5rem 0;
}

/* ── Expander ──────────────────────────────────────────── */
.streamlit-expanderHeader {
    font-weight: 600;
    border-radius: 0.75rem;
}
</style>
"""

# ═══════════════════════════════════════════════════════════════
# DATABASE LAYER (PostgreSQL for cloud + SQLite fallback)
# ═══════════════════════════════════════════════════════════════

def _build_engine():
    url = DATABASE_URL
    if url.startswith("postgres://"):
        url = url.replace("postgres://", "postgresql+psycopg2://", 1)
    elif url.startswith("postgresql://") and "+psycopg2" not in url:
        url = url.replace("postgresql://", "postgresql+psycopg2://", 1)

    if not url:
        return create_engine(
            f"sqlite:///{DB_PATH}",
            connect_args={"check_same_thread": False},
            future=True,
        )

    return create_engine(url, pool_pre_ping=True, future=True)


DB_ENGINE = _build_engine()
DB_IS_SQLITE = DB_ENGINE.url.get_backend_name() == "sqlite"


def db_execute(conn, query, params=None):
    """Execute SQL with placeholder compatibility across sqlite and postgres."""
    if params is None:
        params = ()

    if isinstance(params, dict):
        return conn.execute(text(query), params)

    if DB_IS_SQLITE:
        return conn.exec_driver_sql(query, params)

    if "?" not in query:
        return conn.execute(text(query))

    parts = query.split("?")
    named = {}
    rebuilt = parts[0]
    for idx, value in enumerate(params):
        key = f"p{idx}"
        named[key] = value
        rebuilt += f":{key}{parts[idx + 1]}"
    return conn.execute(text(rebuilt), named)

@contextmanager
def get_db():
    """Database connection that supports SQLite and PostgreSQL."""
    conn = DB_ENGINE.connect()
    trans = conn.begin()
    if DB_IS_SQLITE:
        conn.exec_driver_sql("PRAGMA journal_mode=WAL")
        conn.exec_driver_sql("PRAGMA busy_timeout=10000")
        conn.exec_driver_sql("PRAGMA synchronous=NORMAL")
    try:
        yield conn
        trans.commit()
    except Exception:
        trans.rollback()
        raise
    finally:
        conn.close()


def require_access():
    """Optional lightweight access code prompt for shared deployments."""
    if not APP_ACCESS_CODE:
        return

    if st.session_state.get("authenticated", False):
        return

    st.title("Employee Training Tracker")
    st.info("Secure mode enabled. Enter access code to continue.")
    code = st.text_input("Access Code", type="password")
    if st.button("Unlock", use_container_width=True):
        if code == APP_ACCESS_CODE:
            st.session_state["authenticated"] = True
            st.rerun()
        else:
            st.error("Invalid access code.")
    st.stop()

def init_database():
    """Create tables and import from Excel on first run, else seed sample data."""
    with get_db() as conn:
        db_execute(conn, """CREATE TABLE IF NOT EXISTS employees (
            employee_id TEXT PRIMARY KEY,
            employee_name TEXT UNIQUE NOT NULL,
            department TEXT NOT NULL,
            hire_date TEXT NOT NULL
        )""")
        db_execute(conn, """CREATE TABLE IF NOT EXISTS courses (
            course_id TEXT PRIMARY KEY,
            course_name TEXT UNIQUE NOT NULL,
            category TEXT NOT NULL,
            duration_hours REAL NOT NULL,
            due_within_days INTEGER NOT NULL
        )""")
        db_execute(conn, """CREATE TABLE IF NOT EXISTS training_records (
            record_id TEXT PRIMARY KEY,
            employee_name TEXT NOT NULL,
            course_name TEXT NOT NULL,
            status TEXT NOT NULL,
            assigned_date TEXT NOT NULL,
            completion_date TEXT,
            created_at TEXT DEFAULT CURRENT_TIMESTAMP
        )""")
        count = db_execute(conn, "SELECT COUNT(*) FROM employees").fetchone()[0]
        if count == 0:
            if EXCEL_SOURCE_PATH.exists():
                try:
                    _import_from_excel(conn, EXCEL_SOURCE_PATH)
                except Exception:
                    # Fall back to sample data if Excel format is invalid.
                    _seed_sample_data(conn)
            else:
                _seed_sample_data(conn)

def _pick_column(df, candidates):
    """Return first matching column in df from candidate names (case-insensitive)."""
    normalized = {str(c).strip().lower(): c for c in df.columns}
    for cand in candidates:
        key = cand.strip().lower()
        if key in normalized:
            return normalized[key]
    return None

def _import_from_excel(conn, excel_path):
    """Import data from training_db.xlsx sheets into database tables."""
    employees_df = pd.read_excel(excel_path, sheet_name="Employees")
    courses_df = pd.read_excel(excel_path, sheet_name="Courses")
    records_df = pd.read_excel(excel_path, sheet_name="Training_Records")

    # Reset tables to a clean imported state.
    db_execute(conn, "DELETE FROM training_records")
    db_execute(conn, "DELETE FROM courses")
    db_execute(conn, "DELETE FROM employees")

    emp_name_col = _pick_column(employees_df, ["Employee Name", "Employee_Name", "Name", "Employee"])
    emp_dept_col = _pick_column(employees_df, ["Department", "Dept"])
    emp_hire_col = _pick_column(employees_df, ["Hire Date", "Hire_Date", "Start Date"])

    course_name_col = _pick_column(courses_df, ["Course Name", "Course_Name", "Course", "Training"])
    course_cat_col = _pick_column(courses_df, ["Category", "Type"])
    course_dur_col = _pick_column(courses_df, ["Duration Hours", "Duration_Hours", "Duration"])
    course_due_col = _pick_column(courses_df, ["Due Within Days", "Due_Within_Days", "Due Days"])

    rec_emp_col = _pick_column(records_df, ["Employee Name", "Employee_Name", "Employee"])
    rec_course_col = _pick_column(records_df, ["Course Name", "Course_Name", "Course"])
    rec_status_col = _pick_column(records_df, ["Status", "Training Status"])
    rec_completion_col = _pick_column(records_df, ["Completion Date", "Completion_Date", "Date"])
    rec_assigned_col = _pick_column(records_df, ["Assigned Date", "Assigned_Date", "Enrollment Date"])

    if emp_name_col is None or course_name_col is None or rec_emp_col is None or rec_course_col is None:
        raise ValueError("Excel sheet columns are missing required name fields.")

    # Employees
    emp_rows = employees_df.dropna(subset=[emp_name_col]).copy()
    emp_rows[emp_name_col] = emp_rows[emp_name_col].astype(str).str.strip()
    emp_rows = emp_rows[emp_rows[emp_name_col] != ""]

    for idx, row in enumerate(emp_rows.itertuples(index=False), 1):
        row_map = dict(zip(emp_rows.columns, row))
        emp_name = str(row_map.get(emp_name_col, "")).strip()
        department = str(row_map.get(emp_dept_col, "Other") or "Other").strip() if emp_dept_col else "Other"
        hire_date_raw = row_map.get(emp_hire_col) if emp_hire_col else None
        hire_date = pd.to_datetime(hire_date_raw, errors="coerce")
        hire_date_txt = hire_date.strftime("%Y-%m-%d") if pd.notna(hire_date) else date.today().strftime("%Y-%m-%d")
        db_execute(
            conn,
            "INSERT INTO employees VALUES (?,?,?,?)",
            (f"EMP{str(idx).zfill(3)}", emp_name, department or "Other", hire_date_txt),
        )

    # Courses
    crs_rows = courses_df.dropna(subset=[course_name_col]).copy()
    crs_rows[course_name_col] = crs_rows[course_name_col].astype(str).str.strip()
    crs_rows = crs_rows[crs_rows[course_name_col] != ""]

    for idx, row in enumerate(crs_rows.itertuples(index=False), 1):
        row_map = dict(zip(crs_rows.columns, row))
        course_name = str(row_map.get(course_name_col, "")).strip()
        category = str(row_map.get(course_cat_col, "Other") or "Other").strip() if course_cat_col else "Other"
        duration = row_map.get(course_dur_col, 1) if course_dur_col else 1
        due_days = row_map.get(course_due_col, 30) if course_due_col else 30
        try:
            duration = float(duration)
        except Exception:
            duration = 1.0
        try:
            due_days = int(due_days)
        except Exception:
            due_days = 30
        db_execute(
            conn,
            "INSERT INTO courses VALUES (?,?,?,?,?)",
            (f"CRS{str(idx).zfill(3)}", course_name, category or "Other", duration, due_days),
        )

    # Records
    rec_rows = records_df.dropna(subset=[rec_emp_col, rec_course_col]).copy()
    for idx, row in enumerate(rec_rows.itertuples(index=False), 1):
        row_map = dict(zip(rec_rows.columns, row))
        emp_name = str(row_map.get(rec_emp_col, "")).strip()
        course_name = str(row_map.get(rec_course_col, "")).strip()
        status = str(row_map.get(rec_status_col, "Not Started") or "Not Started").strip() if rec_status_col else "Not Started"

        completion_raw = row_map.get(rec_completion_col) if rec_completion_col else None
        completion_dt = pd.to_datetime(completion_raw, errors="coerce")
        completion_txt = completion_dt.strftime("%Y-%m-%d") if pd.notna(completion_dt) else ""

        assigned_raw = row_map.get(rec_assigned_col) if rec_assigned_col else None
        assigned_dt = pd.to_datetime(assigned_raw, errors="coerce")
        assigned_txt = assigned_dt.strftime("%Y-%m-%d") if pd.notna(assigned_dt) else date.today().strftime("%Y-%m-%d")

        db_execute(
            conn,
            "INSERT INTO training_records VALUES (?,?,?,?,?,?,CURRENT_TIMESTAMP)",
            (f"REC{str(idx).zfill(4)}", emp_name, course_name, status, assigned_txt, completion_txt),
        )

def _seed_sample_data(conn):
    """Insert realistic sample data for demonstration."""
    names = [
        ("Alice Johnson","Engineering"), ("Bob Smith","Engineering"),
        ("Carol White","HR"), ("David Brown","Marketing"),
        ("Eva Martinez","Engineering"), ("Frank Wilson","Finance"),
        ("Grace Lee","HR"), ("Henry Taylor","Marketing"),
        ("Irene Clark","Finance"), ("Jack Davis","Engineering"),
        ("Karen Hall","HR"), ("Leo Adams","Finance"),
        ("Mona Scott","Marketing"), ("Nick Young","Engineering"),
        ("Olivia King","HR"),
    ]
    for i, (name, dept) in enumerate(names, 1):
        hd = (datetime(2020,1,15)+timedelta(days=random.randint(0,1500))).strftime("%Y-%m-%d")
        db_execute(conn, "INSERT INTO employees VALUES (?,?,?,?)",
                   (f"EMP{str(i).zfill(3)}", name, dept, hd))

    crses = [
        ("Workplace Safety","Compliance",2,30),
        ("Data Privacy 101","Compliance",1.5,30),
        ("Leadership Basics","Soft Skills",4,60),
        ("Python for Analysts","Technical",8,90),
        ("Diversity and Inclusion","Compliance",1,30),
        ("Project Management","Soft Skills",6,60),
        ("Cloud Computing","Technical",10,90),
        ("Effective Communication","Soft Skills",3,45),
    ]
    for i, (cn, cat, dur, dd) in enumerate(crses, 1):
        db_execute(conn, "INSERT INTO courses VALUES (?,?,?,?,?)",
                   (f"CRS{str(i).zfill(3)}", cn, cat, dur, dd))

    emp_names = [n for n, _ in names]
    crs_names = [c for c, _, _, _ in crses]
    statuses = STATUS_OPTIONS
    for i in range(1, 41):
        emp = random.choice(emp_names)
        crs = random.choice(crs_names)
        sts = random.choice(statuses)
        ad = (datetime.now()-timedelta(days=random.randint(5,120))).strftime("%Y-%m-%d")
        cd = ""
        if sts == "Completed":
            cd = (datetime.strptime(ad,"%Y-%m-%d")+timedelta(days=random.randint(1,30))).strftime("%Y-%m-%d")
        db_execute(conn, "INSERT INTO training_records VALUES (?,?,?,?,?,?,CURRENT_TIMESTAMP)",
                   (f"REC{str(i).zfill(4)}", emp, crs, sts, ad, cd))

# ── Read functions (cached with short TTL so all users see updates) ──

@st.cache_data(ttl=5)
def get_employees():
    with get_db() as conn:
        rows = db_execute(conn, "SELECT * FROM employees ORDER BY employee_name").mappings().all()
    df = pd.DataFrame(rows)
    if df.empty:
        return pd.DataFrame(columns=["Employee_ID", "Employee_Name", "Department", "Hire_Date"])
    df = df.rename(columns={
        "employee_id": "Employee_ID",
        "employee_name": "Employee_Name",
        "department": "Department",
        "hire_date": "Hire_Date",
    })
    df["Hire_Date"] = pd.to_datetime(df["Hire_Date"], errors="coerce")
    return df

@st.cache_data(ttl=5)
def get_courses():
    with get_db() as conn:
        rows = db_execute(conn, "SELECT * FROM courses ORDER BY course_name").mappings().all()
    df = pd.DataFrame(rows)
    if df.empty:
        return pd.DataFrame(columns=["Course_ID", "Course_Name", "Category", "Duration_Hours", "Due_Within_Days"])
    return df.rename(columns={
        "course_id": "Course_ID",
        "course_name": "Course_Name",
        "category": "Category",
        "duration_hours": "Duration_Hours",
        "due_within_days": "Due_Within_Days",
    })

@st.cache_data(ttl=5)
def get_records():
    with get_db() as conn:
        rows = db_execute(conn, "SELECT * FROM training_records ORDER BY created_at DESC").mappings().all()
    df = pd.DataFrame(rows)
    if df.empty:
        return pd.DataFrame(columns=["Record_ID", "Employee_Name", "Course_Name", "Status", "Assigned_Date", "Completion_Date", "Created_At"])
    df = df.rename(columns={
        "record_id": "Record_ID",
        "employee_name": "Employee_Name",
        "course_name": "Course_Name",
        "status": "Status",
        "assigned_date": "Assigned_Date",
        "completion_date": "Completion_Date",
        "created_at": "Created_At",
    })
    df["Assigned_Date"] = pd.to_datetime(df["Assigned_Date"], errors="coerce")
    df["Completion_Date"] = pd.to_datetime(df["Completion_Date"], errors="coerce")
    return df

# ── Write functions ──────────────────────────────────────────

def add_employee(name, department, hire_date):
    with get_db() as conn:
        count = db_execute(conn, "SELECT COUNT(*) FROM employees").fetchone()[0]
        eid = f"EMP{str(count+1).zfill(3)}"
        db_execute(conn, "INSERT INTO employees VALUES (?,?,?,?)",
                   (eid, name.strip(), department, hire_date))
    st.cache_data.clear()

def add_course(name, category, duration, due_days):
    with get_db() as conn:
        count = db_execute(conn, "SELECT COUNT(*) FROM courses").fetchone()[0]
        cid = f"CRS{str(count+1).zfill(3)}"
        db_execute(conn, "INSERT INTO courses VALUES (?,?,?,?,?)",
                   (cid, name.strip(), category, duration, int(due_days)))
    st.cache_data.clear()

def add_record(emp, course, status, assigned, completion):
    with get_db() as conn:
        count = db_execute(conn, "SELECT COUNT(*) FROM training_records").fetchone()[0]
        rid = f"REC{str(count+1).zfill(4)}"
        cd = completion if status == "Completed" else ""
        db_execute(conn, "INSERT INTO training_records VALUES (?,?,?,?,?,?,CURRENT_TIMESTAMP)",
                   (rid, emp, course, status, assigned, cd))
    st.cache_data.clear()

def delete_employee(name):
    with get_db() as conn:
        db_execute(conn, "DELETE FROM employees WHERE employee_name=?", (name,))
    st.cache_data.clear()

def delete_course(name):
    with get_db() as conn:
        db_execute(conn, "DELETE FROM courses WHERE course_name=?", (name,))
    st.cache_data.clear()

def delete_record(rid):
    with get_db() as conn:
        db_execute(conn, "DELETE FROM training_records WHERE record_id=?", (rid,))
    st.cache_data.clear()

# ── Export helpers ───────────────────────────────────────────

def to_csv(df):
    return df.to_csv(index=False).encode("utf-8")

def to_excel_bytes(emp, crs, rec):
    buf = BytesIO()
    with pd.ExcelWriter(buf, engine="openpyxl") as w:
        emp.to_excel(w, sheet_name="Employees", index=False)
        crs.to_excel(w, sheet_name="Courses", index=False)
        rec.to_excel(w, sheet_name="Training_Records", index=False)
    return buf.getvalue()

# ── UI Helpers ───────────────────────────────────────────────

def gradient_header(title, subtitle=""):
    sub_html = ""
    if subtitle:
        sub_html = f'<p style="color:rgba(255,255,255,0.85);margin:0.5rem 0 0;font-size:1.05rem;font-weight:400;">{subtitle}</p>'
    st.markdown(f"""
    <div style="
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
        padding: 2rem 2.5rem;
        border-radius: 1.25rem;
        margin-bottom: 1.5rem;
        box-shadow: 0 10px 40px rgba(102,126,234,0.25);
    ">
        <h1 style="color:white;margin:0;font-size:1.9rem;font-weight:800;letter-spacing:-0.5px;">{title}</h1>
        {sub_html}
    </div>
    """, unsafe_allow_html=True)

def status_badge(status):
    colors = {"Completed":"#00c853","In Progress":"#ff9100","Not Started":"#78909c","Overdue":"#ff1744"}
    c = colors.get(status, "#78909c")
    return f'<span style="background:{c};color:white;padding:0.25rem 0.75rem;border-radius:1rem;font-size:0.8rem;font-weight:600;">{status}</span>'

def stat_card(label, value, color="#667eea"):
    st.markdown(f"""
    <div style="background:white;border-radius:1rem;padding:1.5rem;text-align:center;
                box-shadow:0 2px 12px rgba(0,0,0,0.06);border-top:4px solid {color};
                transition:transform 0.2s ease;">
        <p style="color:#6b7280;font-size:0.8rem;font-weight:600;text-transform:uppercase;
                  letter-spacing:0.5px;margin:0 0 0.5rem;">{label}</p>
        <p style="color:#1a1a2e;font-size:2.2rem;font-weight:800;margin:0;line-height:1;">{value}</p>
    </div>
    """, unsafe_allow_html=True)

def pct_card(label, value, pct, color="#667eea"):
    st.markdown(f"""
    <div style="background:white;border-radius:1rem;padding:1.5rem;text-align:center;
                box-shadow:0 2px 12px rgba(0,0,0,0.06);border-top:4px solid {color};
                transition:transform 0.2s ease;">
        <p style="color:#6b7280;font-size:0.8rem;font-weight:600;text-transform:uppercase;
                  letter-spacing:0.5px;margin:0 0 0.5rem;">{label}</p>
        <p style="color:#1a1a2e;font-size:2.2rem;font-weight:800;margin:0;line-height:1;">{value}</p>
        <p style="color:{color};font-size:0.95rem;font-weight:700;margin:0.4rem 0 0;">{pct}</p>
    </div>
    """, unsafe_allow_html=True)


# ═══════════════════════════════════════════════════════════════
# APP START
# ═══════════════════════════════════════════════════════════════

st.set_page_config(page_title="Training Tracker", page_icon=":mortar_board:", layout="wide")
st.markdown(THEME_CSS, unsafe_allow_html=True)
require_access()
init_database()

employees = get_employees()
courses = get_courses()
records = get_records()

# ── Sidebar ───────────────────────────────────────────────────

st.sidebar.markdown("""
<div style="text-align:center;padding:1rem 0 0.5rem;">
    <div style="font-size:2.5rem;">&#127891;</div>
    <h2 style="margin:0.25rem 0 0;font-size:1.3rem;">Training Tracker</h2>
    <p style="margin:0;font-size:0.75rem;opacity:0.6;">Multi-User Edition</p>
</div>
""", unsafe_allow_html=True)

page = st.sidebar.radio("Navigate", [
    "Dashboard",
    "Add Training Record",
    "Manage Employees",
    "Manage Courses",
    "Browse Data",
    "Export",
], label_visibility="collapsed")

st.sidebar.markdown("---")
db_label = "PostgreSQL" if not DB_IS_SQLITE else "SQLite"
st.sidebar.caption(
    f"**Database:** {db_label} (multi-user)\n\n"
    f"**Employees:** {len(employees)} | **Courses:** {len(courses)} | **Records:** {len(records)}\n\n"
    f"_Data auto-refreshes every 5 seconds_"
)

# ═══════════════════════════════════════════════════════════════
# DASHBOARD
# ═══════════════════════════════════════════════════════════════
if page == "Dashboard":
    gradient_header("Training Dashboard", "Real-time overview across all departments and employees")

    total = len(records)
    completed = int((records["Status"]=="Completed").sum())
    in_prog = int((records["Status"]=="In Progress").sum())
    overdue = int((records["Status"]=="Overdue").sum())
    not_started = int((records["Status"]=="Not Started").sum())
    comp_rate = round(completed/total*100,1) if total else 0

    c1,c2,c3,c4,c5 = st.columns(5)
    with c1: stat_card("Total Records", total, "#667eea")
    with c2: pct_card("Completed", completed, f"{comp_rate}%", "#00c853")
    with c3: stat_card("In Progress", in_prog, "#ff9100")
    with c4: stat_card("Overdue", overdue, "#ff1744")
    with c5: stat_card("Not Started", not_started, "#78909c")

    st.markdown("<br>", unsafe_allow_html=True)

    # ── Charts Row 1 ─────────────────────────────────────────
    cl, cr = st.columns(2)
    with cl:
        st.markdown("#### Completion Rate")
        sc = records["Status"].value_counts().reset_index()
        sc.columns = ["Status","Count"]
        fig = px.pie(sc, names="Status", values="Count", hole=0.55, color="Status",
                     color_discrete_map=STATUS_COLORS)
        fig.update_traces(textinfo="percent+label", textfont_size=13,
                          marker=dict(line=dict(color="white", width=2)),
                          pull=[0.02]*len(sc))
        fig.update_layout(margin=dict(t=10,b=10,l=10,r=10),
                          legend=dict(orientation="h",y=-0.1,font=dict(size=12)),
                          height=380, paper_bgcolor="rgba(0,0,0,0)", plot_bgcolor="rgba(0,0,0,0)",
                          font=dict(family="Inter"))
        st.plotly_chart(fig, use_container_width=True)

    with cr:
        st.markdown("#### Status by Department")
        merged = records.merge(employees[["Employee_Name","Department"]], on="Employee_Name", how="left")
        ds = merged.groupby(["Department","Status"]).size().reset_index(name="Count")
        fig2 = px.bar(ds, x="Department", y="Count", color="Status", barmode="stack",
                      color_discrete_map=STATUS_COLORS)
        fig2.update_layout(margin=dict(t=10,b=10),
                           legend=dict(orientation="h",y=-0.2,font=dict(size=12)),
                           height=380, paper_bgcolor="rgba(0,0,0,0)", plot_bgcolor="rgba(0,0,0,0)",
                           xaxis=dict(showgrid=False), yaxis=dict(showgrid=True,gridcolor="#f0f0f0"),
                           font=dict(family="Inter"))
        fig2.update_traces(marker_line_width=0, marker_cornerradius=5)
        st.plotly_chart(fig2, use_container_width=True)

    # ── Charts Row 2 ─────────────────────────────────────────
    cl2, cr2 = st.columns(2)
    with cl2:
        st.markdown("#### Completion Trend")
        cdf = records[records["Status"]=="Completed"].copy()
        if not cdf.empty and "Completion_Date" in cdf.columns:
            cdf = cdf.dropna(subset=["Completion_Date"])
            if not cdf.empty:
                cdf["Month"] = cdf["Completion_Date"].dt.to_period("M").astype(str)
                trend = cdf.groupby("Month").size().reset_index(name="Completions").sort_values("Month")
                fig3 = px.area(trend, x="Month", y="Completions", markers=True,
                               color_discrete_sequence=["#667eea"])
                fig3.update_traces(line=dict(width=3), marker=dict(size=8),
                                   fillcolor="rgba(102,126,234,0.15)")
                fig3.update_layout(margin=dict(t=10,b=10), height=350,
                                   paper_bgcolor="rgba(0,0,0,0)", plot_bgcolor="rgba(0,0,0,0)",
                                   xaxis=dict(showgrid=False), yaxis=dict(showgrid=True,gridcolor="#f0f0f0"),
                                   font=dict(family="Inter"))
                st.plotly_chart(fig3, use_container_width=True)
            else: st.info("No completion dates recorded yet.")
        else: st.info("No completed records available.")

    with cr2:
        st.markdown("#### Records per Course")
        cc = records["Course_Name"].value_counts().reset_index()
        cc.columns = ["Course_Name","Count"]
        fig4 = px.bar(cc, y="Course_Name", x="Count", orientation="h",
                      color="Count", color_continuous_scale=["#c3cfe2","#667eea","#764ba2"])
        fig4.update_layout(margin=dict(t=10,b=10,l=10), yaxis=dict(autorange="reversed"),
                           height=350, showlegend=False, coloraxis_showscale=False,
                           paper_bgcolor="rgba(0,0,0,0)", plot_bgcolor="rgba(0,0,0,0)",
                           xaxis=dict(showgrid=True,gridcolor="#f0f0f0"), yaxis_showgrid=False,
                           font=dict(family="Inter"))
        fig4.update_traces(marker_cornerradius=5, marker_line_width=0)
        st.plotly_chart(fig4, use_container_width=True)

    # ── Overdue Table ─────────────────────────────────────────
    st.markdown("---")
    odf = records[records["Status"]=="Overdue"]
    if odf.empty:
        st.markdown("""
        <div style="background:linear-gradient(135deg,#e8f5e9,#c8e6c9);padding:1.5rem 2rem;
                    border-radius:1rem;text-align:center;">
            <p style="font-size:1.2rem;font-weight:600;color:#2e7d32;margin:0;">
            &#9989; No Overdue Training Records &mdash; Great job, team!</p>
        </div>
        """, unsafe_allow_html=True)
    else:
        st.markdown("#### &#9888;&#65039; Overdue Training Records")
        od = odf.merge(employees[["Employee_Name","Department"]], on="Employee_Name", how="left")
        cols = [c for c in ["Record_ID","Employee_Name","Department","Course_Name","Assigned_Date"] if c in od.columns]
        st.dataframe(od[cols], use_container_width=True, hide_index=True)

# ═══════════════════════════════════════════════════════════════
# ADD TRAINING RECORD
# ═══════════════════════════════════════════════════════════════
elif page == "Add Training Record":
    gradient_header("Add Training Record", "Assign a course to an employee and track completion")

    if employees.empty:
        st.warning("No employees found. Please add employees first via **Manage Employees**.")
    elif courses.empty:
        st.warning("No courses found. Please add courses first via **Manage Courses**.")
    else:
        with st.form("add_record", clear_on_submit=True):
            c1, c2 = st.columns(2)
            with c1:
                emp = st.selectbox("Employee Name", sorted(employees["Employee_Name"].unique()))
                status = st.selectbox("Status", STATUS_OPTIONS)
            with c2:
                course = st.selectbox("Course Name", sorted(courses["Course_Name"].unique()))
                comp_date = st.date_input("Completion Date", value=date.today())
            assigned = st.date_input("Assigned Date", value=date.today())
            submitted = st.form_submit_button("Submit Record", use_container_width=True)

        if submitted:
            try:
                add_record(emp, course, status,
                           assigned.strftime("%Y-%m-%d"),
                           comp_date.strftime("%Y-%m-%d"))
                st.success(f"**Saved:** {emp} assigned to _{course}_ ({status})")
                st.balloons()
            except Exception as e:
                st.error(f"Error: {e}")

# ═══════════════════════════════════════════════════════════════
# MANAGE EMPLOYEES
# ═══════════════════════════════════════════════════════════════
elif page == "Manage Employees":
    gradient_header("Manage Employees", "Add new team members or update existing records")

    tab_add, tab_view = st.tabs(["Add New Employee", "Current Employees"])

    with tab_add:
        with st.form("add_emp", clear_on_submit=True):
            c1, c2 = st.columns(2)
            with c1:
                emp_name = st.text_input("Full Name", placeholder="e.g. Jane Smith")
                department = st.selectbox("Department", DEPARTMENTS)
            with c2:
                hire_date = st.date_input("Hire Date", value=date.today())
            add_btn = st.form_submit_button("Add Employee", use_container_width=True)

        if add_btn:
            if not emp_name or not emp_name.strip():
                st.error("Name cannot be empty.")
            elif emp_name.strip() in employees["Employee_Name"].values:
                st.error(f"**{emp_name.strip()}** already exists.")
            else:
                try:
                    add_employee(emp_name, department, hire_date.strftime("%Y-%m-%d"))
                    st.success(f"**Added:** {emp_name.strip()} ({department})")
                    st.balloons()
                except Exception as e:
                    st.error(f"Error: {e}")

    with tab_view:
        search = st.text_input("Search employees", key="emp_search", placeholder="Type a name or department...")
        display = employees.copy()
        if search:
            display = display[display.apply(lambda r: r.astype(str).str.contains(search, case=False).any(), axis=1)]

        st.markdown(f"**Showing {len(display)} of {len(employees)} employees**")
        st.dataframe(display, use_container_width=True, hide_index=True)

        if not employees.empty:
            st.markdown("---")
            st.markdown("#### Remove Employee")
            st.caption("Existing training records for this employee will be kept for historical purposes.")
            rc1, rc2 = st.columns([3,1])
            with rc1:
                del_emp = st.selectbox("Select employee", sorted(employees["Employee_Name"].unique()), key="del_emp")
            with rc2:
                st.markdown("<br>", unsafe_allow_html=True)
                if st.button("Remove", type="primary", use_container_width=True):
                    delete_employee(del_emp)
                    st.success(f"Removed: {del_emp}")
                    st.rerun()

# ═══════════════════════════════════════════════════════════════
# MANAGE COURSES
# ═══════════════════════════════════════════════════════════════
elif page == "Manage Courses":
    gradient_header("Manage Courses", "Add new training courses or remove existing ones")

    tab_add, tab_view = st.tabs(["Add New Course", "Current Courses"])

    with tab_add:
        with st.form("add_crs", clear_on_submit=True):
            c1, c2 = st.columns(2)
            with c1:
                crs_name = st.text_input("Course Name", placeholder="e.g. Advanced Excel")
                category = st.selectbox("Category", CATEGORIES)
            with c2:
                duration = st.number_input("Duration (hours)", min_value=0.5, max_value=200.0, value=2.0, step=0.5)
                due_days = st.number_input("Due Within (days)", min_value=1, max_value=365, value=30, step=1)
            add_btn = st.form_submit_button("Add Course", use_container_width=True)

        if add_btn:
            if not crs_name or not crs_name.strip():
                st.error("Course name cannot be empty.")
            elif crs_name.strip() in courses["Course_Name"].values:
                st.error(f"**{crs_name.strip()}** already exists.")
            else:
                try:
                    add_course(crs_name, category, duration, due_days)
                    st.success(f"**Added:** {crs_name.strip()} ({category}, {duration}h)")
                    st.balloons()
                except Exception as e:
                    st.error(f"Error: {e}")

    with tab_view:
        search = st.text_input("Search courses", key="crs_search", placeholder="Type a course name or category...")
        display = courses.copy()
        if search:
            display = display[display.apply(lambda r: r.astype(str).str.contains(search, case=False).any(), axis=1)]

        st.markdown(f"**Showing {len(display)} of {len(courses)} courses**")
        st.dataframe(display, use_container_width=True, hide_index=True)

        if not courses.empty:
            st.markdown("---")
            st.markdown("#### Remove Course")
            st.caption("Existing training records for this course will be kept for historical purposes.")
            rc1, rc2 = st.columns([3,1])
            with rc1:
                del_crs = st.selectbox("Select course", sorted(courses["Course_Name"].unique()), key="del_crs")
            with rc2:
                st.markdown("<br>", unsafe_allow_html=True)
                if st.button("Remove", type="primary", use_container_width=True):
                    delete_course(del_crs)
                    st.success(f"Removed: {del_crs}")
                    st.rerun()

# ═══════════════════════════════════════════════════════════════
# BROWSE DATA
# ═══════════════════════════════════════════════════════════════
elif page == "Browse Data":
    gradient_header("Browse Database", "Filter, search and explore all training data")

    t1, t2, t3 = st.tabs(["Training Records", "Employees", "Courses"])

    with t1:
        fc1, fc2, fc3 = st.columns(3)
        with fc1: fs = st.multiselect("Status", STATUS_OPTIONS, default=STATUS_OPTIONS)
        with fc2: fe = st.multiselect("Employee", sorted(records["Employee_Name"].dropna().unique()))
        with fc3: fcc = st.multiselect("Course", sorted(records["Course_Name"].dropna().unique()))
        filt = records[records["Status"].isin(fs)]
        if fe: filt = filt[filt["Employee_Name"].isin(fe)]
        if fcc: filt = filt[filt["Course_Name"].isin(fcc)]
        display_cols = [c for c in ["Record_ID","Employee_Name","Course_Name","Status","Assigned_Date","Completion_Date"] if c in filt.columns]
        st.dataframe(filt[display_cols], use_container_width=True, hide_index=True)
        st.caption(f"Showing **{len(filt)}** of **{len(records)}** records")

    with t2:
        se = st.text_input("Search employees", key="browse_emp")
        ed = employees if not se else employees[employees.apply(lambda r: r.astype(str).str.contains(se,case=False).any(), axis=1)]
        st.dataframe(ed, use_container_width=True, hide_index=True)

    with t3:
        sc = st.text_input("Search courses", key="browse_crs")
        cd = courses if not sc else courses[courses.apply(lambda r: r.astype(str).str.contains(sc,case=False).any(), axis=1)]
        st.dataframe(cd, use_container_width=True, hide_index=True)

# ═══════════════════════════════════════════════════════════════
# EXPORT
# ═══════════════════════════════════════════════════════════════
elif page == "Export":
    gradient_header("Export Data", "Download your training data as CSV or Excel")

    st.markdown("#### CSV Downloads")
    c1,c2,c3 = st.columns(3)
    with c1:
        st.download_button("Training Records CSV", to_csv(records),
                           "training_records.csv", "text/csv", use_container_width=True)
    with c2:
        st.download_button("Employees CSV", to_csv(employees),
                           "employees.csv", "text/csv", use_container_width=True)
    with c3:
        st.download_button("Courses CSV", to_csv(courses),
                           "courses.csv", "text/csv", use_container_width=True)

    st.markdown("---")
    st.markdown("#### Full Excel Workbook")
    st.download_button("Download Complete .xlsx", to_excel_bytes(employees, courses, records),
                       "training_tracker_export.xlsx",
                       "application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
                       use_container_width=True)

    st.markdown("---")
    st.markdown("#### Data Preview")
    st.dataframe(records.head(20), use_container_width=True, hide_index=True)
