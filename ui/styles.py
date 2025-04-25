import os
import streamlit as st
from pathlib import Path

def load_styles():
    """Load custom CSS and JavaScript files for better UI styling."""
    project_root = Path(__file__).parent.parent.absolute()
    
    # Load custom CSS
    css_path = os.path.join(project_root, "static", "custom.css")
    if os.path.exists(css_path):
        with open(css_path, "r") as css_file:
            css = css_file.read()
            st.markdown(f"<style>{css}</style>", unsafe_allow_html=True)
    
    # Load custom JavaScript
    js_path = os.path.join(project_root, "static", "custom.js")
    if os.path.exists(js_path):
        with open(js_path, "r") as js_file:
            js = js_file.read()
            st.markdown(f"<script>{js}</script>", unsafe_allow_html=True) 