-- 1. Profiles Table
CREATE TABLE public.profiles (
  id UUID REFERENCES auth.users(id) ON DELETE CASCADE PRIMARY KEY,
  full_name TEXT,
  currency TEXT DEFAULT 'USD',
  updated_at TIMESTAMP WITH TIME ZONE
);
ALTER TABLE public.profiles ENABLE ROW LEVEL SECURITY;

CREATE POLICY "Users can manage their own profile" ON public.profiles
USING (auth.uid() = id)
WITH CHECK (auth.uid() = id);

-- 2. Accounts Table
CREATE TABLE public.accounts (
  id UUID DEFAULT gen_random_uuid() PRIMARY KEY,
  user_id UUID REFERENCES auth.users(id) NOT NULL,
  name TEXT NOT NULL,
  type TEXT CHECK (type IN ('checking', 'savings', 'credit', 'cash', 'investment')),
  balance NUMERIC(12,2) DEFAULT 0.00,
  created_at TIMESTAMP WITH TIME ZONE DEFAULT now()
);
CREATE INDEX idx_accounts_user ON public.accounts(user_id);
ALTER TABLE public.accounts ENABLE ROW LEVEL SECURITY;

CREATE POLICY "Users can manage their own accounts" ON public.accounts
USING (auth.uid() = user_id)
WITH CHECK (auth.uid() = user_id);

-- 3. Categories Table
CREATE TABLE public.categories (
  id UUID DEFAULT gen_random_uuid() PRIMARY KEY,
  user_id UUID REFERENCES auth.users(id) NOT NULL,
  name TEXT NOT NULL,
  type TEXT CHECK (type IN ('income', 'expense')),
  is_default BOOLEAN DEFAULT FALSE,
  color TEXT,
  UNIQUE(user_id, name, type)
);
ALTER TABLE public.categories ENABLE ROW LEVEL SECURITY;

CREATE POLICY "Users can manage their own categories" ON public.categories
USING (auth.uid() = user_id)
WITH CHECK (auth.uid() = user_id);

-- 4. Transactions Table
CREATE TABLE public.transactions (
  id UUID DEFAULT gen_random_uuid() PRIMARY KEY,
  user_id UUID REFERENCES auth.users(id) NOT NULL,
  account_id UUID REFERENCES public.accounts(id) ON DELETE CASCADE,
  category_id UUID REFERENCES public.categories(id) ON DELETE SET NULL,
  date DATE NOT NULL,
  amount NUMERIC(12,2) NOT NULL,
  description TEXT,
  merchant TEXT,
  status TEXT DEFAULT 'posted',
  receipt_path TEXT,
  created_at TIMESTAMP WITH TIME ZONE DEFAULT now()
);
CREATE INDEX idx_transactions_user_date ON public.transactions(user_id, date DESC);
ALTER TABLE public.transactions ENABLE ROW LEVEL SECURITY;

CREATE POLICY "Users can manage their own transactions" ON public.transactions
USING (auth.uid() = user_id)
WITH CHECK (auth.uid() = user_id);

-- 5. Budgets Table
CREATE TABLE public.budgets (
  id UUID DEFAULT gen_random_uuid() PRIMARY KEY,
  user_id UUID REFERENCES auth.users(id) NOT NULL,
  category_id UUID REFERENCES public.categories(id) NOT NULL,
  amount_limit NUMERIC(12,2) NOT NULL,
  period TEXT DEFAULT 'monthly',
  UNIQUE(user_id, category_id, period)
);
ALTER TABLE public.budgets ENABLE ROW LEVEL SECURITY;

CREATE POLICY "Users can manage their own budgets" ON public.budgets
USING (auth.uid() = user_id)
WITH CHECK (auth.uid() = user_id);

-- 6. Storage Bucket for Receipts
-- (Note: Create bucket 'receipts' manually if not exists via Dashboard)
-- Policies for 'receipts' bucket:
-- CREATE POLICY "View own receipts" ON storage.objects FOR SELECT USING ( bucket_id = 'receipts' AND auth.uid()::text = (storage.foldername(name))[1] );
-- CREATE POLICY "Upload own receipts" ON storage.objects FOR INSERT WITH CHECK ( bucket_id = 'receipts' AND auth.uid()::text = (storage.foldername(name))[1] );
