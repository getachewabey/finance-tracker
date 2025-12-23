import streamlit as st
import pandas as pd
from services.data_service import DataService
from utils.ui import setup_sidebar

def show():
    setup_sidebar()
    st.title("Accounts Management")
    
    data_service = DataService()
    
    # 1. Accounts List
    st.subheader("Your Accounts")
    accounts = data_service.get_accounts()
    
    if accounts:
        df = pd.DataFrame(accounts)
        st.dataframe(
            df[["name", "type", "balance", "created_at"]],
            use_container_width=True,
            hide_index=True
        )
    else:
        st.info("No accounts found. Create one below!")

    st.divider()

    # 2. Create Account Form
    st.subheader("Add New Account")
    
    with st.form("create_account_form"):
        col1, col2 = st.columns(2)
        with col1:
            name = st.text_input("Account Name", placeholder="e.g. Chase Checking")
            acc_type = st.selectbox("Type", ["checking", "savings", "credit", "cash", "investment"])
        with col2:
            balance = st.number_input("Current Balance", min_value=0.0, step=0.01)
        
        submitted = st.form_submit_button("Create Account")
        
        if submitted:
            if not name:
                st.error("Account Name is required.")
            else:
                try:
                    # For credit cards, balance implies debt usually, but let's just take raw number
                    # Protocol: User enters positive number.
                    # If it's a credit card, maybe we should treat it as negative? 
                    # Let's trust user input for now.
                    data_service.create_account(name, acc_type, balance)
                    st.success(f"Account '{name}' created!")
                    st.rerun()
                except Exception as e:
                    st.error(f"Error creating account: {e}")

    st.divider()
    
    # 3. Manage Categories
    with st.expander("Manage Categories"):
        col_cat1, col_cat2 = st.columns(2)
        with col_cat1:
            st.subheader("Existing Categories")
            cats = data_service.get_categories()
            if cats:
                df_cats = pd.DataFrame(cats)
                st.dataframe(df_cats[['name', 'type']], hide_index=True, use_container_width=True)
            else:
                st.info("No categories found.")
        
        with col_cat2:
            st.subheader("Add Category")
            with st.form("add_category_form"):
                new_cat_name = st.text_input("Category Name", placeholder="e.g. Groceries")
                new_cat_type = st.selectbox("Type", ["expense", "income"])
                submitted_cat = st.form_submit_button("Add Category")
                
                if submitted_cat:
                    if new_cat_name:
                        try:
                            # Use a default color for now
                            data_service.create_category(new_cat_name, new_cat_type)
                            st.success(f"Added '{new_cat_name}'!")
                            st.rerun()
                        except Exception as e:
                            st.error(f"Could not add category. It might already exist.")
                    else:
                        st.warning("Enter a name.")

if __name__ == "__main__":
    show()
