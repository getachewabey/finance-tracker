import streamlit as st
from services.supabase_client import SupabaseClient
import time

# Page Config
st.set_page_config(
    page_title="Personal Finance Tracker",
    page_icon="💰",
    layout="wide",
    initial_sidebar_state="expanded"
)

from utils.ui import setup_sidebar

# Initialize Supabase
supabase = SupabaseClient.get_instance()

# Note: In app.py, we only setup sidebar IF logged in, inside the main flow

def login_form():
    st.title("Welcome to Finance Tracker 💰")
    
    tab1, tab2 = st.tabs(["Login", "Sign Up"])
    
    with tab1:
        with st.form("login_form"):
            email = st.text_input("Email")
            password = st.text_input("Password", type="password")
            submitted = st.form_submit_button("Log In")
            
            if submitted:
                try:
                    res = supabase.auth.sign_in_with_password({"email": email, "password": password})
                    st.session_state.user = res.user
                    st.session_state.access_token = res.session.access_token
                    
                    # Seed Defaults (Quick Hack for MVP)
                    try:
                        from utils.seed import seed_defaults
                        seed_defaults()
                    except Exception as seed_err:
                        print(f"Seeding warning: {seed_err}")
                        
                    st.success("Logged in successfully!")
                    st.rerun()
                except Exception as e:
                    st.error(f"Login failed: {e}")

    with tab2:
        with st.form("signup_form"):
            email = st.text_input("Email")
            password = st.text_input("Password", type="password")
            submitted = st.form_submit_button("Sign Up")
            
            if submitted:
                try:
                    res = supabase.auth.sign_up({"email": email, "password": password})
                    st.success("Sign up successful! Please check your email to confirm.")
                except Exception as e:
                    st.error(f"Sign up failed: {e}")

def main():
    # Setup Sidebar (Theme Toggle always visible, skip login check here to verify auth)
    setup_sidebar(ignore_login=True)

    # Check Auth
    if "user" not in st.session_state:
        # Try to restore session if persistent (not implemented in MVP yet, relying on simple state)
        login_form()
        return

    # User is logged in
    user_email = st.session_state.user.email
    
    # Navigation logic is handled by Streamlit's native Multipage sidebar for the pages.
    # But since we are in app.py (Home), we might just show the Dashboard content or redirect.
    # Actually, the user asked for sidebar navigation. 
    # With Streamlit Pages, the framework creates the nav.
    # Our `setup_sidebar` adds items to that native sidebar.
    
    # Let's show the Dashboard summary here as the "Home" view
    # or just a welcome message.
    
    st.write("### Review your financial health")
    st.info("Select a page from the sidebar to manage your finances.")

if __name__ == "__main__":
    main()
