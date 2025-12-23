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

    # 3. Manage Existing Accounts
    if accounts:
        with st.expander("Manage Existing Accounts (Edit / Delete)"):
            account_names = [a['name'] for a in accounts]
            selected_acc_name = st.selectbox("Select Account", account_names)
            
            # Find selected account object
            selected_acc = next((a for a in accounts if a['name'] == selected_acc_name), None)
            
            if selected_acc:
                with st.form("edit_account_form"):
                    new_name = st.text_input("Name", value=selected_acc['name'])
                    # Handle Type Selection safely
                    types = ["checking", "savings", "credit", "cash", "investment"]
                    curr_type = selected_acc['type']
                    type_idx = types.index(curr_type) if curr_type in types else 0
                    
                    new_type = st.selectbox("Type", types, index=type_idx)
                    new_balance = st.number_input("Balance", value=float(selected_acc['balance']), step=0.01)
                    
                    col_update, col_delete = st.columns(2)
                    with col_update:
                        submitted_update = st.form_submit_button("Update Account")
                    with col_delete:
                        submitted_delete = st.form_submit_button("Delete Account", type="primary")
                        
                    if submitted_update:
                        try:
                            data_service.update_account(selected_acc['id'], new_name, new_type, new_balance)
                            st.success("Account updated!")
                            st.rerun()
                        except Exception as e:
                            st.error(f"Update failed: {e}")
                            
                    if submitted_delete:
                        try:
                            data_service.delete_account(selected_acc['id'])
                            st.warning("Account deleted!")
                            st.rerun()
                        except Exception as e:
                             st.error(f"Delete failed: {e}")

    st.divider()
    # Categories moved to separate page 06_Categories.py
    st.info("💡 To manage categories, go to the **Categories** page in the sidebar.")

if __name__ == "__main__":
    show()
