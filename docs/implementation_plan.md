# Personal Finance App - Implementation Plan

## Goal Description
Build a comprehensive Personal Finance Tracking MVP using Streamlit (frontend) and Supabase (backend). The app will allow users to track expenses, manage budgets, upload receipts (with optional OCR), and view financial dashboards.

## User Review Required
> [!IMPORTANT]
> - **Supabase Auth**: We will use Email/Password auth.
> - **RLS**: Strict Row Level Security is critical for financial data.
> - **Secrets**: Streamlit secrets management is required for Supabase keys.

## Proposed Changes

### Documentation
#### [NEW] [design_spec.md](design_spec.md)
- Comprehensive design document containing:
  1. MVP Feature List
  2. System Architecture
  3. Database Schema (SQL)
  4. RLS + Storage Policies
  5. Streamlit Page/Component Design
  6. Key Workflows
  7. Implementation Steps
  8. Deployment Checklist
  9. Future Enhancements

### Codebase Scaffolding (If functionality is requested later)
- `app.py`: Main entry point.
- `requirements.txt`: Dependencies.
- `/pages`: Streamlit pages.
- `/services`: Supabase and logic.

## Verification Plan
### Manual Verification
- Review the `design_spec.md` against all user requirements.
- Verify SQL schemas are valid Postgres syntax.
- Verify RLS policies cover CRUD operations securely.
