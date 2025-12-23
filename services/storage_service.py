from services.supabase_client import SupabaseClient
import streamlit as st

class StorageService:
    def __init__(self):
        self.supabase = SupabaseClient.get_instance()
        self.bucket = "receipts"

    def upload_receipt(self, file, file_name: str, user_id: str):
        """Uploads a file to Supabase Storage and returns the path."""
        try:
            path = f"{user_id}/{file_name}"
            # Read file bytes
            file_bytes = file.getvalue()
            
            # Check if bucket exists (can't create via client easily for public, 
            # assume it exists as per schema instructions or handle error)
            
            # Upload
            res = self.supabase.storage.from_(self.bucket).upload(
                path=path,
                file=file_bytes,
                file_options={"content-type": file.type}
            )
            return path
        except Exception as e:
            st.error(f"Upload failed: {e}")
            return None

    def get_public_url(self, path: str):
        try:
            # For private buckets, we need create_signed_url
            res = self.supabase.storage.from_(self.bucket).create_signed_url(path, 3600) # 1 hour
            return res['signedURL']
        except Exception as e:
            return None
