# Personal Finance Tracking App 💰

A secure, Streamlit-based personal finance application using Supabase for backend services (Auth, DB, Storage) and Google Gemini for AI Receipt Parsing.

![Status](https://img.shields.io/badge/Status-Complete-green)
![Tech](https://img.shields.io/badge/Stack-Streamlit%20|%20Supabase%20|%20Python-blue)

## Features

- **Authentication**: Secure Email/Password login.
- **Financial Tracking**: 
    - Manage Accounts (Checking, Savings, Credit).
    - Track Income & Expenses with Categories.
    - View Dashboards & Spending Trends.
- **AI Integration**:
    - **Smart Receipt Scanning**: Upload a receipt image, and the app uses Gemini AI to automatically extract the Merchant, Date, Amount, and Category.
- **Privacy & Security**:
    - **RLS**: Row Level Security ensures users see only their data.
    - **Private Storage**: Receipt images are stored in private buckets accessible only to the owner.

## Quick Start

1.  **Clone & Install**:
    ```bash
    pip install -r requirements.txt
    ```

2.  **Supabase Setup**:
    - Create a new project on [Supabase.com](https://supabase.com).
    - Run the provided SQL script: [`schema.sql`](schema.sql) in the Supabase SQL Editor to create tables and policies.
    - Create a Storage Bucket named `receipts` (Private).

3.  **Configuration**:
    - Rename `.streamlit/secrets.toml.example` to `.streamlit/secrets.toml` (or create it).
    - Add your keys:
      ```toml
      SUPABASE_URL = "your-project-url"
      SUPABASE_KEY = "your-anon-key"
      GEMINI_API_KEY = "your-gemini-key"
      ```

4.  **Run**:
    ```bash
    streamlit run app.py
    ```

## Documentation

Detailed documentation is available in the [`docs/`](docs/) directory:

- **[Design Specification](docs/design_spec.md)**: Full architecture, schema, and page design.
- **[Implementation Plan](docs/implementation_plan.md)**: Step-by-step build log.
- **[Walkthrough](docs/walkthrough.md)**: User guide and features overview.
- **[Deployment Guide](docs/DEPLOYMENT.md)**: Instructions for Streamlit Cloud.

## Project Structure

```
personal-finance-app/
├── app.py                  # Main Entry Point
├── pages/                  # Streamlit Pages
│   ├── 01_Accounts.py
│   ├── 02_Transactions.py
│   ├── 03_Dashboard.py
│   ├── 04_Budgets.py
│   └── 05_Upload_Receipt.py
├── services/               # Business Logic
│   ├── supabase_client.py
│   ├── data_service.py
│   ├── storage_service.py
│   └── ocr_service.py
├── services/               # DB Schema
│   └── schema.sql
├── docs/                   # Documentation
│   └── design_spec.md
└── requirements.txt
```
