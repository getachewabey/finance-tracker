from services.data_service import DataService
import streamlit as st

def seed_defaults():
    ds = DataService()
    
    # Check if we have categories
    existing = ds.get_categories()
    if not existing:
        defaults = [
            ("Food", "expense"),
            ("Rent", "expense"),
            ("Utilities", "expense"),
            ("Salary", "income"),
            ("Entertainment", "expense"),
            ("Transport", "expense")
        ]
        for name, c_type in defaults:
            try:
                ds.create_category(name=name, type=c_type)
            except:
                pass # Ignore duplicates
