# Personal Finance App - Walkthrough

## Overview
We have built a comprehensive personal finance tracker with Streamlit and Supabase.

### Features Implemented
1.  **Authentication**: Email/Password login via Supabase Auth.
2.  **Core Data**: Accounts, Categories, Transactions (Add/Edit/Delete).
3.  **Dashboards**: Interactive charts for spending trends and category breakdown.
4.  **Receipts**: Upload receipt images to private storage.
5.  **AI OCR**: Automatically parse merchant, date, and amount from receipts using Gemini.

## Setup Instructions
1.  **Install**: `pip install -r requirements.txt`
2.  **Database**: Run `schema.sql` in Supabase SQL Editor.
3.  **Secrets**: Update `.streamlit/secrets.toml` with:
    - Supabase URL & Key
    - `GEMINI_API_KEY` (for OCR)
4.  **Run**: `streamlit run app.py`

## User Guide
### 1. Dashboard
View your monthly Net Income and spending breakdown. Use the date filters to analyze specific periods.

### 2. Transactions
- **Manual**: Add transactions directly.
- **List**: Filter by date range to see history.

### 3. Upload Receipt
- Upload an image.
- Click **"Extract Data (AI)"**.
- Review the pre-filled form.
- Save to create a transaction linked to the receipt image.

### 4. Accounts & Budgets
- Create multiple accounts (Checking, Credit Card).
- Track monthly budget limits per category.
