import streamlit as st
import sys
import os

st.title("Auth Module Debug")

st.write("### Python Environment")
st.code(f"Python version: {sys.version}")
st.code(f"Current directory: {os.getcwd()}")

st.write("### Testing Imports")

import_success = False
error_message = ""

try:
    st.write("Attempting to import FirebaseAuth...")
    from auth import FirebaseAuth
    import_success = True
    st.success("✅ Successfully imported FirebaseAuth!")
    
    # Test creating an instance
    auth = FirebaseAuth()
    st.success("✅ Successfully created FirebaseAuth instance!")
    
except Exception as e:
    import_success = False
    error_message = str(e)
    st.error(f"❌ Import failed: {error_message}")
    
st.write("### File Structure")
st.code(f"""
auth directory exists: {os.path.exists("auth")}
auth/__init__.py exists: {os.path.exists("auth/__init__.py")}
auth/firebase_auth.py exists: {os.path.exists("auth/firebase_auth.py")}
auth/local_storage.py exists: {os.path.exists("auth/local_storage.py")}
""")

if os.path.exists("auth/__init__.py"):
    with open("auth/__init__.py", "r") as f:
        st.write("### Contents of auth/__init__.py")
        st.code(f.read(), language="python") 