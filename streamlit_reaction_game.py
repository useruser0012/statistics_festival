import streamlit as st
from google.oauth2.service_account import Credentials

scope = ['https://spreadsheets.google.com/feeds', 'https://www.googleapis.com/auth/drive']

try:
    creds = Credentials.from_service_account_info(st.secrets["gcp_service_account"], scopes=scope)
    st.success("Credentials loaded successfully")
except Exception as e:
    st.error(f"Credentials error: {e}")

