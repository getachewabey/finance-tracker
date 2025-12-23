import streamlit as st
from services.storage_service import StorageService
from services.ocr_service import OCRService
from services.data_service import DataService
from datetime import date
import uuid
from utils.ui import setup_sidebar

def show():
    setup_sidebar()
    st.title("Scan Receipt 🧾")
    
    # Init Services
    storage = StorageService()
    ocr = OCRService()
    data_service = DataService()
    
    uploaded_file = st.file_uploader("Upload Receipt Image", type=['png', 'jpg', 'jpeg'])
    
    if "ocr_result" not in st.session_state:
        st.session_state.ocr_result = None

    if uploaded_file:
        st.image(uploaded_file, caption="Preview", width=300)
        
        col1, col2 = st.columns(2)
        
        with col1:
            if st.button("✨ Extract Data (AI)"):
                with st.spinner("Analyzing receipt..."):
                    result = ocr.parse_receipt(uploaded_file)
                    if result:
                        st.session_state.ocr_result = result
                        st.success("Data Extracted!")
                    else:
                        st.error("Could not extract data.")

    st.divider()

    # Form to Confirm/Save
    st.subheader("Confirm Details")
    
    # Defaults from OCR or Empty
    defaults = st.session_state.ocr_result or {}
    
    with st.form("save_receipt_form"):
        col_a, col_b = st.columns(2)
        
        with col_a:
            merchant = st.text_input("Merchant", value=defaults.get("merchant", ""))
            d_val = date.today()
            if defaults.get("date"):
                try:
                    d_val = date.fromisoformat(defaults.get("date"))
                except:
                    pass
            txn_date = st.date_input("Date", value=d_val)
            amount = st.number_input("Amount", value=float(defaults.get("amount", 0.0)), step=0.01)

        with col_b:
            # Account & Category Logic
            accounts = data_service.get_accounts()
            acct_names = [a['name'] for a in accounts] if accounts else []
            account_choice = st.selectbox("Account", acct_names)
            
            cats = data_service.get_categories()
            cat_names = [c['name'] for c in cats] if cats else ["Uncategorized"]
            
            # Try to match OCR category
            default_cat_idx = 0
            if defaults.get("category") and defaults.get("category") in cat_names:
                default_cat_idx = cat_names.index(defaults.get("category"))
            
            category_choice = st.selectbox("Category", cat_names, index=default_cat_idx)
            
            description = st.text_input("Notes", value="Receipt Scan")

        submitted = st.form_submit_button("Save Transaction & Receipt")
        
        if submitted and uploaded_file:
            if not account_choice:
                st.error("Account required.")
                return

            try:
                # 1. Upload Image
                user_id = st.session_state.user.id
                ext = uploaded_file.name.split('.')[-1]
                filename = f"{uuid.uuid4()}.{ext}"
                path = storage.upload_receipt(uploaded_file, filename, user_id)
                
                # 2. Save Transaction
                # Need IDs
                acct_id = next(a['id'] for a in accounts if a['name'] == account_choice)
                cat_id = next(c['id'] for c in cats if c['name'] == category_choice)
                
                # We need to update create_transaction to accept receipt_path
                # For now using the existing method which might not have the arg, I need to update DataService first?
                # Ah, standard MVP - let's update DataService signature or just not pass it if I forgot to add it to python method.
                # Checking DataService.create_transaction signature... 
                # It does NOT have receipt_path. I must update it.
                
                # Assuming I will update DataService in next step, I'll call it here.
                data_service.create_transaction_with_receipt(
                    account_id=acct_id,
                    date_obj=txn_date,
                    amount=-abs(amount), # Expense usually
                    category_id=cat_id,
                    description=description,
                    merchant=merchant,
                    receipt_path=path
                )
                
                st.success("Saved successfully!")
                st.session_state.ocr_result = None # Reset
                
            except Exception as e:
                st.error(f"Save failed: {e}")

if __name__ == "__main__":
    show()
