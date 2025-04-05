import streamlit as st
import tempfile
import os
from pdf_processor import process_pdf, display_pdf
from rag_engine import RAGEngine

# Initialize session state for storing chat history and PDF state
if "messages" not in st.session_state:
    st.session_state.messages = []
    
if "pdf_indexed" not in st.session_state:
    st.session_state.pdf_indexed = False
    
if "pdf_path" not in st.session_state:
    st.session_state.pdf_path = None
    
if "pdf_content" not in st.session_state:
    st.session_state.pdf_content = None
    
if "rag_engine" not in st.session_state:
    st.session_state.rag_engine = None

# Check for required API keys and MongoDB URI
groq_api_key = os.environ.get("GROQ_API_KEY")
cohere_api_key = os.environ.get("COHERE_API_KEY")
mongodb_uri = os.environ.get("MONGODB_URI")

if not groq_api_key or not cohere_api_key or not mongodb_uri:
    st.error("⚠️ Missing required API keys or MongoDB URI. Please add GROQ_API_KEY, COHERE_API_KEY, and MONGODB_URI to your environment.")

# Page configuration
st.set_page_config(
    page_title="PDF Chat Assistant",
    page_icon="📄",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Create the main title with an icon
st.markdown('## :material/chat: PDF Chat Assistant')

# Create a sidebar
with st.sidebar:
    st.markdown("## Document Upload 📁")
    
    # File uploader for PDF
    uploaded_file = st.file_uploader("Upload a PDF document", type="pdf")
    
    if uploaded_file is not None:
        # Save the uploaded file to a temporary location
        with tempfile.NamedTemporaryFile(delete=False, suffix='.pdf') as tmp_file:
            tmp_file.write(uploaded_file.getvalue())
            st.session_state.pdf_path = tmp_file.name
        
        # Index button
        if st.button("Index Document", type="primary", use_container_width=True):
            with st.spinner("Processing document..."):
                try:
                    # Process the PDF
                    pdf_content = process_pdf(st.session_state.pdf_path)
                    st.session_state.pdf_content = pdf_content
                    
                    # Initialize RAG engine with both API keys
                    rag_engine = RAGEngine(pdf_content, groq_api_key, cohere_api_key)
                    st.session_state.rag_engine = rag_engine
                    st.session_state.pdf_indexed = True
                    
                    # Success message
                    st.success("Document indexed successfully!")
                    st.info("✅ Ready to chat! Ask questions now!")
                    st.rerun()
                except Exception as e:
                    st.error(f"Error processing document: {str(e)}")
        
        # Display PDF using the streamlit-pdf-viewer with specified size
        st.markdown("## PDF Preview 📄")
        display_pdf(st.session_state.pdf_path)

# Main chat area
if st.session_state.pdf_indexed and st.session_state.rag_engine:
    # Display chat messages
    for message in st.session_state.messages:
        with st.chat_message(message["role"]):
            st.markdown(message["content"])
    
    # Chat input
    if prompt := st.chat_input("Ask a question about your document"):
        # Add user message to chat history
        st.session_state.messages.append({"role": "user", "content": prompt})
        
        # Display user message
        with st.chat_message("user"):
            st.markdown(prompt)
        
        # Display assistant response with streaming
        with st.chat_message("assistant"):
            message_placeholder = st.empty()
            full_response = ""
            
            try:
                # Get streaming response from RAG engine
                stream = st.session_state.rag_engine.query(prompt)
                
                # Process the streaming response
                for chunk in stream:
                    if hasattr(chunk.choices[0].delta, 'content'):
                        content = chunk.choices[0].delta.content
                        if content:
                            full_response += content
                            message_placeholder.markdown(full_response + "✨")
                
                # Update with final response (without cursor)
                message_placeholder.markdown(full_response)
                
                # Add assistant response to chat history
                st.session_state.messages.append({"role": "assistant", "content": full_response})
            except Exception as e:
                st.error(f"Error generating response: {str(e)}")
else:
    # Simple instructions
    st.info("Upload a PDF document in the sidebar and index it to start chatting!")
