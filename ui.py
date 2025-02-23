# app.py

import streamlit as st
from streamlit import session_state
import time
import base64
import os
from vectors import EmbeddingsManager  # Import the EmbeddingsManager class
from chatbot import ChatbotManager     # Import the ChatbotManager class

# Function to display the PDF of a given file
def displayPDF(file):
    # Reading the uploaded file
    pdf_path = os.path.join(os.getcwd(), "temp.pdf")
    if file is not None:
        with open(pdf_path, "wb") as f:
            f.write(uploaded_file.getbuffer())

        # Embed PDF using the local file method
        pdf_display = '<iframe src="{pdf_path}" width="100%" height="600"></iframe>'
    
    # Displaying the PDF
    st.markdown(pdf_display, unsafe_allow_html=True)

# Initialize session_state variables if not already present
if 'temp_pdf_path' not in st.session_state:
    st.session_state['temp_pdf_path'] = None

if 'chatbot_manager' not in st.session_state:
    st.session_state['chatbot_manager'] = ChatbotManager(
                            model_name="BAAI/bge-small-en",
                            device="cpu",
                            encode_kwargs={"normalize_embeddings": True},
                            llm_model="llama3.2:3b",
                            llm_temperature=0.7,
                            qdrant_url="http://localhost:6333",
                            collection_name="vector_db"
                        )

if 'messages' not in st.session_state:
    st.session_state['messages'] = []

# Set the page configuration to wide layout and add a title
st.set_page_config(
    page_title="Information Retrieval from Technical Documents",
    layout="wide",
    initial_sidebar_state="expanded",
)

# Sidebar
with st.sidebar:
    # You can replace the URL below with your own logo URL or local image path
    st.image("logo.png", use_container_width=True)
    st.markdown("### 📚 Document Assistant")
    st.markdown("---")
    
    # Navigation Menu
    menu = ["🏠 Home", "📤 Upload PDFs", "🤖 Chatbot"]
    choice = st.selectbox("Navigate", menu)

# Home Page
if choice == "🏠 Home":
    st.title("📄 Retreive Information from Documents")
    st.markdown("""
    Welcome! 🚀

    **Built using Open Source Stack (Llama 3.2, BGE Embeddings, and Qdrant running locally within a Docker Container.)**

    - **Upload Documents**: Easily upload your technical PDF documents.
    - **Chat**: Interact with your documents through our intelligent chatbot.

    """)

# Upload Page
elif choice == "📤 Upload PDFs":
    st.title("📤Upload Technical Documents in PDF")
    st.markdown("---")
    uploaded_file = st.file_uploader("Upload a PDF", type=["pdf"])
    if uploaded_file is not None:
        st.success("📄 File Uploaded Successfully!")
        # Display file name and size
        st.markdown(f"**Filename:** {uploaded_file.name}")
        st.markdown(f"**File Size:** {uploaded_file.size} bytes")
        
        # Save the uploaded file to a temporary location
        temp_pdf_path = "temp.pdf"
        with open(temp_pdf_path, "wb") as f:
            f.write(uploaded_file.getbuffer())
        
        # Store the temp_pdf_path in session_state
        st.session_state['temp_pdf_path'] = temp_pdf_path
        if st.session_state['temp_pdf_path'] is None:
                st.warning("⚠️ Please upload a PDF first.")
        else:
            try:
                # Initialize the EmbeddingsManager
                embeddings_manager = EmbeddingsManager(
                    model_name="BAAI/bge-small-en",
                    device="cpu",
                    encode_kwargs={"normalize_embeddings": True},
                    qdrant_url="http://localhost:6333",
                    collection_name="vector_db"
                )
                
                with st.spinner("🔄 Embeddings are in process..."):
                    # Create embeddings
                    result = embeddings_manager.create_embeddings(st.session_state['temp_pdf_path'])
                    time.sleep(1)  # Optional: To show spinner for a bit longer
                st.success(result)
                
                # Initialize the ChatbotManager after embeddings are created
                if st.session_state['chatbot_manager'] is None:
                    st.session_state['chatbot_manager'] = ChatbotManager(
                        model_name="BAAI/bge-small-en",
                        device="cpu",
                        encode_kwargs={"normalize_embeddings": True},
                        llm_model="llama3.2:3b",
                        llm_temperature=0.7,
                        qdrant_url="http://localhost:6333",
                        collection_name="vector_db"
                    )
                
            except FileNotFoundError as fnf_error:
                st.error(fnf_error)
            except ValueError as val_error:
                st.error(val_error)
            except ConnectionError as conn_error:
                st.error(conn_error)
            except Exception as e:
                st.error(f"An unexpected error occurred: {e}")

# Chatbot Page
elif choice == "🤖 Chatbot":
    st.title("🤖 Chatbot Interface (Llama 3.2 RAG 🦙)")
    st.markdown("---")
    st.header("💬 Chat with Documents")
    
    if st.session_state['chatbot_manager'] is None:
        st.info("🤖 Please upload a PDF and create embeddings to start chatting.")
    else:
        # Display existing messages
        for msg in st.session_state['messages']:
            st.chat_message(msg['role']).markdown(msg['content'])

        # User input
        if user_input := st.chat_input("Type your message here..."):
            # Display user message
            st.chat_message("user").markdown(user_input)
            st.session_state['messages'].append({"role": "user", "content": user_input})

            with st.spinner("🤖 Responding..."):
                try:
                    # Get the chatbot response using the ChatbotManager
                    answer = st.session_state['chatbot_manager'].get_response(user_input)
                    time.sleep(1)  # Simulate processing time
                except Exception as e:
                    answer = f"⚠️ An error occurred while processing your request: {e}"
            
            # Display chatbot message
            st.chat_message("assistant").markdown(answer)
            st.session_state['messages'].append({"role": "assistant", "content": answer})

# Footer
st.markdown("---")
st.markdown("© 2025 Information Retriever from Documents using RAG by CND/CISDG. All rights reserved. 🛡️")