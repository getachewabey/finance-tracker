import streamlit as st
from services.data_service import DataService
import pandas as pd
from datetime import date
from utils.ui import setup_sidebar

def show():
    setup_sidebar()
    st.title("Transactions")
    
    data_service = DataService()
    accounts = data_service.get_accounts()
    categories = data_service.get_categories()
    
    # Ensure they have accounts/categories before adding transaction
    if not accounts:
        st.warning("Please create an Account first!")
        return

    # --- Add Transaction Form ---
    with st.expander("➕ Add New Transaction", expanded=False):
        with st.form("add_txn_form"):
            col1, col2 = st.columns(2)
            
            with col1:
                txn_date = st.date_input("Date", value=date.today())
                merchant = st.text_input("Merchant/Payee", placeholder="e.g. Starbucks")
                description = st.text_input("Description", placeholder="details...")
            
            with col2:
                # Account Selection
                account_map = {acc['name']: acc['id'] for acc in accounts}
                account_name = st.selectbox("Account", list(account_map.keys()))
                
                # Category Handling
                # Simple predefined map + existing user cats
                # If no categories, provide basic
                cat_map = {cat['name']: cat['id'] for cat in categories}
                
                # Fallback if no categories exist yet - maybe auto-create logic in Phase 3?
                # For now just showing what exists.
                category_name = st.selectbox("Category", list(cat_map.keys()) if cat_map else ["Uncategorized"])
                
                # Payment flow
                txn_type = st.radio("Type", ["Expense", "Income"], horizontal=True)
                amount_input = st.number_input("Amount", min_value=0.0, step=0.01)

            submitted = st.form_submit_button("Save Transaction")
            
            if submitted:
                if not account_name:
                    st.error("Account required.")
                elif amount_input <= 0:
                    st.error("Amount must be > 0")
                else:
                    try:
                        final_amount = -amount_input if txn_type == "Expense" else amount_input
                        
                        # Handle Category ID
                        cat_id = cat_map.get(category_name) if cat_map else None
                        
                        data_service.create_transaction(
                            account_id=account_map[account_name],
                            date_obj=txn_date,
                            amount=final_amount,
                            category_id=cat_id,
                            description=description,
                            merchant=merchant
                        )
                        st.success("Transaction Saved!")
                        st.rerun()
                    except Exception as e:
                        st.error(f"Error saving: {e}")

    st.divider()
    
    # --- Transactions List ---
    st.subheader("History")
    
    # Simple Filters
    col_f1, col_f2 = st.columns(2)
    with col_f1:
        start_date = st.date_input("Start Date", value=date(2023,1,1))
    with col_f2:
        end_date = st.date_input("End Date", value=date.today())

    txns = data_service.get_transactions(start_date=start_date, end_date=end_date)
    
    if txns:
        # Flatten the object for display
        clean_data = []
        for t in txns:
            clean_data.append({
                "Date": t['date'],
                "Merchant": t['merchant'],
                "Amount": t['amount'],
                "Category": t['categories']['name'] if t['categories'] else "None",
                "Account": t['accounts']['name'] if t['accounts'] else "Unknown",
                "Description": t['description']
            })
        
        st.dataframe(
            pd.DataFrame(clean_data),
            use_container_width=True,
            hide_index=True
        )
    else:
        st.info("No transactions found in this period.")

    st.divider()

    # --- Manage Transactions ---
    if txns:
        with st.expander("Manage Transactions (Edit / Delete)"):
            # Select transaction to manage by description/date/amount
            # A bit tricky to select comfortably. Let's make a selectbox format string
            txn_opts = {f"{t['date']} | {t['merchant']} | ${t['amount']}": t for t in txns}
            selected_txn_str = st.selectbox("Select Transaction", list(txn_opts.keys()))
            
            if selected_txn_str:
                selected_txn = txn_opts[selected_txn_str]
                st.write(f"**Selected:** {selected_txn['description']}")
                
                with st.form("edit_txn_form"):
                    new_desc = st.text_input("Description", value=selected_txn['description'] or "")
                    new_merch = st.text_input("Merchant", value=selected_txn['merchant'] or "")
                    new_amt = st.number_input("Amount", value=float(abs(selected_txn['amount'])), step=0.01)
                    
                    # Update & Delete
                    c1, c2 = st.columns(2)
                    with c1:
                        if st.form_submit_button("Update Transaction"):
                            # If Expense/Income sign logic needed? Assuming keeping same sign for now simplicity
                            # Or we can ask user. For MVP, assume sign is preserved based on existing.
                            original_sign = -1 if float(selected_txn['amount']) < 0 else 1
                            final_amt = new_amt * original_sign
                            
                            try:
                                data_service.update_transaction(
                                    selected_txn['id'],
                                    description=new_desc,
                                    merchant=new_merch,
                                    amount=final_amt
                                    # date, category left as is for simplicity
                                )
                                st.success("Updated!")
                                st.rerun()
                            except Exception as e:
                                st.error(f"Error: {e}")
                    
                    with c2:
                         if st.form_submit_button("Delete Transaction", type="primary"):
                             try:
                                 data_service.delete_transaction(selected_txn['id'])
                                 st.warning("Deleted!")
                                 st.rerun()
                             except Exception as e:
                                 st.error(f"Error: {e}")

if __name__ == "__main__":
    show()
