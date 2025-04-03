import os
import streamlit as st
import json
import datetime
import uuid
from typing import List, Dict, Any, Optional, Union
from llama_index.core import SimpleDirectoryReader, ServiceContext, Response
from llama_index.core.chat_engine import SimpleChatEngine
from llama_index.core.memory import ChatMemoryBuffer
from llama_index.llms.groq import Groq

# Initialize session state variables if they don't exist
if "messages" not in st.session_state:
    st.session_state.messages = []

if "chat_engine" not in st.session_state:
    st.session_state.chat_engine = None

if "authenticated_user" not in st.session_state:
    st.session_state.authenticated_user = None

if "is_authenticated" not in st.session_state:
    st.session_state.is_authenticated = False
    
# Add timestamps to messages if not present
if "message_timestamps" not in st.session_state:
    st.session_state.message_timestamps = []

# ============= JSON Data Storage =============
# Sample users data
USERS = {
    "X12345": {
        "user_name": "John Doe",
        "user_system_prompt": "You are a helpful AI assistant for John Doe. You specialize in technical support and programming advice."
    },
    "X67890": {
        "user_name": "Jane Smith",
        "user_system_prompt": "You are a dedicated AI assistant for Jane Smith. You focus on data analysis and scientific research."
    },
    "X11111": {
        "user_name": "Robert Johnson",
        "user_system_prompt": "You are Robert Johnson's AI helper. You excel at creative writing and marketing suggestions."
    },
    "X22222": {
        "user_name": "Emily Davis",
        "user_system_prompt": "You are Emily's personal AI assistant. You're good at providing health and wellness recommendations."
    },
    "X33333": {
        "user_name": "Michael Wilson",
        "user_system_prompt": "You are Michael's AI companion. You specialize in financial advice and investment strategies."
    }
}

# Guest system prompt for unauthenticated users
GUEST_SYSTEM_PROMPT = "You are a general-purpose AI assistant for a guest user. You can provide helpful information but avoid sharing sensitive data."

def authenticate_user(user_key: str) -> Optional[Dict[str, Any]]:
    """Authenticate user based on their key"""
    if user_key in USERS:
        return {
            "user_key": user_key,
            "user_name": USERS[user_key]["user_name"],
            "user_system_prompt": USERS[user_key]["user_system_prompt"]
        }
    return None

def initialize_chat_engine(system_prompt: str):
    """Initialize the chat engine with the given system prompt"""
    # Initialize Groq LLM
    llm = Groq(
        api_key=os.getenv("GROQ_API_KEY", ""), 
        model="llama3-8b-8192"
    )
    
    # Create memory buffer for chat history
    memory = ChatMemoryBuffer.from_defaults(token_limit=3900)
    
    # Initialize chat engine
    chat_engine = SimpleChatEngine.from_defaults(
        llm=llm,
        system_prompt=system_prompt,
        memory=memory,
        verbose=True
    )
    
    return chat_engine

# Function to format chat history as text with timestamps
def format_chat_history_as_text():
    """Format the chat history as text with timestamps"""
    now = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    text_output = f"Chat History - {now}\n\n"
    
    # Ensure timestamps list is the same length as messages
    while len(st.session_state.message_timestamps) < len(st.session_state.messages):
        st.session_state.message_timestamps.append(datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S"))
    
    for i, message in enumerate(st.session_state.messages):
        timestamp = st.session_state.message_timestamps[i]
        sender = "User" if message["role"] == "user" else "Assistant"
        text_output += f"[{timestamp}] {sender}:\n{message['content']}\n\n"
    
    return text_output

# ============= Main Streamlit App =============
st.subheader('PERSONAL-B0T', divider='red')

# Sidebar for authentication
with st.sidebar:
    st.header("Authentication")
    user_key = st.text_input("Enter your User Key:", type="password")
    
    if st.button("Nouveau Chat"):
        # Clear current chat if there's any
        st.session_state.messages = []
        st.session_state.message_timestamps = []
        
        # Authenticate user
        user = authenticate_user(user_key)
        
        if user:
            st.session_state.authenticated_user = user
            st.session_state.is_authenticated = True
            system_prompt = user["user_system_prompt"]
            st.success(f"Welcome, {user['user_name']}!")
        else:
            st.session_state.authenticated_user = None
            st.session_state.is_authenticated = False
            system_prompt = GUEST_SYSTEM_PROMPT
            st.warning("Invalid key. Continuing as guest.")
        
        # Initialize chat engine with appropriate system prompt
        st.session_state.chat_engine = initialize_chat_engine(system_prompt)
        st.rerun()

# Display current status
if st.session_state.is_authenticated and st.session_state.authenticated_user:
    st.sidebar.info(f"Logged in as: {st.session_state.authenticated_user['user_name']}")
else:
    st.sidebar.info("Currently in Guest Mode")

# Add download button for chat history as text
if st.session_state.messages:
    # Create text format download button
    text_history = format_chat_history_as_text()
    st.sidebar.download_button(
        label="Download Chat History",
        data=text_history,
        file_name="chat_history.txt",
        mime="text/plain"
    )

# Chat interface
if st.session_state.chat_engine:
    # Display chat messages
    for message in st.session_state.messages:
        with st.chat_message(message["role"]):
            st.markdown(message["content"])
    
    # Input for new message
    if prompt := st.chat_input("Type your message here..."):
        # Add timestamp
        current_time = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        st.session_state.message_timestamps.append(current_time)
        
        # Add user message to chat history
        st.session_state.messages.append({"role": "user", "content": prompt})
        
        # Display user message
        with st.chat_message("user"):
            st.markdown(prompt)
        
        # Generate and display assistant response
        with st.chat_message("assistant"):
            with st.spinner("Thinking..."):
                response = st.session_state.chat_engine.chat(prompt)
                st.markdown(response.response)
        
        # Add timestamp for assistant message
        current_time = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        st.session_state.message_timestamps.append(current_time)
        
        # Add assistant response to chat history
        st.session_state.messages.append({"role": "assistant", "content": response.response})
else:
    st.info("Please authenticate using the sidebar to start chatting.")
