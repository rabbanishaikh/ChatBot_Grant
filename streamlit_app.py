import streamlit as st
from openai import OpenAI
import time

# Set page configuration
st.set_page_config(
    page_title="DeepSeek AI Assistant",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Custom CSS for light mode UI
st.markdown("""
<style>
    /* Base styles and fonts */
    @import url('https://fonts.googleapis.com/css2?family=Inter:wght@300;400;500;600;700&display=swap');
    
    html, body, [class*="css"] {
        font-family: 'Inter', sans-serif;
    }
    
    /* Main app background */
    .stApp {
        background-color: #F8F9FA;
    }
    
    /* Scrollable chat container */
    .main-container {
        height: calc(100vh - 200px);
        overflow-y: auto;
        padding-bottom: 120px;
    }
    
    /* Fixed input container */
    .fixed-input-container {
        position: fixed;
        bottom: 20px;
        left: 50%;
        transform: translateX(-50%);
        width: 85%;
        z-index: 999;
        background: transparent;
    }
    
    /* Chat message styling */
    .chat-message {
        padding: 1.5rem; 
        border-radius: 1rem; 
        margin-bottom: 0.5rem; 
        display: flex;
        flex-direction: row;
        align-items: flex-start;
        gap: 1rem;
        box-shadow: 0 2px 5px rgba(0,0,0,0.05);
        animation: fadeIn 0.3s ease-in-out;
    }
    
    @keyframes fadeIn {
        from { opacity: 0; transform: translateY(10px); }
        to { opacity: 1; transform: translateY(0); }
    }
    
    .chat-message.user {
        background-color: #E9ECEF;
        border-left: 4px solid #ADB5BD;
    }
    
    .chat-message.bot {
        background-color: #E3F2FD;
        border-left: 4px solid #0d6efd;
    }
    
    .chat-message .avatar {
        width: 3rem;
        height: 3rem;
        border-radius: 1rem;
        display: flex;
        align-items: center;
        justify-content: center;
        font-size: 1.5rem;
        box-shadow: 0 2px 5px rgba(0,0,0,0.1);
    }
    
    .chat-message .avatar.user {
        background: linear-gradient(135deg, #ADB5BD, #6C757D);
        color: white;
    }
    
    .chat-message .avatar.bot {
        background: linear-gradient(135deg, #0d6efd, #0a58ca);
        color: white;
    }
    
    .chat-message .message {
        flex-grow: 1;
        line-height: 1.6;
        color: #212529;
        font-weight: 500;
    }
    
    /* Input box styling */
    .input-box {
        background-color: #FFFFFF;
        border-radius: 0.75rem;
        padding: 0.5rem;
        box-shadow: 0 2px 8px rgba(0,0,0,0.05);
    }
    
    /* Button styling */
    .stButton button {
        border-radius: 0.75rem;
        padding: 0.5rem 1.5rem;
        font-weight: 600;
        box-shadow: 0 2px 5px rgba(0,0,0,0.1);
        transition: all 0.3s ease;
        background: #87CEEB;
        color: white;
        border: none;
    }
    
    .stButton button:hover {
        background-color: #6fa8dc;
        transform: translateY(-1px);
        box-shadow: 0 4px 8px rgba(0,0,0,0.15);
    }
    
    /* Sidebar styling */
    [data-testid="stSidebar"] {
        background-color: #F0F2F5;
    }
    
    .sidebar-content {
        padding: 1.5rem;
        background-color: #FFFFFF;
        border-radius: 1rem;
        margin-bottom: 1.5rem;
        box-shadow: 0 2px 5px rgba(0,0,0,0.05);
    }
    
    /* Header styling */
    .main-header {
        text-align: center;
        margin-bottom: 2rem;
        padding: 1.5rem;
        background-color: #FFFFFF;
        color: #212529;
        border-radius: 1rem;
        box-shadow: 0 4px 12px rgba(0, 0, 0, 0.1);
    }
</style>
""", unsafe_allow_html=True)

# Initialize session state variables
if "messages" not in st.session_state:
    st.session_state.messages = []

if "api_key" not in st.session_state:
    st.session_state.api_key = "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"

if "show_welcome" not in st.session_state:
    st.session_state.show_welcome = True

# Fixed model parameters
temperature = 0.7
max_tokens = 2048
model = "deepseek/deepseek-r1:free"

# Header
st.markdown("""
<div class='main-header'>
    <h1>AI Assistant</h1>
    <p>Powered by advanced AI to help answer your questions</p>
</div>
""", unsafe_allow_html=True)

# Sidebar for settings
with st.sidebar:
    st.markdown("<div class='sidebar-content'>", unsafe_allow_html=True)
    st.subheader("💬 Chat Options")
    
    col1, col2 = st.columns(2)
    with col1:
        if st.button("🗑️ Clear Chat", use_container_width=True):
            st.session_state.messages = []
            st.session_state.show_welcome = True

    with col2:
        if st.button("📝 New Chat", use_container_width=True):
            st.session_state.messages = []
            st.session_state.show_welcome = True
    
    st.markdown("</div>", unsafe_allow_html=True)
    
    st.markdown("<div class='sidebar-content'>", unsafe_allow_html=True)
    st.markdown("### About")
    st.markdown("""
    This AI assistant can
    
    - Get instant answers to your questions
    - Have natural conversations
    - Explore ideas and concepts
    
    v1.0.0 | © 2025
    """)
    st.markdown("</div>", unsafe_allow_html=True)

# Function to display chat messages
def display_chat_messages():
    if not st.session_state.messages:
        if st.session_state.show_welcome:
            st.markdown("""
            <div class="empty-chat-state">
                <div class="welcome-text">What can I help with?</div>
            </div>
            """, unsafe_allow_html=True)
        return
    
    for msg in st.session_state.messages:
        if msg["role"] == "user":
            st.markdown(f"""
            <div class="chat-message user">
                <div class="avatar user">👤</div>
                <div class="message">{msg["content"]}</div>
            </div>
            """, unsafe_allow_html=True)
        else:
            st.markdown(f"""
            <div class="chat-message bot">
                <div class="avatar bot">🤖</div>
                <div class="message">{msg["content"]}</div>
            </div>
            """, unsafe_allow_html=True)

# Function to generate response
def generate_response(prompt):
    try:
        with st.spinner("Thinking..."):
            client = OpenAI(
                base_url="https://openrouter.ai/api/v1",
                api_key=st.session_state.api_key,
            )
            
            messages = [{"role": m["role"], "content": m["content"]} for m in st.session_state.messages]
            
            message_placeholder = st.empty()
            full_response = ""
            
            completion = client.chat.completions.create(
                extra_headers={
                    "HTTP-Referer": "https://deepseek-ai-assistant.com",
                    "X-Title": "AI Assistant",
                },
                model=model,
                messages=messages,
                temperature=temperature,
                max_tokens=max_tokens,
                stream=True
            )
            
            # Stream the response
            for chunk in completion:
                if chunk.choices and chunk.choices[0].delta and chunk.choices[0].delta.content:
                    content_chunk = chunk.choices[0].delta.content
                    full_response += content_chunk
                    message_placeholder.markdown(f"""
                    <div class="chat-message bot">
                        <div class="avatar bot">🤖</div>
                        <div class="message">{full_response}█</div>
                    </div>
                    """, unsafe_allow_html=True)
            
            # Add final response without cursor
            st.session_state.messages.append({"role": "assistant", "content": full_response})
            
    except Exception as e:
        error_message = str(e)
        st.error(f"Error: {error_message}")
        st.session_state.messages.append({
            "role": "assistant", 
            "content": "I'm sorry, I encountered an error. Please try again."
        })

# Main content area
with st.container():
    st.markdown('<div class="main-container">', unsafe_allow_html=True)
    display_chat_messages()
    st.markdown('</div>', unsafe_allow_html=True)

# Fixed input container at the bottom
st.markdown("""
<div class="fixed-input-container">
    <div class="input-box">
""", unsafe_allow_html=True)

with st.form(key="message_form", clear_on_submit=True):
    user_input = st.text_area("Message", height=68, placeholder="Ask anything", label_visibility="collapsed")
    
    cols = st.columns([5, 1])
    with cols[1]:
        submit_button = st.form_submit_button("Send", use_container_width=True)
    
    if submit_button and user_input.strip():
        st.session_state.messages.append({"role": "user", "content": user_input})
        st.session_state.show_welcome = False
        generate_response(user_input)

st.markdown("""
    </div>
</div>
""", unsafe_allow_html=True)
