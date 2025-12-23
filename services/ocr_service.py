import google.generativeai as genai
import streamlit as st
import json
import PIL.Image

class OCRService:
    def __init__(self):
        try:
            api_key = st.secrets.get("GEMINI_API_KEY")
            if not api_key:
                st.warning("GEMINI_API_KEY not found in secrets. OCR will not work.")
                self.model = None
            else:
                genai.configure(api_key=api_key)
                self.model = genai.GenerativeModel('gemini-2.5-flash')
        except Exception as e:
            st.error(f"Gemini Init Error: {e}")
            self.model = None

    def parse_receipt(self, image_file):
        if not self.model:
            return None

        try:
            img = PIL.Image.open(image_file)
            prompt = """
            Analyze this receipt and extract:
            1. Merchant Name
            2. Date (YYYY-MM-DD)
            3. Total Amount
            4. Category (guess from: Food, Rent, Utilities, Salary, Entertainment, Transport, Shopping)
            
            Return JSON ONLY: {"merchant": str, "date": str, "amount": float, "category": str}
            """
            
            response = self.model.generate_content([prompt, img])
            text = response.text
            
            # Clean generic markdown if present
            text = text.replace("```json", "").replace("```", "").strip()
            
            return json.loads(text)
        except Exception as e:
            st.error(f"OCR Parsing failed: {e}")
            return None
