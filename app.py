import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
import os
import smtplib
import ssl
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
from datetime import datetime, date, timedelta
from pathlib import Path
from io import BytesIO
from contextlib import contextmanager
import random
from sqlalchemy import create_engine, text
from sqlalchemy.pool import QueuePool

# ═══════════════════════════════════════════════════════════════
# CONFIGURATION
# ═══════════════════════════════════════════════════════════════

DB_PATH = Path("training_tracker.db")
EXCEL_SOURCE_PATH = Path("training_db.xlsx")
DATABASE_URL = os.getenv("DATABASE_URL", "").strip()
APP_ACCESS_CODE = os.getenv("APP_ACCESS_CODE", "").strip()

# Email config — set these as Streamlit Secrets or environment variables
SMTP_HOST = os.getenv("SMTP_HOST", "smtp.gmail.com")
SMTP_PORT = int(os.getenv("SMTP_PORT", "587"))  # 587 for STARTTLS (Gmail)
SMTP_USER = os.getenv("SMTP_USER", "").strip()       # your Gmail address
SMTP_PASS = os.getenv("SMTP_PASS", "").strip()       # Gmail App Password (16 chars)
NOTIFY_FROM = os.getenv("NOTIFY_FROM", SMTP_USER)   # sender address
OVERDUE_DAYS_THRESHOLD = int(os.getenv("OVERDUE_DAYS_THRESHOLD", "3"))  # warn N days before due
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
@import url('https://fonts.googleapis.com/css2?family=Plus+Jakarta+Sans:wght@400;500;600;700;800&display=swap');

/* ── Global ─────────────────────────────────────────────── */
.stApp {
    font-family: 'Plus Jakarta Sans', sans-serif;
    background: linear-gradient(145deg, #f0f4ff 0%, #faf5ff 50%, #f0fff4 100%) !important;
}
.block-container {
    padding-top: 0.2rem;
    padding-bottom: 2rem;
    max-width: 1240px;
}

/* ── Sidebar ─────────────────────────────────────────────── */
section[data-testid="stSidebar"] {
    background: linear-gradient(160deg, #0d0221 0%, #1a0533 30%, #0d1b4b 70%, #001233 100%) !important;
    border-right: 1px solid rgba(139,92,246,0.2) !important;
}
/* Scope text colour to text nodes only — do NOT use * wildcard (hides SVG icons) */
section[data-testid="stSidebar"] p,
section[data-testid="stSidebar"] span:not([data-testid]),
section[data-testid="stSidebar"] div.stMarkdown,
section[data-testid="stSidebar"] label { color: #c4b5fd !important; }
section[data-testid="stSidebar"] h1,
section[data-testid="stSidebar"] h2,
section[data-testid="stSidebar"] h3 { color: #ffffff !important; font-weight: 800 !important; }
section[data-testid="stSidebar"] .stRadio label {
    color: #ddd6fe !important;
    font-weight: 600 !important;
    font-size: 0.92rem !important;
    padding: 0.35rem 0.6rem !important;
    border-radius: 0.5rem;
    transition: all 0.18s ease;
    display: block;
}
section[data-testid="stSidebar"] .stRadio label:hover {
    color: #ffffff !important;
    background: rgba(139,92,246,0.2) !important;
}
section[data-testid="stSidebar"] hr { border-color: rgba(139,92,246,0.15) !important; }
section[data-testid="stSidebar"] .stCaption {
    background: rgba(139,92,246,0.1) !important;
    border: 1px solid rgba(139,92,246,0.2);
    border-radius: 0.75rem;
    padding: 0.75rem !important;
}

/* ── Page background cards ───────────────────────────────── */
[data-testid="stVerticalBlock"] > div:first-child { }

/* ── Metric Cards ────────────────────────────────────────── */
div[data-testid="stMetric"] {
    background: rgba(255,255,255,0.9) !important;
    border-radius: 1.1rem !important;
    padding: 1.3rem 1.5rem !important;
    box-shadow: 0 4px 24px rgba(99,102,241,0.10), 0 1px 4px rgba(0,0,0,0.04) !important;
    border: 1px solid rgba(99,102,241,0.12) !important;
    backdrop-filter: blur(8px);
    transition: transform 0.2s ease, box-shadow 0.2s ease !important;
}
div[data-testid="stMetric"]:hover {
    transform: translateY(-4px) !important;
    box-shadow: 0 12px 32px rgba(99,102,241,0.18) !important;
}
div[data-testid="stMetric"] label {
    color: #6366f1 !important;
    font-weight: 700 !important;
    font-size: 0.72rem !important;
    text-transform: uppercase;
    letter-spacing: 1px;
}
div[data-testid="stMetric"] [data-testid="stMetricValue"] {
    font-weight: 800 !important;
    font-size: 2.1rem !important;
    color: #1e1b4b !important;
    letter-spacing: -0.5px;
}

/* ── Forms ───────────────────────────────────────────────── */
[data-testid="stForm"] {
    background: rgba(255,255,255,0.95) !important;
    padding: 2rem 2.5rem !important;
    border-radius: 1.4rem !important;
    box-shadow: 0 8px 32px rgba(99,102,241,0.10) !important;
    border: 1px solid rgba(99,102,241,0.10) !important;
    backdrop-filter: blur(12px);
}

/* ── Submit Button ───────────────────────────────────────── */
.stFormSubmitButton > button {
    background: linear-gradient(135deg, #6366f1 0%, #8b5cf6 50%, #a855f7 100%) !important;
    color: white !important;
    border: none !important;
    border-radius: 0.85rem !important;
    padding: 0.75rem 2.5rem !important;
    font-weight: 800 !important;
    font-size: 1rem !important;
    letter-spacing: 0.3px;
    box-shadow: 0 6px 20px rgba(99,102,241,0.40) !important;
    transition: all 0.25s cubic-bezier(0.4,0,0.2,1) !important;
}
.stFormSubmitButton > button:hover {
    transform: translateY(-3px) scale(1.02) !important;
    box-shadow: 0 12px 28px rgba(99,102,241,0.50) !important;
}

/* ── Regular Buttons ─────────────────────────────────────── */
.stButton > button {
    border-radius: 0.85rem !important;
    font-weight: 700 !important;
    padding: 0.55rem 1.5rem !important;
    transition: all 0.22s ease !important;
    border: 2px solid #6366f1 !important;
    color: #6366f1 !important;
    background: rgba(99,102,241,0.05) !important;
}
.stButton > button:hover {
    background: linear-gradient(135deg,#6366f1,#8b5cf6) !important;
    color: white !important;
    border-color: transparent !important;
    transform: translateY(-2px) !important;
    box-shadow: 0 6px 18px rgba(99,102,241,0.35) !important;
}
button[kind="primary"] {
    background: linear-gradient(135deg, #f43f5e 0%, #e11d48 100%) !important;
    color: white !important;
    border: none !important;
    box-shadow: 0 4px 14px rgba(244,63,94,0.35) !important;
}

/* ── Download Buttons ────────────────────────────────────── */
.stDownloadButton > button {
    background: linear-gradient(135deg, #059669 0%, #10b981 50%, #34d399 100%) !important;
    color: white !important;
    border: none !important;
    border-radius: 0.85rem !important;
    font-weight: 700 !important;
    box-shadow: 0 4px 16px rgba(5,150,105,0.32) !important;
    transition: all 0.25s ease !important;
}
.stDownloadButton > button:hover {
    transform: translateY(-2px) !important;
    box-shadow: 0 8px 22px rgba(5,150,105,0.42) !important;
}

/* ── Tabs ────────────────────────────────────────────────── */
.stTabs [data-baseweb="tab-list"] {
    gap: 0.3rem;
    background: rgba(255,255,255,0.85);
    border-radius: 1rem;
    padding: 0.4rem;
    box-shadow: 0 2px 12px rgba(99,102,241,0.08);
    border: 1px solid rgba(99,102,241,0.10);
}
.stTabs [data-baseweb="tab"] {
    border-radius: 0.75rem;
    padding: 0.55rem 1.4rem;
    font-weight: 700;
    font-size: 0.88rem;
    color: #6366f1 !important;
    transition: all 0.2s ease;
}
.stTabs [aria-selected="true"] {
    background: linear-gradient(135deg, #6366f1 0%, #8b5cf6 100%) !important;
    color: white !important;
    box-shadow: 0 4px 14px rgba(99,102,241,0.35);
}

/* ── Alerts ──────────────────────────────────────────────── */
.stSuccess, .stWarning, .stError, .stInfo { border-radius: 0.85rem !important; }

/* ── DataFrames ──────────────────────────────────────────── */
[data-testid="stDataFrame"] {
    border-radius: 1rem;
    overflow: hidden;
    box-shadow: 0 4px 16px rgba(99,102,241,0.08);
    border: 1px solid rgba(99,102,241,0.10) !important;
}

/* ── Inputs ──────────────────────────────────────────────── */
.stSelectbox > div > div,
.stTextInput > div > div > input,
.stNumberInput > div > div > input,
.stDateInput > div > div > input {
    border-radius: 0.7rem !important;
    border: 2px solid #e0e7ff !important;
    background: rgba(255,255,255,0.95) !important;
    transition: border-color 0.2s ease, box-shadow 0.2s ease !important;
    font-family: 'Plus Jakarta Sans', sans-serif !important;
}
.stSelectbox > div > div:focus-within,
.stTextInput > div > div > input:focus,
.stNumberInput > div > div > input:focus,
.stDateInput > div > div > input:focus {
    border-color: #6366f1 !important;
    box-shadow: 0 0 0 3px rgba(99,102,241,0.18) !important;
}

/* ── Tags ────────────────────────────────────────────────── */
span[data-baseweb="tag"] {
    background: linear-gradient(135deg, #6366f1 0%, #8b5cf6 100%) !important;
    border-radius: 0.5rem !important;
    color: white !important;
    font-weight: 600 !important;
}

/* ── Divider ─────────────────────────────────────────────── */
hr {
    border: none;
    height: 1px;
    background: linear-gradient(90deg, transparent 0%, #c7d2fe 50%, transparent 100%);
    margin: 1.5rem 0;
}

/* ── Spinner ─────────────────────────────────────────────── */
.stSpinner > div { border-top-color: #6366f1 !important; }

/* ── Expander ────────────────────────────────────────────── */
.streamlit-expanderHeader {
    font-weight: 700;
    border-radius: 0.75rem;
    background: rgba(99,102,241,0.05) !important;
}

/* ── Scrollbar ───────────────────────────────────────────── */
::-webkit-scrollbar { width: 6px; height: 6px; }
::-webkit-scrollbar-track { background: #f1f5f9; border-radius: 10px; }
::-webkit-scrollbar-thumb { background: linear-gradient(#6366f1,#8b5cf6); border-radius: 10px; }

/* ── Hide Streamlit top chrome (blank header bar) ── */
[data-testid="stHeader"] { display: none !important; }
[data-testid="stDecoration"] { display: none !important; }
[data-testid="stToolbarActions"] { display: none !important; }
[data-testid="stStatusWidget"] { display: none !important; }
#MainMenu { display: none !important; }
footer { display: none !important; }
/* Force sidebar always open - never auto-collapse */
[data-testid="collapsedControl"] { display: none !important; }
section[data-testid="stSidebar"] {
    transform: none !important;
    min-width: 240px !important;
    width: 240px !important;
    display: block !important;
    visibility: visible !important;
    opacity: 1 !important;
}

/* ── Sidebar nav: hide radio dot and tighten spacing ── */
section[data-testid="stSidebar"] .stRadio > div {
    gap: 0 !important;
}
section[data-testid="stSidebar"] .stRadio > div > label {
    display: flex !important;
    align-items: center !important;
    padding: 0.6rem 1rem !important;
    border-radius: 0.65rem !important;
    margin: 1px 0 !important;
    font-size: 0.88rem !important;
    font-weight: 600 !important;
    color: #c4b5fd !important;
    cursor: pointer;
    border: 1px solid transparent !important;
    transition: all 0.18s ease !important;
    width: 100%;
}
section[data-testid="stSidebar"] .stRadio > div > label:hover {
    background: rgba(139,92,246,0.15) !important;
    color: #ffffff !important;
    border-color: rgba(139,92,246,0.3) !important;
    padding-left: 1.3rem !important;
}
section[data-testid="stSidebar"] .stRadio > div > label[data-checked="true"],
section[data-testid="stSidebar"] .stRadio > div > label:has(input:checked) {
    background: linear-gradient(90deg, rgba(201,168,76,0.18) 0%, rgba(201,168,76,0.05) 100%) !important;
    color: #e8c96a !important;
    border-color: rgba(201,168,76,0.4) !important;
    border-left: 3px solid #c9a84c !important;
    font-weight: 700 !important;
}
section[data-testid="stSidebar"] .stRadio > div > label > div:first-child {
    display: none !important;
}
</style>
"""

# ═══════════════════════════════════════════════════════════════
# DATABASE LAYER (PostgreSQL for cloud + SQLite fallback)
# ═══════════════════════════════════════════════════════════════

@st.cache_resource
def _build_engine():
    """Build DB engine ONCE per server process — avoids reconnect on every request."""
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

    return create_engine(
        url,
        poolclass=QueuePool,
        pool_size=5,
        max_overflow=10,
        pool_pre_ping=True,
        pool_recycle=300,
        future=True,
    )


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

    # Centre the login card
    _, col, _ = st.columns([1, 1.4, 1])
    with col:
        st.markdown("""
        <div style="
            background:linear-gradient(135deg,#1a1a2e 0%,#0f3460 100%);
            border-radius:1.2rem;
            padding:2.5rem 2rem;
            border:1px solid rgba(201,168,76,0.25);
            box-shadow:0 12px 40px rgba(0,0,0,0.35);
            text-align:center;
            margin-top:4rem;
        ">
            <div style="font-size:2.8rem;margin-bottom:0.5rem;">&#128218;</div>
            <div style="color:#ffffff;font-size:1.4rem;font-weight:800;margin-bottom:0.25rem;">Employee Training Tracker</div>
            <div style="color:#c9a84c;font-size:0.75rem;font-weight:600;letter-spacing:1.5px;text-transform:uppercase;margin-bottom:1.5rem;">Secure Access</div>
        </div>
        """, unsafe_allow_html=True)

        # Wrap in form so Enter key triggers submission
        with st.form("login_form"):
            code = st.text_input("Access Code", type="password",
                                 placeholder="Enter your access code…",
                                 label_visibility="collapsed")
            submitted = st.form_submit_button("🔓  Unlock", use_container_width=True)

        if submitted:
            if code.strip() == APP_ACCESS_CODE:
                st.session_state["authenticated"] = True
                st.rerun()
            else:
                st.error("Invalid access code. Please try again.")

    st.stop()

# ═══════════════════════════════════════════════════════════════
# AUDIT TRAIL
# ═══════════════════════════════════════════════════════════════

def _ensure_audit_table(conn):
    db_execute(conn, """
        CREATE TABLE IF NOT EXISTS audit_log (
            log_id      TEXT PRIMARY KEY,
            action      TEXT NOT NULL,
            table_name  TEXT NOT NULL,
            record_ref  TEXT,
            detail      TEXT,
            performed_by TEXT DEFAULT 'user',
            performed_at TEXT DEFAULT CURRENT_TIMESTAMP
        )
    """)

def write_audit(action, table_name, record_ref="", detail=""):
    """Write one audit entry. action = ADDED / DELETED / LOGIN."""
    with get_db() as conn:
        _ensure_audit_table(conn)
        from uuid import uuid4
        lid = str(uuid4())[:12]
        performed_by = st.session_state.get("current_user", "user")
        db_execute(conn,
            "INSERT INTO audit_log VALUES (?,?,?,?,?,?,CURRENT_TIMESTAMP)",
            (lid, action, table_name, record_ref, detail, performed_by))

@st.cache_data(ttl=30)
def get_audit_log(limit=200):
    with get_db() as conn:
        _ensure_audit_table(conn)
        rows = db_execute(
            conn,
            "SELECT * FROM audit_log ORDER BY performed_at DESC LIMIT ?",
            (limit,)
        ).mappings().all()
    df = pd.DataFrame(rows)
    if df.empty:
        return pd.DataFrame(columns=["log_id","action","table_name","record_ref","detail","performed_by","performed_at"])
    return df.rename(columns={
        "log_id": "Log_ID", "action": "Action", "table_name": "Table",
        "record_ref": "Record", "detail": "Detail",
        "performed_by": "User", "performed_at": "Timestamp"
    })

# ═══════════════════════════════════════════════════════════════
# EMAIL REMINDERS
# ═══════════════════════════════════════════════════════════════

def _send_email(to_addr, subject, html_body):
    """Send one email via SMTP TLS. Returns (success, error_msg)."""
    if not SMTP_USER or not SMTP_PASS:
        return False, "SMTP_USER or SMTP_PASS not configured."
    
    msg = MIMEMultipart("alternative")
    msg["Subject"] = subject
    msg["From"] = NOTIFY_FROM
    msg["To"] = to_addr
    msg.attach(MIMEText(html_body, "html"))
    
    # Try multiple methods for compatibility with different SMTP servers
    methods = []
    
    if SMTP_PORT == 465:
        methods.append(("SMTP_SSL (port 465)", lambda: _send_via_ssl(msg, to_addr)))
    elif SMTP_PORT == 587:
        methods.append(("STARTTLS (port 587)", lambda: _send_via_starttls(msg, to_addr)))
    else:
        # Try both methods
        methods.append(("SMTP_SSL (port 465)", lambda: _send_via_ssl(msg, to_addr, 465)))
        methods.append(("STARTTLS (port 587)", lambda: _send_via_starttls(msg, to_addr, 587)))
    
    last_error = ""
    for method_name, send_func in methods:
        try:
            send_func()
            return True, ""
        except Exception as e:
            last_error = f"{method_name} failed: {str(e)}"
            continue
    
    return False, last_error

def _send_via_ssl(msg, to_addr, port=None):
    """Send email using SMTP_SSL (implicit SSL on port 465)."""
    port = port or SMTP_PORT
    context = ssl.create_default_context()
    with smtplib.SMTP_SSL(SMTP_HOST, port, context=context, timeout=30) as server:
        server.set_debuglevel(0)
        server.login(SMTP_USER, SMTP_PASS)
        server.sendmail(NOTIFY_FROM, to_addr, msg.as_string())

def _send_via_starttls(msg, to_addr, port=None):
    """Send email using STARTTLS (explicit TLS on port 587)."""
    port = port or SMTP_PORT
    with smtplib.SMTP(SMTP_HOST, port, timeout=30) as server:
        server.set_debuglevel(0)
        server.ehlo()
        server.starttls()
        server.ehlo()
        server.login(SMTP_USER, SMTP_PASS)
        server.sendmail(NOTIFY_FROM, to_addr, msg.as_string())

def send_overdue_reminder(employee_name, course_name, to_email, days_overdue):
    subject = f"[Training Reminder] Overdue: {course_name}"
    html = f"""
    <div style="font-family:Inter,sans-serif;max-width:600px;margin:auto;">
      <div style="background:linear-gradient(135deg,#667eea,#764ba2);padding:24px 32px;border-radius:12px 12px 0 0;">
        <h2 style="color:white;margin:0;">Training Reminder</h2>
      </div>
      <div style="background:#f9f9ff;padding:24px 32px;border-radius:0 0 12px 12px;border:1px solid #e0e0f0;">
        <p>Hi <strong>{employee_name}</strong>,</p>
        <p>This is a reminder that the following training is <span style="color:#ff1744;font-weight:700;">overdue by {days_overdue} day(s)</span>:</p>
        <table style="width:100%;border-collapse:collapse;margin:16px 0;">
          <tr style="background:#667eea;color:white;">
            <th style="padding:10px;text-align:left;">Course</th>
            <th style="padding:10px;text-align:left;">Status</th>
          </tr>
          <tr style="background:white;">
            <td style="padding:10px;border:1px solid #e0e0f0;">{course_name}</td>
            <td style="padding:10px;border:1px solid #e0e0f0;"><span style="color:#ff1744;font-weight:600;">Overdue</span></td>
          </tr>
        </table>
        <p>Please complete this training as soon as possible.</p>
        <p style="color:#6b7280;font-size:0.85rem;">This is an automated reminder from Employee Training Tracker.</p>
      </div>
    </div>
    """
    return _send_email(to_email, subject, html)

def send_upcoming_reminder(employee_name, course_name, to_email, days_left):
    subject = f"[Training Reminder] Due Soon: {course_name}"
    html = f"""
    <div style="font-family:Inter,sans-serif;max-width:600px;margin:auto;">
      <div style="background:linear-gradient(135deg,#11998e,#38ef7d);padding:24px 32px;border-radius:12px 12px 0 0;">
        <h2 style="color:white;margin:0;">Upcoming Training Reminder</h2>
      </div>
      <div style="background:#f9fff9;padding:24px 32px;border-radius:0 0 12px 12px;border:1px solid #c8e6c9;">
        <p>Hi <strong>{employee_name}</strong>,</p>
        <p>Your training <strong>{course_name}</strong> is due in <span style="color:#ff9100;font-weight:700;">{days_left} day(s)</span>.</p>
        <p>Please complete it on time to stay compliant.</p>
        <p style="color:#6b7280;font-size:0.85rem;">This is an automated reminder from Employee Training Tracker.</p>
      </div>
    </div>
    """
    return _send_email(to_email, subject, html)

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

@st.cache_data(ttl=30)
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

@st.cache_data(ttl=30)
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

@st.cache_data(ttl=30)
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

@st.cache_data(ttl=30)
def get_employee_completion_summary():
    """Get completed trainings grouped by employee for the Training Summary page."""
    with get_db() as conn:
        rows = db_execute(
            conn,
            "SELECT employee_name, course_name FROM training_records WHERE status='Completed' ORDER BY employee_name, course_name"
        ).mappings().all()
    
    if not rows:
        return pd.DataFrame(columns=["Employee_Name", "Completed_Count", "Courses"])
    
    # Group by employee
    from collections import defaultdict
    emp_courses = defaultdict(list)
    for row in rows:
        emp_name = row["employee_name"]
        course_name = row["course_name"]
        emp_courses[emp_name].append(course_name)
    
    # Build result dataframe
    data = []
    for emp_name in sorted(emp_courses.keys()):
        courses = emp_courses[emp_name]
        data.append({
            "Employee_Name": emp_name,
            "Completed_Count": len(courses),
            "Courses": ", ".join(courses)
        })
    
    return pd.DataFrame(data)

# ── Write functions ──────────────────────────────────────────

def add_employee(name, department, hire_date):
    with get_db() as conn:
        count = db_execute(conn, "SELECT COUNT(*) FROM employees").fetchone()[0]
        eid = f"EMP{str(count+1).zfill(3)}"
        db_execute(conn, "INSERT INTO employees VALUES (?,?,?,?)",
                   (eid, name.strip(), department, hire_date))
    get_employees.clear()
    write_audit("ADDED", "employees", eid, f"{name.strip()} / {department}")

def add_course(name, category, duration, due_days):
    with get_db() as conn:
        count = db_execute(conn, "SELECT COUNT(*) FROM courses").fetchone()[0]
        cid = f"CRS{str(count+1).zfill(3)}"
        db_execute(conn, "INSERT INTO courses VALUES (?,?,?,?,?)",
                   (cid, name.strip(), category, duration, int(due_days)))
    get_courses.clear()
    write_audit("ADDED", "courses", cid, f"{name.strip()} / {category}")

def add_record(emp, course, status, assigned, completion):
    with get_db() as conn:
        count = db_execute(conn, "SELECT COUNT(*) FROM training_records").fetchone()[0]
        rid = f"REC{str(count+1).zfill(4)}"
        cd = completion if status == "Completed" else ""
        db_execute(conn, "INSERT INTO training_records VALUES (?,?,?,?,?,?,CURRENT_TIMESTAMP)",
                   (rid, emp, course, status, assigned, cd))
    get_records.clear()
    get_employee_completion_summary.clear()
    write_audit("ADDED", "training_records", rid, f"{emp} → {course} ({status})")

def delete_employee(name):
    with get_db() as conn:
        db_execute(conn, "DELETE FROM employees WHERE employee_name=?", (name,))
    get_employees.clear()
    write_audit("DELETED", "employees", name, f"Removed employee: {name}")

def delete_course(name):
    with get_db() as conn:
        db_execute(conn, "DELETE FROM courses WHERE course_name=?", (name,))
    get_courses.clear()
    write_audit("DELETED", "courses", name, f"Removed course: {name}")

def delete_record(rid):
    with get_db() as conn:
        db_execute(conn, "DELETE FROM training_records WHERE record_id=?", (rid,))
    get_records.clear()
    get_employee_completion_summary.clear()
    write_audit("DELETED", "training_records", rid, f"Removed record: {rid}")

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

def gradient_header(title, subtitle="", color_start="#1a1a2e", color_end="#0f3460"):
    sub_html = ""
    if subtitle:
        sub_html = f'<p style="color:rgba(201,168,76,0.9);margin:0.35rem 0 0;font-size:0.93rem;font-weight:500;">{subtitle}</p>'
    st.markdown(f"""
    <div style="
        background: linear-gradient(135deg, #1a1a2e 0%, #0f3460 100%);
        padding: 1.3rem 1.8rem;
        border-radius: 1rem;
        margin-bottom: 1.2rem;
        box-shadow: 0 6px 20px rgba(0,0,0,0.20);
        border-left: 5px solid #c9a84c;
        border-bottom: 1px solid rgba(201,168,76,0.2);
    ">
        <h1 style="color:#ffffff;margin:0;font-size:1.55rem;font-weight:800;letter-spacing:-0.2px;font-family:'Plus Jakarta Sans',sans-serif;">{title}</h1>
        {sub_html}
    </div>
    """, unsafe_allow_html=True)

def status_badge(status):
    colors = {"Completed":"#00c853","In Progress":"#ff9100","Not Started":"#78909c","Overdue":"#ff1744"}
    c = colors.get(status, "#78909c")
    return f'<span style="background:{c};color:white;padding:0.25rem 0.75rem;border-radius:1rem;font-size:0.8rem;font-weight:600;">{status}</span>'

def stat_card(label, value, color="#6366f1"):
    st.markdown(f"""
    <div style="background:white;border-radius:1.1rem;padding:1.4rem 1.2rem;text-align:center;
                box-shadow:0 4px 18px rgba(99,102,241,0.10);border-top:4px solid {color};
                transition:transform 0.2s ease;">
        <p style="color:#7c7c9c;font-size:0.72rem;font-weight:700;text-transform:uppercase;
                  letter-spacing:1px;margin:0 0 0.4rem;">{label}</p>
        <p style="color:#1e1b4b;font-size:2.1rem;font-weight:800;margin:0;line-height:1;">{value}</p>
    </div>
    """, unsafe_allow_html=True)

def pct_card(label, value, pct, color="#6366f1"):
    st.markdown(f"""
    <div style="background:white;border-radius:1.1rem;padding:1.4rem 1.2rem;text-align:center;
                box-shadow:0 4px 18px rgba(99,102,241,0.10);border-top:4px solid {color};
                transition:transform 0.2s ease;">
        <p style="color:#7c7c9c;font-size:0.72rem;font-weight:700;text-transform:uppercase;
                  letter-spacing:1px;margin:0 0 0.4rem;">{label}</p>
        <p style="color:#1e1b4b;font-size:2.1rem;font-weight:800;margin:0;line-height:1;">{value}</p>
        <p style="color:{color};font-size:0.95rem;font-weight:700;margin:0.4rem 0 0;">{pct}</p>
    </div>
    """, unsafe_allow_html=True)


# ═══════════════════════════════════════════════════════════════
# APP START
# ═══════════════════════════════════════════════════════════════

st.set_page_config(page_title="Employee Training Tracker | Gainwell Technologies", page_icon="\U0001f4d8", layout="wide", initial_sidebar_state="expanded")
st.markdown(THEME_CSS, unsafe_allow_html=True)

# ── Top Branding Bar ──────────────────────────────────────────
st.markdown("""
<div style="
    background: linear-gradient(135deg, #1a1a2e 0%, #16213e 40%, #0f3460 100%);
    padding: 0.85rem 2.2rem;
    display: flex;
    align-items: center;
    justify-content: space-between;
    border-radius: 0 0 1.1rem 1.1rem;
    margin-bottom: 1.2rem;
    box-shadow: 0 6px 24px rgba(0,0,0,0.35);
    border-bottom: 3px solid #c9a84c;
">
    <div style="display:flex;align-items:center;gap:1rem;">
        <div style="font-size:2.2rem;">&#128218;</div>
        <div>
            <div style="color:#ffffff;font-size:1.35rem;font-weight:800;letter-spacing:-0.2px;font-family:'Plus Jakarta Sans',sans-serif;">Employee Training Tracker</div>
            <div style="color:#c9a84c;font-size:0.68rem;font-weight:700;letter-spacing:1.5px;text-transform:uppercase;margin-top:2px;">Gainwell Technologies • Tennessee</div>
        </div>
    </div>
    <div style="
        background:linear-gradient(135deg,#c9a84c,#e8c96a);
        color:#1a1a2e;
        font-size:0.7rem;
        font-weight:800;
        padding:0.3rem 0.9rem;
        border-radius:999px;
        letter-spacing:0.5px;
        text-transform:uppercase;
    ">&#9679; Live &amp; Secure</div>
</div>
""", unsafe_allow_html=True)
require_access()
init_database()

# ── Sidebar ───────────────────────────────────────────────────

st.sidebar.markdown("""
<div style="text-align:center;padding:0.75rem 0.5rem 0.5rem;">
    <div style="
        background:linear-gradient(135deg,#1a1a2e,#0f3460);
        border-radius:1rem;
        padding:1rem 0.5rem;
        border:1px solid rgba(201,168,76,0.25);
    ">
        <div style="font-size:1.8rem;">&#128218;</div>
        <div style="color:#ffffff;font-size:1rem;font-weight:800;margin:0.3rem 0 0;letter-spacing:-0.2px;">Training Tracker</div>
        <div style="color:#c9a84c;font-size:0.65rem;font-weight:700;letter-spacing:1.5px;text-transform:uppercase;margin-top:3px;">Management Platform</div>
    </div>
</div>
""", unsafe_allow_html=True)

st.sidebar.markdown("<div style='padding:0.3rem 0.5rem 0.1rem;color:#94a3b8;font-size:0.65rem;font-weight:700;letter-spacing:1.5px;text-transform:uppercase;'>Navigation</div>", unsafe_allow_html=True)

NAV_ITEMS = [
    ("🏠", "Dashboard"),
    ("➕", "Add Training Record"),
    ("👥", "Manage Employees"),
    ("📚", "Manage Courses"),
    ("🔍", "Browse Data"),
    ("📤", "Export"),
    ("📋", "Audit Log"),
    ("📧", "Email Reminders"),
    ("�", "Training Summary"),
    ("�📥", "Import from Excel"),
]
NAV_LABELS = [f"{icon}  {label}" for icon, label in NAV_ITEMS]

selected_label = st.sidebar.radio("Navigate", NAV_LABELS, label_visibility="collapsed")
page = selected_label.split("  ", 1)[-1]

st.sidebar.markdown("---")
db_label = "PostgreSQL" if not DB_IS_SQLITE else "SQLite"
# Lightweight status - no heavy queries here
st.sidebar.caption(
    f"**Database:** {db_label} (multi-user)\n\n"
    f"_Data loads on-demand per page_"
)

# ═══════════════════════════════════════════════════════════════
# DASHBOARD
# ═══════════════════════════════════════════════════════════════
if page == "Dashboard":
    gradient_header("Training Dashboard", "Real-time overview across all departments and employees")

    # Load data only for this page
    employees = get_employees()
    records = get_records()

    total = len(records)
    completed = int((records["Status"]=="Completed").sum())
    in_prog = int((records["Status"]=="In Progress").sum())
    overdue = int((records["Status"]=="Overdue").sum())
    not_started = int((records["Status"]=="Not Started").sum())
    comp_rate = round(completed/total*100,1) if total else 0

    c1,c2,c3,c4,c5 = st.columns(5)
    with c1: stat_card("Total Records", total, "#6366f1")
    with c2: pct_card("Completed", completed, f"{comp_rate}%", "#059669")
    with c3: stat_card("In Progress", in_prog, "#f59e0b")
    with c4: stat_card("Overdue", overdue, "#f43f5e")
    with c5: stat_card("Not Started", not_started, "#94a3b8")

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

    # Load data only for this page
    employees = get_employees()
    courses = get_courses()

    if employees.empty:
        st.warning("No employees found. Please add employees first via **Manage Employees**.")
    elif courses.empty:
        st.warning("No courses found. Please add courses first via **Manage Courses**.")
    else:
        emp_list    = sorted(employees["Employee_Name"].unique().tolist())
        course_list = sorted(courses["Course_Name"].unique().tolist())

        # Restore last selections so they persist after save
        last_emp    = st.session_state.get("last_emp", emp_list[0])
        last_course = st.session_state.get("last_course", course_list[0])
        last_status = st.session_state.get("last_status", STATUS_OPTIONS[0])

        emp_idx    = emp_list.index(last_emp)    if last_emp    in emp_list    else 0
        course_idx = course_list.index(last_course) if last_course in course_list else 0
        status_idx = STATUS_OPTIONS.index(last_status) if last_status in STATUS_OPTIONS else 0

        with st.form("add_record", clear_on_submit=False):
            c1, c2 = st.columns(2)
            with c1:
                emp    = st.selectbox("Employee Name", emp_list, index=emp_idx)
                status = st.selectbox("Status", STATUS_OPTIONS, index=status_idx)
            with c2:
                course    = st.selectbox("Course Name", course_list, index=course_idx)
                comp_date = st.date_input("Completion Date", value=date.today())
            assigned  = st.date_input("Assigned Date", value=date.today())
            submitted = st.form_submit_button("Submit Record", use_container_width=True)

        if submitted:
            try:
                add_record(emp, course, status,
                           assigned.strftime("%Y-%m-%d"),
                           comp_date.strftime("%Y-%m-%d"))
                # Persist selections so they remain after save
                st.session_state["last_emp"]    = emp
                st.session_state["last_course"] = course
                st.session_state["last_status"] = status
                st.success(f"**Saved:** {emp} assigned to _{course}_ ({status})")
                st.balloons()
            except Exception as e:
                st.error(f"Error: {e}")

# ═══════════════════════════════════════════════════════════════
# MANAGE EMPLOYEES
# ═══════════════════════════════════════════════════════════════
elif page == "Manage Employees":
    gradient_header("Manage Employees", "Add new team members or update existing records")

    # Load data only for this page
    employees = get_employees()

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
                    st.rerun()
                except Exception as e:
                    st.error(f"Error: {e}")

    with tab_view:
        search = st.text_input("Search employees", key="emp_search", placeholder="Type a name or department...")
        # Use fresh DB fetch so newly added employees always appear immediately
        fresh_employees = get_employees()
        display = fresh_employees.copy()
        if search:
            mask = display.apply(lambda r: r.astype(str).str.contains(search.strip(), case=False, regex=False).any(), axis=1)
            display = display[mask]

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

    # Load data only for this page
    courses = get_courses()

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
                    st.rerun()
                except Exception as e:
                    st.error(f"Error: {e}")

    with tab_view:
        search = st.text_input("Search courses", key="crs_search", placeholder="Type a course name or category...")
        fresh_courses = get_courses()
        display = fresh_courses.copy()
        if search:
            display = display[display.apply(lambda r: r.astype(str).str.contains(search.strip(), case=False, regex=False).any(), axis=1)]

        st.markdown(f"**Showing {len(display)} of {len(fresh_courses)} courses**")
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

    # Load data only for this page
    employees = get_employees()
    courses = get_courses()
    records = get_records()

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

    # Load data only for this page
    employees = get_employees()
    courses = get_courses()
    records = get_records()

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

# ═══════════════════════════════════════════════════════════════
# IMPORT FROM EXCEL
# ═══════════════════════════════════════════════════════════════
elif page == "Import from Excel":
    gradient_header("Import from Excel", "Upload a workbook to bulk-import Employees, Courses or Training Records")

    def _pick(df, candidates):
        lmap = {str(c).strip().lower(): c for c in df.columns}
        for cand in candidates:
            if cand.lower() in lmap:
                return lmap[cand.lower()]
        return None

    uploaded = st.file_uploader(
        "Choose an Excel file (.xlsx)",
        type=["xlsx"],
        help="File must contain at least one of: Employees, Courses, Training_Records sheets"
    )

    if uploaded:
        try:
            xls = pd.ExcelFile(uploaded)
        except Exception as e:
            st.error(f"Cannot read file: {e}")
            st.stop()

        available = {s.lower(): s for s in xls.sheet_names}
        st.success(f"Loaded **{uploaded.name}** — sheets found: {', '.join(xls.sheet_names)}")

        ix1, ix2 = st.columns(2)
        with ix1:
            import_mode = st.radio("Import Mode",
                ["Append (keep existing rows)", "Replace (clear table first)"],
                help="Append adds new rows. Replace deletes existing data first."
            )
        with ix2:
            sheets_to_import = st.multiselect(
                "Sheets to import",
                [s for s in ["Employees", "Courses", "Training_Records"]
                 if s.lower() in available or s.lower().replace("_"," ") in available],
                default=[s for s in ["Employees", "Courses", "Training_Records"]
                         if s.lower() in available or s.lower().replace("_"," ") in available]
            )

        mode = "replace" if "Replace" in import_mode else "append"

        # Preview tabs
        if sheets_to_import:
            st.markdown("#### Preview (first 10 rows)")
            preview_tabs = st.tabs(sheets_to_import)
            for tab, sname in zip(preview_tabs, sheets_to_import):
                real = available.get(sname.lower()) or available.get(sname.lower().replace("_"," "))
                if real:
                    with tab:
                        st.dataframe(pd.read_excel(uploaded, sheet_name=real).head(10),
                                     use_container_width=True, hide_index=True)

        st.markdown("---")
        if st.button("Import Now", type="primary", use_container_width=True):
            results = []
            with get_db() as conn:
                for sname in sheets_to_import:
                    real = available.get(sname.lower()) or available.get(sname.lower().replace("_"," "))
                    if not real:
                        results.append((sname, 0, 0, "sheet not found"))
                        continue
                    df = pd.read_excel(uploaded, sheet_name=real)

                    if sname == "Employees":
                        n_col = _pick(df, ["Employee Name","Employee_Name","Name","Employee"])
                        d_col = _pick(df, ["Department","Dept"])
                        h_col = _pick(df, ["Hire Date","Hire_Date","Start Date"])
                        if not n_col:
                            results.append((sname, 0, 0, "Name column not found")); continue
                        if mode == "replace":
                            db_execute(conn, "DELETE FROM training_records")
                            db_execute(conn, "DELETE FROM employees")
                        cnt = db_execute(conn, "SELECT COUNT(*) FROM employees").fetchone()[0]
                        ins = skip = 0
                        for i, row in enumerate(df.dropna(subset=[n_col]).itertuples(index=False), 1):
                            rm = dict(zip(df.columns, row))
                            nm = str(rm[n_col]).strip()
                            dp = str(rm.get(d_col,"Other") or "Other").strip() if d_col else "Other"
                            hd = pd.to_datetime(rm.get(h_col), errors="coerce") if h_col else pd.NaT
                            ht = hd.strftime("%Y-%m-%d") if pd.notna(hd) else date.today().strftime("%Y-%m-%d")
                            try:
                                db_execute(conn, "INSERT INTO employees VALUES (?,?,?,?)",
                                           (f"EMP{str(cnt+i).zfill(3)}", nm, dp or "Other", ht))
                                ins += 1
                            except Exception: skip += 1
                        results.append((sname, ins, skip, ""))

                    elif sname == "Courses":
                        n_col = _pick(df, ["Course Name","Course_Name","Course","Training"])
                        if not n_col:
                            results.append((sname, 0, 0, "Name column not found")); continue
                        if mode == "replace":
                            db_execute(conn, "DELETE FROM training_records")
                            db_execute(conn, "DELETE FROM courses")
                        cnt  = db_execute(conn, "SELECT COUNT(*) FROM courses").fetchone()[0]
                        c_col = _pick(df, ["Category","Type"])
                        d_col = _pick(df, ["Duration Hours","Duration_Hours","Duration"])
                        dd_col = _pick(df, ["Due Within Days","Due_Within_Days","Due Days"])
                        ins = skip = 0
                        for i, row in enumerate(df.dropna(subset=[n_col]).itertuples(index=False), 1):
                            rm  = dict(zip(df.columns, row))
                            nm  = str(rm[n_col]).strip()
                            cat = str(rm.get(c_col,"Other") or "Other").strip() if c_col else "Other"
                            try: dur = float(rm.get(d_col,1) or 1) if d_col else 1.0
                            except: dur = 1.0
                            try: dud = int(rm.get(dd_col,30) or 30) if dd_col else 30
                            except: dud = 30
                            try:
                                db_execute(conn, "INSERT INTO courses VALUES (?,?,?,?,?)",
                                           (f"CRS{str(cnt+i).zfill(3)}", nm, cat or "Other", dur, dud))
                                ins += 1
                            except Exception: skip += 1
                        results.append((sname, ins, skip, ""))

                    elif sname == "Training_Records":
                        e_col = _pick(df, ["Employee Name","Employee_Name","Employee"])
                        c_col = _pick(df, ["Course Name","Course_Name","Course"])
                        if not e_col or not c_col:
                            results.append((sname, 0, 0, "Employee or Course column not found")); continue
                        if mode == "replace":
                            db_execute(conn, "DELETE FROM training_records")
                        cnt   = db_execute(conn, "SELECT COUNT(*) FROM training_records").fetchone()[0]
                        s_col = _pick(df, ["Status","Training Status"])
                        comp_c = _pick(df, ["Completion Date","Completion_Date","Date"])
                        asgn_c = _pick(df, ["Assigned Date","Assigned_Date","Enrollment Date"])
                        ins = skip = 0
                        for i, row in enumerate(df.dropna(subset=[e_col,c_col]).itertuples(index=False), 1):
                            rm  = dict(zip(df.columns, row))
                            en  = str(rm[e_col]).strip()
                            cn  = str(rm[c_col]).strip()
                            st_ = str(rm.get(s_col,"Not Started") or "Not Started").strip() if s_col else "Not Started"
                            cdt = pd.to_datetime(rm.get(comp_c), errors="coerce") if comp_c else pd.NaT
                            adt = pd.to_datetime(rm.get(asgn_c), errors="coerce") if asgn_c else pd.NaT
                            ct  = cdt.strftime("%Y-%m-%d") if pd.notna(cdt) else ""
                            at  = adt.strftime("%Y-%m-%d") if pd.notna(adt) else date.today().strftime("%Y-%m-%d")
                            try:
                                db_execute(conn, "INSERT INTO training_records VALUES (?,?,?,?,?,?,CURRENT_TIMESTAMP)",
                                           (f"REC{str(cnt+i).zfill(4)}", en, cn, st_, at, ct))
                                ins += 1
                            except Exception: skip += 1
                        results.append((sname, ins, skip, ""))

            get_employees.clear()
            get_courses.clear()
            get_records.clear()
            get_employee_completion_summary.clear()

            st.markdown("#### Import Results")
            for sname, ins, skip, err in results:
                if err:
                    st.error(f"**{sname}**: {err}")
                else:
                    st.success(f"**{sname}**: {ins} rows imported, {skip} skipped (duplicates)")
            write_audit("IMPORT", "excel", uploaded.name, f"Mode={mode}, sheets={sheets_to_import}")
    else:
        st.info("Upload an Excel file above to get started. The file should have sheets named **Employees**, **Courses**, and/or **Training_Records**.")
        st.markdown("""**Required column names per sheet:**
| Sheet | Required columns |
|---|---|
| Employees | Employee Name, Department, Hire Date |
| Courses | Course Name, Category, Duration Hours, Due Within Days |
| Training_Records | Employee Name, Course Name, Status, Completion Date, Assigned Date |""")

# ═══════════════════════════════════════════════════════════════
# AUDIT LOG
# ═══════════════════════════════════════════════════════════════
elif page == "Audit Log":
    gradient_header("Audit Log", "Full history of every add, delete, and login action")

    audit_df = get_audit_log(500)

    if audit_df.empty:
        st.info("No audit entries yet. Actions will appear here automatically.")
    else:
        fa1, fa2 = st.columns(2)
        with fa1:
            action_filter = st.multiselect("Filter by Action",
                audit_df["Action"].unique().tolist(),
                default=audit_df["Action"].unique().tolist())
        with fa2:
            table_filter = st.multiselect("Filter by Table",
                audit_df["Table"].unique().tolist(),
                default=audit_df["Table"].unique().tolist())

        filtered_audit = audit_df[
            audit_df["Action"].isin(action_filter) &
            audit_df["Table"].isin(table_filter)
        ]

        action_colors = {"ADDED": "#00c853", "DELETED": "#ff1744", "LOGIN": "#0ea5e9"}

        st.markdown(f"**{len(filtered_audit)} entries**")
        st.dataframe(filtered_audit, use_container_width=True, hide_index=True, height=420)

        st.markdown("---")
        al1, al2 = st.columns(2)
        with al1:
            ac = filtered_audit["Action"].value_counts().reset_index()
            ac.columns = ["Action", "Count"]
            fig_a = px.bar(ac, x="Action", y="Count", color="Action",
                           color_discrete_map=action_colors,
                           title="Actions Breakdown")
            fig_a.update_layout(paper_bgcolor="rgba(0,0,0,0)", plot_bgcolor="rgba(0,0,0,0)",
                                margin=dict(t=40,b=10), showlegend=False,
                                font=dict(family="Inter"))
            st.plotly_chart(fig_a, use_container_width=True)
        with al2:
            tb = filtered_audit["Table"].value_counts().reset_index()
            tb.columns = ["Table", "Count"]
            fig_t = px.pie(tb, names="Table", values="Count", hole=0.5,
                           title="Activity by Table",
                           color_discrete_sequence=px.colors.sequential.Purpor)
            fig_t.update_layout(paper_bgcolor="rgba(0,0,0,0)",
                                margin=dict(t=40,b=10), font=dict(family="Inter"))
            st.plotly_chart(fig_t, use_container_width=True)

        st.download_button(
            "Download Audit Log CSV",
            filtered_audit.to_csv(index=False).encode("utf-8"),
            "audit_log.csv", "text/csv", use_container_width=True
        )

# ═══════════════════════════════════════════════════════════════
# EMAIL REMINDERS
# ═══════════════════════════════════════════════════════════════
elif page == "Email Reminders":
    gradient_header("Email Reminders", "Send overdue and upcoming training reminders to employees")

    # Load data only for this page
    employees = get_employees()
    courses = get_courses()
    records = get_records()

    smtp_ready = bool(SMTP_USER and SMTP_PASS)
    if not smtp_ready:
        st.warning(
            "Email not configured. Add these to Streamlit Secrets:\n\n"
            "```\nSMTP_USER = \"your_email@gmail.com\"\n"
            "SMTP_PASS = \"your_16_char_app_password\"\n```\n\n"
            "Generate Gmail App Password at: https://myaccount.google.com/apppasswords\n\n"
            "Note: You must enable 2-Factor Authentication on your Gmail account first."
        )

    st.markdown("#### Send Manual Reminder")
    with st.form("manual_reminder", clear_on_submit=True):
        mr1, mr2 = st.columns(2)
        with mr1:
            rem_emp = st.selectbox("Employee", sorted(employees["Employee_Name"].unique()) if not employees.empty else ["No employees"])
            rem_email = st.text_input("Recipient Email", placeholder="employee@company.com")
        with mr2:
            rem_course = st.selectbox("Course", sorted(courses["Course_Name"].unique()) if not courses.empty else ["No courses"])
            rem_type = st.selectbox("Reminder Type", ["Overdue", "Upcoming"])
        rem_days = st.number_input("Days overdue / days left", min_value=1, max_value=365, value=3)
        rem_btn = st.form_submit_button("Send Reminder", use_container_width=True, disabled=not smtp_ready)

    if rem_btn:
        if not rem_email or "@" not in rem_email:
            st.error("Please enter a valid email address.")
        else:
            if rem_type == "Overdue":
                ok, err = send_overdue_reminder(rem_emp, rem_course, rem_email, int(rem_days))
            else:
                ok, err = send_upcoming_reminder(rem_emp, rem_course, rem_email, int(rem_days))
            if ok:
                st.success(f"Reminder sent to {rem_email}")
                write_audit("EMAIL_SENT", "reminders", rem_emp, f"{rem_type} reminder for {rem_course} → {rem_email}")
            else:
                st.error(f"Failed to send email: {err}")

    st.markdown("---")
    st.markdown("#### Bulk Overdue Reminders")
    st.caption("Sends one reminder email per overdue record that has an employee email on file.")

    overdue_records = records[records["Status"] == "Overdue"].copy()
    if overdue_records.empty:
        st.success("No overdue records — nothing to remind!")
    else:
        overdue_merged = overdue_records.merge(
            employees[["Employee_Name", "Department"]], on="Employee_Name", how="left"
        )
        st.dataframe(overdue_merged[["Employee_Name", "Course_Name", "Assigned_Date"]],
                     use_container_width=True, hide_index=True)
        bulk_email = st.text_input(
            "HR / Manager Email (receives all bulk reminders)",
            placeholder="hr@company.com"
        )
        bulk_btn = st.button(
            f"Send {len(overdue_records)} Overdue Reminders",
            disabled=not smtp_ready,
            type="primary",
            use_container_width=True
        )
        if bulk_btn:
            if not bulk_email or "@" not in bulk_email:
                st.error("Please enter a valid email address.")
            else:
                sent, failed = 0, 0
                with st.spinner("Sending reminders..."):
                    for _, row in overdue_records.iterrows():
                        assigned = pd.to_datetime(row.get("Assigned_Date"), errors="coerce")
                        days_late = (date.today() - assigned.date()).days if pd.notna(assigned) else 0
                        ok, _ = send_overdue_reminder(
                            row["Employee_Name"], row["Course_Name"], bulk_email, max(days_late, 1)
                        )
                        if ok:
                            sent += 1
                            write_audit("EMAIL_SENT", "reminders", row["Employee_Name"],
                                        f"Bulk overdue for {row['Course_Name']} → {bulk_email}")
                        else:
                            failed += 1
                st.success(f"Sent: {sent} | Failed: {failed}")

    st.markdown("---")
    st.markdown("#### SMTP Configuration Status")
    c1, c2, c3 = st.columns(3)
    c1.metric("SMTP Host", SMTP_HOST)
    c2.metric("SMTP Port", SMTP_PORT)
    c3.metric("Auth Configured", "Yes" if smtp_ready else "No")

elif page == "Training Summary":
    gradient_header("Employee Training Summary", "Track completed trainings per employee with course details on hover")

    # Get completion data
    summary_df = get_employee_completion_summary()

    if summary_df.empty:
        st.info("No completed trainings yet. Courses will appear here as employees complete their training.")
    else:
        # Display metrics at top
        metric_cols = st.columns(3)
        with metric_cols[0]:
            st.metric("Total Employees with Completions", len(summary_df))
        with metric_cols[1]:
            st.metric("Total Trainings Completed", summary_df["Completed_Count"].sum())
        with metric_cols[2]:
            avg_completed = summary_df["Completed_Count"].mean()
            st.metric("Avg. Trainings per Employee", f"{avg_completed:.1f}")

        st.markdown("---")

        # Filter by employee (optional)
        st.markdown("#### Employee Completion List")
        employee_filter = st.multiselect(
            "Filter by Employee (leave empty to show all)",
            sorted(summary_df["Employee_Name"].unique().tolist()),
            key="emp_filter_training_summary"
        )

        display_df = summary_df.copy()
        if employee_filter:
            display_df = display_df[display_df["Employee_Name"].isin(employee_filter)]

        # Create interactive table with hover tooltips using HTML
        st.markdown("""
        <style>
        .completion-row {
            display: flex;
            padding: 0.75rem 1rem;
            margin: 0.5rem 0;
            background: linear-gradient(90deg, rgba(26,26,46,0.6) 0%, rgba(15,52,96,0.4) 100%);
            border-left: 3px solid #c9a84c;
            border-radius: 0.5rem;
            align-items: center;
            gap: 2rem;
            transition: all 0.2s ease;
        }
        .completion-row:hover {
            background: linear-gradient(90deg, rgba(26,26,46,0.9) 0%, rgba(15,52,96,0.7) 100%);
            border-left-color: #e8c96a;
            box-shadow: 0 4px 12px rgba(201,168,76,0.15);
        }
        .emp-name {
            flex: 1;
            font-weight: 600;
            color: #ffffff;
            font-size: 0.95rem;
        }
        .count-badge {
            background: linear-gradient(135deg, #c9a84c, #e8c96a);
            color: #1a1a2e;
            padding: 0.35rem 0.75rem;
            border-radius: 2rem;
            font-weight: 700;
            font-size: 0.85rem;
            min-width: 3rem;
            text-align: center;
        }
        .courses-link {
            color: #0ea5e9;
            font-weight: 600;
            cursor: help;
            text-decoration: underline;
            transition: color 0.2s ease;
        }
        .courses-link:hover {
            color: #c9a84c;
        }
        </style>
        """, unsafe_allow_html=True)

        # Display each employee's completion record
        for idx, row in display_df.iterrows():
            emp_name = row["Employee_Name"]
            count = row["Completed_Count"]
            courses_list = row["Courses"]

            # Create HTML with hover tooltip
            html_content = f"""
            <div class="completion-row">
                <div class="emp-name">{emp_name}</div>
                <div class="count-badge">{count}</div>
                <div class="courses-link" title="{courses_list}">📋 Hover to see courses</div>
            </div>
            """
            st.markdown(html_content, unsafe_allow_html=True)

        st.markdown("---")

        # Completion statistics
        st.markdown("#### Completion Statistics")
        col1, col2 = st.columns(2)

        with col1:
            # Bar chart: Employees by completion count
            completion_dist = display_df["Completed_Count"].value_counts().sort_index().reset_index()
            completion_dist.columns = ["Number of Trainings", "Number of Employees"]

            fig_bar = px.bar(
                completion_dist,
                x="Number of Trainings",
                y="Number of Employees",
                title="Distribution of Completed Trainings",
                color="Number of Employees",
                color_continuous_scale=["#0f3460", "#16c784"],
                labels={"Number of Trainings": "Trainings Completed", "Number of Employees": "Employees"}
            )
            fig_bar.update_layout(
                paper_bgcolor="rgba(0,0,0,0)",
                plot_bgcolor="rgba(0,0,0,0)",
                font=dict(family="Inter", color="#ffffff"),
                margin=dict(t=40, b=10),
                hovermode="x unified"
            )
            st.plotly_chart(fig_bar, use_container_width=True)

        with col2:
            # Pie chart: Top courses completed
            all_courses_str = " ".join(display_df["Courses"].tolist())
            course_counts = {}
            for courses_str in display_df["Courses"].tolist():
                for course in courses_str.split(", "):
                    course = course.strip()
                    if course:
                        course_counts[course] = course_counts.get(course, 0) + 1

            if course_counts:
                course_df = pd.DataFrame(list(course_counts.items()), columns=["Course", "Count"]).sort_values("Count", ascending=False)
                fig_pie = px.pie(
                    course_df.head(8),  # Top 8 courses
                    names="Course",
                    values="Count",
                    title="Top Completed Courses",
                    hole=0.4,
                    color_discrete_sequence=px.colors.sequential.Turbo
                )
                fig_pie.update_layout(
                    paper_bgcolor="rgba(0,0,0,0)",
                    font=dict(family="Inter", color="#ffffff"),
                    margin=dict(t=40, b=10)
                )
                st.plotly_chart(fig_pie, use_container_width=True)

        st.markdown("---")

        # Download CSV
        csv_data = display_df[["Employee_Name", "Completed_Count", "Courses"]].copy()
        csv_data.columns = ["Employee Name", "Trainings Completed", "Courses"]

        st.download_button(
            "📥 Download Training Summary CSV",
            csv_data.to_csv(index=False).encode("utf-8"),
            "training_summary.csv",
            "text/csv",
            use_container_width=True
        )
