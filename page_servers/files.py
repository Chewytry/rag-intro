import streamlit as st
from streamlit_pdf_viewer import pdf_viewer
import requests
import os
import base64

API_URL = "http://localhost:5000"  # Replace with your Flask API URL

def list_files():
    response = requests.get(f"{API_URL}/show_data_files")
    if response.status_code == 200:
        return response.json()
    else:
        st.error("Failed to fetch files.")
        return []

def index_database():
    response = requests.post(f"{API_URL}/update_database")
    if response.status_code == 200:
        st.success("All files updated.")
    else:
        st.error("Failed to update all files.")

def show_pdf(file_path, col):
    with col:
        pdf_viewer(input = file_path, height=700)
    # with open(file_path, "rb") as file:
        # base64_pdf = base64.b64encode(file.read()).decode('utf-8')
    #pdf_display = f'<iframe src="data:application/pdf;base64,{base64_pdf}" width="600" height="700" type="application/pdf"></iframe>'
    #col.markdown(pdf_display, unsafe_allow_html=True)

def delete_file(file_name):
    response = requests.post(f"{API_URL}/remove_file", json={"file_name": file_name})
    if response.status_code == 200:
        st.success(f"{file_name} deleted.")
    else:
        st.error(f"Failed to delete {file_name}.")

def delete_all_files():
    response = requests.post(f"{API_URL}/clear_database")
    if response.status_code == 200:
        st.success("All files deleted.")
    else:
        st.error("Failed to delete all files.")

def add_file(file):
    if file is not None:
        file_path = os.path.join("data", file.name)
        with open(file_path, "wb") as f:
            f.write(file.getbuffer())
        response = requests.post(f"{API_URL}/add_file", json={"file_path": file_path})
        if response.status_code == 200:
            st.success(f"{file.name} added.")
        else:
            st.error(f"Failed to add {file.name}.")

def serve_file_system():
    if "viewed_pdf" not in st.session_state:
        st.session_state.viewed_pdf = None

    st.title("File Management System")

    c1, c2 = st.columns(2)
    # Add new file
    c1.markdown("### Add a New PDF File")
    uploaded_file = c1.file_uploader("Choose a PDF file", type="pdf")
    if c1.button("Upload"):
        add_file(uploaded_file)
        st.experimental_rerun()

    d1, d2 = c2.columns(2)
    # Delete all files
    d1.markdown("### Delete chromaDB")
    if d1.button("Delete All Files"):
        delete_all_files()
        st.experimental_rerun()
    d2.markdown("### Update chromaDB")
    if d2.button("Re-Index DB"):
        index_database()
        st.rerun()

    # List and manage files
    l1,l2 = st.columns(2)
    l1.markdown("### List of PDF Files")
    files = list_files()
    for file_name in files:
        col1, col2, col3 = l1.columns([3, 1, 1])
        col1.write(file_name)
        if col2.button("View", key=f"view_{file_name}"):
            st.session_state.viewed_pdf = os.path.join("data", file_name)
            st.experimental_rerun()
        if col3.button("Delete", key=f"delete_{file_name}"):
            delete_file(file_name)
            st.experimental_rerun()

    # Display viewed PDF
    l2.markdown("### File View")
    if st.session_state.viewed_pdf:
        if l2.button("Close File View"):
            st.session_state.viewed_pdf = None
            st.experimental_rerun()
        show_pdf(st.session_state.viewed_pdf, l2)