# Personal Finance Tracking Web App - Design Specification

## 1. MVP Feature List
**Target Persona**: Solo freelancer or tech-savvy individual wanting control over their financial data without manual spreadsheet entry.

### Core Schema
- **User Management**: Secure Email/Password login via Supabase Auth.
- **Account Management**: Support for Cash, Bank, Credit Cards with manual balance updates.
- **Transaction Tracking**: Add, edit, delete, and list transactions with categories and filters.
- **Receipts**: Upload receipt images, store securely, and view them linked to transactions.
- **Budgeting**: Set monthly limits per category and track progress.
- **Dashboard**: High-level view of monthly spend, income, and category breakdown.

### Success Metrics
- **Performance**: Transaction list loads in < 2s for 10k rows.
- **Usability**: Log a transaction manually in < 20 seconds.
- **Efficiency**: Receipt upload to parsed transaction (OCR) in < 15 seconds.

---

## 2. System Architecture
**Flow**: `User <-> Streamlit UI <-> Supabase Services <-> Postgres DB`

### Components
1.  **Frontend (Streamlit)**:
    - Renders UI.
    - Manages Session State (`st.session_state`) for user token and form data.
    - Communicates with Supabase via `supabase-py` client.
2.  **Backend (Supabase)**:
    - **Auth**: Handles JWT generation and validation.
    - **Postgres**: Stores all relational data.
    - **Storage**: Private bucket for receipt images.
    - **Edge Functions (Optional/Future)**: Could handle OCR if not done directly in Python.
3.  **OCR Service (Pluggable)**:
    - Python layer integration (e.g., Google Gemini VLM) called from Streamlit.
    - Returns JSON structure to prefill UI forms.

### Authentication & Security Flow
- **Login**: User enters credentials in Streamlit -> `supabase.auth.sign_in_with_password`.
- **Session**: Access Token is stored in `st.session_state` (NOT local storage).
- **Requests**: All DB requests use the authenticated client (forwarding the JWT), ensuring RLS policies apply.

---

## 3. Database Schema (Postgres)
All tables should explicitly enable Row Level Security (RLS).

### A) Profiles (`profiles`)
Links to `auth.users`.
```sql
CREATE TABLE public.profiles (
  id UUID REFERENCES auth.users(id) ON DELETE CASCADE PRIMARY KEY,
  full_name TEXT,
  currency TEXT DEFAULT 'USD',
  updated_at TIMESTAMP WITH TIME ZONE
);
```

### B) Accounts (`accounts`)
```sql
CREATE TABLE public.accounts (
  id UUID DEFAULT gen_random_uuid() PRIMARY KEY,
  user_id UUID REFERENCES auth.users(id) NOT NULL,
  name TEXT NOT NULL,
  type TEXT CHECK (type IN ('checking', 'savings', 'credit', 'cash', 'investment')),
  balance NUMERIC(12,2) DEFAULT 0.00,
  created_at TIMESTAMP WITH TIME ZONE DEFAULT now()
);
-- Index on user_id for faster lookups
CREATE INDEX idx_accounts_user ON public.accounts(user_id);
```

### C) Categories (`categories`)
```sql
CREATE TABLE public.categories (
  id UUID DEFAULT gen_random_uuid() PRIMARY KEY,
  user_id UUID REFERENCES auth.users(id) NOT NULL,
  name TEXT NOT NULL,
  type TEXT CHECK (type IN ('income', 'expense')),
  is_default BOOLEAN DEFAULT FALSE,
  color TEXT,
  UNIQUE(user_id, name, type)
);
```

### D) Transactions (`transactions`)
```sql
CREATE TABLE public.transactions (
  id UUID DEFAULT gen_random_uuid() PRIMARY KEY,
  user_id UUID REFERENCES auth.users(id) NOT NULL,
  account_id UUID REFERENCES public.accounts(id) ON DELETE CASCADE,
  category_id UUID REFERENCES public.categories(id) ON DELETE SET NULL,
  date DATE NOT NULL,
  amount NUMERIC(12,2) NOT NULL, -- Negative for expense, positive for income
  description TEXT,
  merchant TEXT,
  status TEXT DEFAULT 'posted',
  receipt_path TEXT, -- Link to storage
  created_at TIMESTAMP WITH TIME ZONE DEFAULT now()
);
CREATE INDEX idx_transactions_user_date ON public.transactions(user_id, date DESC);
```

### E) Budgets (`budgets`)
```sql
CREATE TABLE public.budgets (
  id UUID DEFAULT gen_random_uuid() PRIMARY KEY,
  user_id UUID REFERENCES auth.users(id) NOT NULL,
  category_id UUID REFERENCES public.categories(id) NOT NULL,
  amount_limit NUMERIC(12,2) NOT NULL,
  period TEXT DEFAULT 'monthly', -- potentially 'yearly'
  UNIQUE(user_id, category_id, period)
);
```

---

## 4. Security: RLS & Policies
**Philosophy**: "Deny by default". Users can only access rows where `user_id == auth.uid()`.

### Database RLS
Enable RLS on all tables:
```sql
ALTER TABLE profiles ENABLE ROW LEVEL SECURITY;
ALTER TABLE accounts ENABLE ROW LEVEL SECURITY;
ALTER TABLE transactions ENABLE ROW LEVEL SECURITY;
-- etc.
```

**Standard Policy Pattern** (Apply to SELECT, INSERT, UPDATE, DELETE):
```sql
CREATE POLICY "Users can manage their own transactions" ON public.transactions
USING (auth.uid() = user_id)
WITH CHECK (auth.uid() = user_id);
```

### Storage RLS (`receipts` bucket)
- **Bucket Type**: Private.
- **Policy**:
```sql
-- Allow authenticated users to view their own folder
-- Assuming folder structure: {user_id}/{filename}
CREATE POLICY "View own receipts" ON storage.objects
FOR SELECT USING ( bucket_id = 'receipts' AND auth.uid()::text = (storage.foldername(name))[1] );

CREATE POLICY "Upload own receipts" ON storage.objects
FOR INSERT WITH CHECK ( bucket_id = 'receipts' AND auth.uid()::text = (storage.foldername(name))[1] );
```

---

## 5. Streamlit UX & Page Map

### Layout
- **Sidebar**: Logo, Navigation Menu (Dashboard, Transactions, Upload, Accounts, Budget), User Profile / Logout.
- **Main Area**: Content based on selection.

### Page Breakdown
1.  **Auth Page** (Default if no session):
    - Tabs: Login / Sign Up.
    - Inputs: Email, Password.
    - Action: Updates `st.session_state.user`.
2.  **Dashboard**:
    - **KPI Row**: Total Spend (Current Month), Net Income.
    - **Charts**: Bar chart of daily spending, Pie chart of top categories.
3.  **Transactions**:
    - **Filter Bar**: Date Range, Account (Multiselect), Search (Text).
    - **Data Grid**: `st.dataframe` handling the list.
    - **Edit Mode**: Clicking a row opens a modal/form to edit details.
4.  **Add/Upload**:
    - **Tabs**: "Manual Entry" vs "Scan Receipt".
    - **OCR Flow**: Upload Image -> Preview -> "Extract Data" button -> Auto-fill form -> "Save".
5.  **Accounts & Budgets**:
    - Tables to manage reference data.
    - Visual progress bars for budgets (`st.progress`).

---

## 6. Key Workflows

### A) OCR Pipeline
1.  User uploads image in Streamlit (`st.file_uploader`).
2.  App sends bytes to OCR Service (e.g., Gemini Flash).
3.  Service returns JSON: `{ "merchant": "Walmart", "date": "2023-10-12", "total": 45.20 }`.
4.  Streamlit populates the "Add Transaction" form with these values.
5.  User verifies and clicks "Save".
6.  App uploads image to Supabase Storage (`/{uid}/{uuid}.jpg`) and saves Transaction to DB.

### B) Transfers
Modeled as **two transactions** (Negative on Source, Positive on Dest) linked by a common ID or just manually managed for MVP.
*Alternative*: A single transaction record with `transfer_account_id` field. For MVP simplicity, stick to manual separate entries or a "Transfer" form that creates both.

---

## 7. Implementation Plan

### Phase 1: Foundation (Days 1-2)
- [ ] Initialize Python environment (`requirements.txt`).
- [ ] Set up Supabase Project (SQL scripts for Tables + RLS).
- [ ] Implement `SupabaseClient` service singleton.
- [ ] Build Auth UI (Login/Signup).

### Phase 2: Core Data (Days 3-5)
- [ ] Build "Accounts" and "Categories" management pages.
- [ ] Build "Transactions" CRUD (Create, Read, Update, Delete).
- [ ] Implement Manual Transaction Form.

### Phase 3: Visuals & Logic (Days 6-8)
- [ ] Build Dashboard with `pandas` and `plotly`/`altair`.
- [ ] Implement Budgeting logic (Comparisons vs Actuals).

### Phase 4: Integrations (Days 9-10)
- [ ] Set up Supabase Storage for receipts.
- [ ] Integrate OCR (Gemini API) for receipt parsing.
- [ ] Implement "Scan Receipt" flow.

---

## 8. Code Organization
```
/
├── .streamlit/
│   └── secrets.toml      # Keys (gitignored)
├── assets/               # Static logo/css
├── components/           # Reusable UI widgets
│   ├── transaction_form.py
│   └── charts.py
├── services/             # Business Logic
│   ├── auth.py
│   ├── db.py             # Supabase wrapper
│   └── ocr.py            # Gemini integration
├── pages/                # Streamlit Multipage
│   ├── 01_Dashboard.py
│   └── ...
├── app.py                # Entry point
├── requirements.txt
└── schema.sql            # DB Reference
```

## 9. Deployment with Streamlit
- **Platform**: Streamlit Community Cloud (easiest) or Docker.
- **Config**: Add `SUPABASE_URL` and `SUPABASE_KEY` to Streamlit Secrets management.
- **Security**: Use the **KEY** (Anon Public) for frontend client. Use Service Role only if strictly necessary for Admin tasks (avoid in Streamlit if possible).

## 10. Non-Functional Requirements
- **Privacy**: No receipt data sent to 3rd party OCR other than the chosen LLM provider (Gemini).
- **Backups**: Supabase handles daily backups.
- **Responsiveness**: Use `st.columns` to adapt to mobile widths where possible.
