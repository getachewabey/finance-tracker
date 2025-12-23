import streamlit as st
import pandas as pd
from services.data_service import DataService
from utils.ui import setup_sidebar

def show():
    setup_sidebar()
    st.title("Manage Categories 🏷️")
    
    data_service = DataService()
    
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
