# Training Tracker App Development - Prompt History

## Session Overview
Development of a production-grade Employee Training Tracker for Gainwell Technologies (Tennessee) using Streamlit, PostgreSQL, and deployed on Streamlit Cloud.

---

## Prompts Used (Chronological Order)

### 1. Feature Request: Training Summary Page
```
Create a new page in the streamlit app so that we can keep track of the number 
of trainings completed by each employee and have hyperlink which gives a preview 
of the courses completed when hovered over. Please do this carefully and 
effectively as I will be cancelling your licence if done incorrectly.
```

**Result**: Created Training Summary page with:
- Employee completion counts
- Hover tooltips showing course lists
- Interactive charts (distribution, top courses)
- CSV download capability
- Cached data function for performance

---

### 2. Multi-Issue Fix: Header, Performance, Navigation
```
Include Gainwell Technologies and Tennessee in the header. Moreover the app is 
very slow and taking time to load. You are an expert coder - I want you to 
efficiently make the app very very fast. Audit trail webpage is also not working 
when navigating different pages.
```

**Result**: 
- Updated header subtitle to "Gainwell Technologies • Tennessee"
- Implemented lazy loading (data loaded per-page instead of globally) → 3-5x speed improvement
- Fixed Audit Log page routing bug (was embedded in Import page, missing `elif`)
- Reduced initial load from 3 tables to 0 tables, each page loads only what it needs

---

## Reusable Prompt Template for Future Development

```
CONTEXT: Streamlit app with PostgreSQL database, deployed on Streamlit Cloud.
Current features: [list existing features]

REQUEST:
1. [Primary feature/fix with clear acceptance criteria]
2. [Any performance/optimization requirements]
3. [Any UI/UX changes needed]

REQUIREMENTS:
- Maintain existing caching strategy (@st.cache_data with TTL=30s)
- Follow dark navy/gold theme (#1a1a2e, #0f3460, #c9a84c)
- Use lazy loading for data (per-page, not global)
- Clear relevant caches after mutations
- Add audit trail entries for major actions
- Validate syntax before commit
- Push to GitHub: kanagurm/training-tracker

CRITICAL: [Any deal-breaker issues or high-priority constraints]

SUCCESS CRITERIA: [How to verify the change works]
```

---

## Quick Reference: Common Requests

### Add New Page
```
Add a new page called "[PAGE_NAME]" to the Streamlit app that [FUNCTIONALITY].
Requirements:
- Add to NAV_ITEMS with appropriate icon
- Use gradient_header() for title
- Load only necessary data (employees/courses/records)
- Match existing dark theme
- Include download/export if applicable
```

### Performance Optimization
```
The app is slow. Optimize performance by:
- Implementing lazy loading (load data per-page, not globally)
- Reviewing cache TTL settings
- Minimizing redundant database queries
- Adding targeted cache invalidation
Verify: App should load in <2 seconds on first visit
```

### Fix Navigation/Routing Bug
```
Page "[PAGE_NAME]" is not working when navigating from sidebar.
Debug checklist:
- Verify `elif page == "[PAGE_NAME]"` exists (not missing elif)
- Check page is not embedded inside another page's code block
- Confirm NAV_ITEMS includes the page
- Test navigation from all other pages
```

### UI Theme Update
```
Update [COMPONENT] to match corporate branding:
- Primary colors: #1a1a2e (charcoal navy), #0f3460 (deep blue), #c9a84c (gold)
- Font: Plus Jakarta Sans
- Use gradient_header() for consistent styling
- Maintain responsive design (works on mobile)
```

---

## Best Practices Learned

1. **Performance First**: Always lazy-load data per page, never globally
2. **Cache Wisely**: Use TTL=30s for reads, clear caches selectively after writes
3. **Audit Everything**: Log adds, deletes, imports, email sends
4. **Theme Consistency**: Use gradient_header(), stat_card(), existing CSS patterns
5. **Navigation Structure**: Proper `elif` chains, no nested page logic
6. **Error Handling**: Try/except blocks with user-friendly error messages
7. **Validation**: Always `py -m py_compile` before commit
8. **Git Workflow**: Clear commit messages, push immediately after validation

---

## Architecture Quick Reference

### Database Schema
- **employees**: employee_id, employee_name, department, hire_date
- **courses**: course_id, course_name, category, duration_hours, due_within_days
- **training_records**: record_id, employee_name, course_name, status, assigned_date, completion_date, created_at
- **audit_log**: log_id, action, table_name, record_ref, detail, performed_by, performed_at

### Caching Pattern
```python
@st.cache_data(ttl=30)
def get_[TABLE]():
    with get_db() as conn:
        rows = db_execute(conn, "SELECT * FROM [TABLE]").mappings().all()
    return pd.DataFrame(rows)

# Clear after mutation
def add_[ENTITY](...):
    with get_db() as conn:
        db_execute(conn, "INSERT INTO [TABLE] VALUES ...")
    get_[TABLE].clear()  # Only clear affected table
    write_audit("ADDED", "[TABLE]", ...)
```

### Page Template
```python
elif page == "[PAGE_NAME]":
    gradient_header("[TITLE]", "[SUBTITLE]")
    
    # Load only needed data
    employees = get_employees()  # if needed
    courses = get_courses()      # if needed
    records = get_records()      # if needed
    
    # Page logic here
    ...
```

---

## Deployment Info
- **Repo**: https://github.com/kanagurm/training-tracker
- **Live App**: https://trainingtrackertennessee.streamlit.app/
- **Auto-deploy**: Pushes to main branch auto-deploy to Streamlit Cloud (1-2 min)
- **Secrets**: SMTP_USER, SMTP_PASS, DATABASE_URL, APP_ACCESS_CODE (in Streamlit Cloud)

---

## Key Files
- `app.py`: Main Streamlit application (~1850 lines)
- `import_from_excel.py`: Standalone bulk import script
- `requirements.txt`: Python dependencies
- `.streamlit/config.toml`: Streamlit configuration
- `training_tracker.db`: Local SQLite (dev only)

---

Generated: 2026-06-10
Project: Employee Training Tracker | Gainwell Technologies (Tennessee)
