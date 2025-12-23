import streamlit as st
from supabase import create_client, Client

class SupabaseClient:
    _instance = None
    _client: Client = None

    def __new__(cls):
        if cls._instance is None:
            cls._instance = super(SupabaseClient, cls).__new__(cls)
            cls._instance._init_client()
        return cls._instance

    def _init_client(self):
        try:
            url = st.secrets["SUPABASE_URL"]
            key = st.secrets["SUPABASE_KEY"]
            self._client = create_client(url, key)
        except Exception as e:
            st.error(f"Failed to initialize Supabase client: {e}")
            self._client = None

    @property
    def client(self) -> Client:
        if self._client is None:
            self._init_client()
        return self._client
    
    @staticmethod
    def get_instance():
        if SupabaseClient._instance is None:
            SupabaseClient()
        return SupabaseClient._instance.client
