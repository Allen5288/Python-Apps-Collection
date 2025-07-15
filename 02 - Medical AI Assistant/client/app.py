import streamlit as st
from components.upload import render_uploader
from components.chatUI import render_chat
from components.history_download import render_history_download

st.set_page_config(page_title="AI Medical Assistant", page_icon=":robot_face:", layout="wide")
st.title("🩺 Medical Assistant Chatbot")

# Render the file uploader in the sidebar
render_uploader()
# Render the chat interface
render_chat()
# Render the chat history download button
render_history_download()