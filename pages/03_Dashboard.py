import streamlit as st
import pandas as pd
import plotly.express as px
from services.data_service import DataService
from datetime import date, timedelta
from utils.ui import setup_sidebar

def show():
    setup_sidebar()
    st.title("Financial Dashboard 📊")
    ds = DataService()
    
    # Date Filter
    col1, col2 = st.columns(2)
    with col1:
        start_date = st.date_input("Start Date", value=date.today().replace(day=1))
    with col2:
        end_date = st.date_input("End Date", value=date.today())

    txns = ds.get_transactions(start_date=start_date, end_date=end_date)
    
    if not txns:
        st.info("No data available for this period.")
        return

    df = pd.DataFrame(txns)
    # Ensure amount is numeric (it comes as string from Supabase usually if using Decimal)
    df['amount'] = pd.to_numeric(df['amount'])
    
    # KPI Cards
    income = df[df['amount'] > 0]['amount'].sum()
    expenses = df[df['amount'] < 0]['amount'].sum()
    net = income + expenses
    
    kpi1, kpi2, kpi3 = st.columns(3)
    kpi1.metric("Income", f"${income:,.2f}")
    kpi2.metric("Expenses", f"${abs(expenses):,.2f}", delta=f"{expenses:,.2f}")
    kpi3.metric("Net", f"${net:,.2f}", delta_color="normal")
    
    st.divider()

    # Charts
    c1, c2 = st.columns(2)
    
    with c1:
        st.subheader("Spending by Category")
        expense_df = df[df['amount'] < 0].copy()
        if not expense_df.empty:
            expense_df['abs_amount'] = expense_df['amount'].abs()
            expense_df['category_name'] = expense_df['categories'].apply(lambda x: x['name'] if x else 'Uncategorized')
            
            fig_pie = px.pie(expense_df, values='abs_amount', names='category_name', hole=0.4)
            st.plotly_chart(fig_pie, use_container_width=True)
        else:
            st.text("No expenses to show.")

    with c2:
        st.subheader("Daily Trend")
        daily = df.groupby('date')['amount'].sum().reset_index()
        fig_bar = px.bar(daily, x='date', y='amount', color='amount')
        st.plotly_chart(fig_bar, use_container_width=True)

if __name__ == "__main__":
    show()
