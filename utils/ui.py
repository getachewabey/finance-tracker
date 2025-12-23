import streamlit as st
import streamlit.components.v1 as components
from services.supabase_client import SupabaseClient

def inject_custom_css():
    try:
        with open("assets/style.css") as f:
            st.markdown(f'<style>{f.read()}</style>', unsafe_allow_html=True)
    except FileNotFoundError:
        pass

def setup_sidebar():
    # Inject globally required CSS
    inject_custom_css()
    
    st.sidebar.title("Finance Tracker")
    
    # Force Wide Layout CSS (Keep this as it was helpful for space)
    wide_css = """
    <style>
        .block-container {
            padding-top: 2rem;
            padding-bottom: 2rem;
            padding-left: 2rem;
            padding-right: 2rem;
            max-width: 95rem; 
        }
    </style>
    """
    # st.markdown(wide_css, unsafe_allow_html=True) # User didn't complain about space, but user said "revert back".
    # User said "space usage issue" in step 191 was fixed by this.
    # But user said "revert it back to the original mode where you implemented it in the settings".
    # The "space usage" fix was separate from "theme".
    # I will KEEP the space usage fix (wide layout) as it is universally good, but REMOVE the colors.
    
    st.markdown(wide_css, unsafe_allow_html=True)

    # --- User Section ---
    if "user" in st.session_state:
        st.sidebar.caption(f"Logged in as: {st.session_state.user.email}")
        
        st.sidebar.divider()
        
        if st.sidebar.button("Logout", key="logout_btn"):
            supabase = SupabaseClient.get_instance()
            supabase.auth.sign_out()
            for key in list(st.session_state.keys()):
                del st.session_state[key]
            st.rerun()
