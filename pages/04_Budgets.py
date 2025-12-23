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
                try:
                    ds.create_budget(cat_map[c_name], limit)
                    st.success(f"Budget set for {c_name}!")
                    st.rerun()
                except Exception as e:
                    if "duplicate key" in str(e) or "23505" in str(e):
                        st.warning(f"A budget for {c_name} already exists. Please update it in the list below.")
                    else:
                        st.error(f"Error: {e}")
    
    # 2. Manage Budgets (Edit / Delete)
    st.divider()
    st.write("### Your Budgets")
    budgets = ds.get_budgets()
    
    if budgets:
         
         # Display as a table or list with edit options
         for b in budgets:
             c_name = b['categories']['name'] if b['categories'] else "Unknown"
             b_id = b['id']
             
             with st.expander(f"{c_name}: ${b['amount_limit']}", expanded=False):
                 with st.form(f"edit_budget_{b_id}"):
                     new_limit = st.number_input("Monthly Limit ($)", value=float(b['amount_limit']), min_value=1.0, key=f"lim_{b_id}")
                     
                     c1, c2 = st.columns(2)
                     with c1:
                         if st.form_submit_button("Update Limit"):
                             try:
                                 ds.update_budget(b_id, new_limit)
                                 st.success("Updated!")
                                 st.rerun()
                             except Exception as e:
                                 st.error(f"Error: {e}")
                     with c2:
                         if st.form_submit_button("Delete Budget", type="primary"):
                             try:
                                 ds.delete_budget(b_id)
                                 st.warning("Deleted!")
                                 st.rerun()
                             except Exception as e:
                                 st.error(f"Error: {e}")
    else:
        st.info("No budgets set.")

    st.divider()
    
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
        # Create a map of category -> limit from the fetched budgets
        budget_map = {}
        if budgets:
            for b in budgets:
                c_name = b['categories']['name'] if b['categories'] else "Unknown"
                budget_map[c_name] = float(b['amount_limit'])

        # Visualize only budgeted categories (to match "Your Budgets" list)
        # We could also show unbudgeted spending separately, but for consistency let's filter.
        
        has_budgeted_spend = False
        for cat, spent in spend_by_cat.items():
            if cat in budget_map:
                has_budgeted_spend = True
                limit = budget_map[cat]
                st.write(f"**{cat}**")
                col_bar, col_val = st.columns([3, 1])
                progress = min(spent / limit, 1.0)
                # Color bar red if over budget
                color = "red" if spent > limit else "green"
                # Streamlit progress doesn't support color directly in simple API, but we can customize if needed.
                # For now just standard blue/theme.
                col_bar.progress(progress)
                col_val.write(f"${spent:.0f} / ${limit:.0f}")
        
        if not has_budgeted_spend:
            st.info("No spending recorded for your active budgets yet.")
            
        # Optional: Show unbudgeted spending logic could go here
    else:
        st.info("No spending data this month.")

if __name__ == "__main__":
    show()
