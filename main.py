import streamlit as st
import requests
import sseclient
import json
import logging
from page_servers.chatbot import serve_chatbot
from page_servers.files import serve_file_system

st.set_page_config(
    page_title="RAG-intro",
    layout="wide",
    initial_sidebar_state="expanded",
    page_icon="./assets/image.png"
)

PAGES = {
    "Talk with RAG": serve_chatbot,
    "File Collection": serve_file_system,
}

st.sidebar.title("Navigation")
selection = st.sidebar.selectbox("Go to", list(PAGES.keys()))

page = PAGES[selection]
page()