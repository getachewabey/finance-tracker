import streamlit as st
from services.data_service import DataService
import pandas as pd
from datetime import date
from utils.ui import setup_sidebar

def show():
    setup_sidebar()
    st.title("Budgets 🎯")
    ds = DataService()
    
    # 1. Create Budget
    with st.expander("Set New Budget"):
        with st.form("budget_form"):
            cats = ds.get_categories(type="expense")
            cat_map = {c['name']: c['id'] for c in cats}
            
            c_name = st.selectbox("Category", list(cat_map.keys()))
            limit = st.number_input("Monthly Limit ($)", min_value=1.0)
            
            if st.form_submit_button("Set Budget"):
                # TODO: Implement create_budget in DataService
                # ds.create_budget(cat_map[c_name], limit)
                st.info("Budget creation DB method needed in Phase 2 update. adding now.")
    
    # 2. View Progress
    # Mock for now until DB method added
    st.write("### Monthly Progress")
    
    # Fetch actual spend
    start = date.today().replace(day=1)
    txns = ds.get_transactions(start_date=start)
    df = pd.DataFrame(txns)
    
    if not df.empty:
        df['amount'] = pd.to_numeric(df['amount'])
        expenses = df[df['amount'] < 0].copy()
        expenses['cat_name'] = expenses['categories'].apply(lambda x: x['name'] if x else 'Uncategorized')
        
        spend_by_cat = expenses.groupby('cat_name')['amount'].sum().abs()
        
        # Visualize
        for cat, spent in spend_by_cat.items():
            limit = 500 # Mock limit
            st.write(f"**{cat}**")
            col_bar, col_val = st.columns([3, 1])
            progress = min(spent / limit, 1.0)
            col_bar.progress(progress)
            col_val.write(f"${spent:.0f} / ${limit}")
    else:
        st.info("No spending data this month.")

if __name__ == "__main__":
    show()
