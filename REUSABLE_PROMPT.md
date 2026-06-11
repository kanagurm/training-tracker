# STREAMLIT APP DEVELOPMENT - REUSABLE PROMPT

## Copy-Paste Template for Future AI Sessions

```
You are an expert Python/Streamlit developer working on a production training tracker app.

TECH STACK:
- Streamlit (multi-page app with session state)
- PostgreSQL (SQLAlchemy + psycopg2 with connection pooling)
- Pandas, Plotly Express for charts
- Deployed on Streamlit Cloud (kanagurm/training-tracker)

CURRENT ARCHITECTURE:
- Database: employees, courses, training_records, audit_log tables
- Caching: @st.cache_data(ttl=30) for reads, @st.cache_resource for DB engine
- Performance: Lazy loading (data loaded per-page, NOT globally)
- Theme: Dark navy (#1a1a2e, #0f3460) + gold (#c9a84c), Plus Jakarta Sans font
- Navigation: Sidebar radio with 10 pages (Dashboard, Add Training, Manage Employees/Courses, Browse, Export, Audit Log, Email, Training Summary, Import)

DEVELOPMENT RULES:
1. Load data INSIDE each page (employees = get_employees() after page check)
2. Clear caches selectively after mutations (get_employees.clear() not st.cache_data.clear())
3. Use gradient_header(title, subtitle) for page headers
4. Add audit_log entries for all create/delete/import actions
5. Validate syntax with `py -m py_compile app.py` before commit
6. Push to GitHub immediately after validation

REQUEST:
[Describe what you want: new feature, bug fix, performance optimization, UI change]

REQUIREMENTS:
- [Any specific constraints or acceptance criteria]
- [Performance targets if applicable]
- [UI/UX specifications]

SUCCESS CRITERIA:
[How to verify it works correctly]
```

---

## Common Quick Prompts

### Add New Feature
```
Add a [FEATURE_NAME] page that allows users to [FUNCTIONALITY].
Include: data table, filters, download button, match existing theme.
Load only necessary data, add to NAV_ITEMS, use lazy loading.
```

### Fix Performance Issue
```
App is slow. Optimize by implementing lazy loading - move all get_employees(), 
get_courses(), get_records() calls INSIDE their respective page blocks (after 
`elif page == "..."`). Remove from global scope. Verify loads <2 seconds.
```

### Fix Navigation Bug
```
Page [NAME] not showing when clicked. Debug: ensure proper `elif page == "[NAME]"` 
exists, not embedded in another page's code. Extract to standalone elif block.
```

### Update Branding
```
Update header to show "[COMPANY_NAME] • [LOCATION]". 
Change line ~987 subtitle from current text to new branding.
Maintain gold color (#c9a84c) and uppercase styling.
```

### Add Data Visualization
```
Add a [CHART_TYPE] to [PAGE_NAME] showing [METRIC].
Use Plotly Express, match dark theme (paper_bgcolor="rgba(0,0,0,0)"), 
use Inter font. Data should be loaded per-page (not global).
```

---

## One-Line Troubleshooting Prompts

- **Slow performance**: "Implement lazy loading - move data fetching inside page blocks"
- **Page not showing**: "Fix navigation routing - extract [PAGE] to proper elif block"  
- **Cache not updating**: "Add [function].clear() after mutation in add_/delete_ functions"
- **Styling broken**: "Match existing gradient_header() and dark navy/gold theme"
- **Deploy failing**: "Validate syntax with py -m py_compile, check requirements.txt"

---

## Example Usage

**Instead of**: "The app is slow, can you help?"

**Use**: "Implement lazy loading for all pages. Move get_employees(), get_courses(), 
get_records() from global scope (line ~1003) into each page's elif block. 
Each page should load only the data it needs. Verify Dashboard loads <2 seconds."

---

**Result**: Clear, actionable, produces optimized code on first attempt ✅
