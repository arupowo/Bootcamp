# Streamlit Chat UI - Simple RAG Interface with LLM Only
import streamlit as st
import os
from dotenv import load_dotenv
from app.services.rag_service import RAGService
from app.services.ui_helper import UIHelper

load_dotenv()

# Page configuration
st.set_page_config(
    page_title="RAG Chat Assistant",
    page_icon="🤖",
    layout="wide"
)

# Custom CSS for red-tinted modern UI
st.markdown("""
<style>
    /* Main app background with subtle gradient */
    .stApp {
        background: linear-gradient(135deg, #1a0000 0%, #2d0a0a 100%);
    }
    
    /* Sidebar styling */
    [data-testid="stSidebar"] {
        background: linear-gradient(180deg, #2d0a0a 0%, #1a0000 100%);
        border-right: 2px solid #ff6b6b;
    }
    
    /* Main content area */
    .main .block-container {
        padding-top: 2rem;
        background: rgba(0, 0, 0, 0.3);
        border-radius: 15px;
        border: 1px solid rgba(255, 107, 107, 0.2);
    }
    
    /* Headers */
    h1, h2, h3 {
        color: #ff6b6b !important;
        text-shadow: 0 0 10px rgba(255, 107, 107, 0.3);
        font-weight: 700 !important;
    }
    
    /* Chat messages */
    [data-testid="stChatMessage"] {
        background: rgba(255, 107, 107, 0.05) !important;
        border: 1px solid rgba(255, 107, 107, 0.2) !important;
        border-radius: 10px !important;
        margin: 10px 0 !important;
    }
    
    /* Buttons */
    .stButton button {
        background: linear-gradient(135deg, #ff6b6b 0%, #ee5a6f 100%) !important;
        color: white !important;
        border: none !important;
        border-radius: 8px !important;
        padding: 0.5rem 1rem !important;
        font-weight: 600 !important;
        box-shadow: 0 4px 15px rgba(255, 107, 107, 0.4) !important;
        transition: all 0.3s ease !important;
    }
    
    .stButton button:hover {
        background: linear-gradient(135deg, #ee5a6f 0%, #ff6b6b 100%) !important;
        box-shadow: 0 6px 20px rgba(255, 107, 107, 0.6) !important;
        transform: translateY(-2px) !important;
    }
    
    /* Expanders */
    [data-testid="stExpander"] {
        background: rgba(255, 107, 107, 0.08) !important;
        border: 1px solid rgba(255, 107, 107, 0.3) !important;
        border-radius: 8px !important;
        margin: 8px 0 !important;
    }
    
    /* Info boxes */
    .stAlert {
        background: rgba(255, 107, 107, 0.1) !important;
        border-left: 4px solid #ff6b6b !important;
        border-radius: 5px !important;
    }
    
    /* Success boxes */
    [data-testid="stSuccess"] {
        background: rgba(255, 107, 107, 0.15) !important;
        border-left: 4px solid #ff6b6b !important;
    }
    
    /* Text input */
    [data-testid="stChatInput"] {
        background: rgba(255, 107, 107, 0.05) !important;
        border: 2px solid rgba(255, 107, 107, 0.3) !important;
        border-radius: 10px !important;
    }
    
    /* Dividers */
    hr {
        border-color: rgba(255, 107, 107, 0.3) !important;
    }
    
    /* Markdown text */
    .stMarkdown {
        color: #f0f0f0 !important;
    }
    
    /* Code blocks */
    code {
        background: rgba(255, 107, 107, 0.1) !important;
        color: #ff6b6b !important;
        padding: 2px 6px !important;
        border-radius: 4px !important;
    }
    
    /* Scrollbar */
    ::-webkit-scrollbar {
        width: 10px;
        height: 10px;
    }
    
    ::-webkit-scrollbar-track {
        background: rgba(0, 0, 0, 0.3);
    }
    
    ::-webkit-scrollbar-thumb {
        background: linear-gradient(135deg, #ff6b6b 0%, #ee5a6f 100%);
        border-radius: 5px;
    }
    
    ::-webkit-scrollbar-thumb:hover {
        background: #ee5a6f;
    }
</style>
""", unsafe_allow_html=True)

# Initialize session state
try:
    if "messages" not in st.session_state:
        st.session_state.messages = []
    if "rag_service" not in st.session_state:
        st.session_state.rag_service = None
    if "initialized" not in st.session_state:
        st.session_state.initialized = False
    if "current_retrieved_headers" not in st.session_state:
        st.session_state.current_retrieved_headers = []
    if "suggested_questions" not in st.session_state:
        st.session_state.suggested_questions = []
except (AttributeError, KeyError):
    # Running as Python script - use regular variables instead
    if not hasattr(st, '_local_state'):
        st._local_state = {
            'messages': [],
            'rag_service': None,
            'initialized': False,
            'current_retrieved_headers': [],
            'suggested_questions': []
        }


def initialize_rag_service():
    # Initialize the RAG Service
    api_key = os.getenv("GOOGLE_API_KEY")
    if not api_key:
        st.error("⚠️ Please set GOOGLE_API_KEY in your .env file")
        st.stop()
    
    try:
        rag_service = RAGService(
            api_key=api_key,
            model="gemini-2.5-flash",
            temperature=0.7
        )
        return rag_service
    except Exception as e:
        st.error(f"Failed to initialize RAG service: {e}")
        st.stop()


# Sidebar for configuration
with st.sidebar:
    # Clear Chat button at the TOP
    if st.button("🗑️ Clear Chat", use_container_width=True):
        try:
            st.session_state.rag_service = None
            st.session_state.messages = []
            st.session_state.initialized = False
            st.session_state.current_retrieved_headers = []
            st.session_state.suggested_questions = []
        except (AttributeError, KeyError):
            if hasattr(st, '_local_state'):
                st._local_state['rag_service'] = None
                st._local_state['messages'] = []
                st._local_state['initialized'] = False
                st._local_state['current_retrieved_headers'] = []
                st._local_state['suggested_questions'] = []
        try:
            st.rerun()
        except Exception:
            pass
    
    st.divider()
    
    # Display retrieved context
    st.markdown("### 📚 Retrieved Context (Top 4)")
    
    try:
        current_headers = st.session_state.current_retrieved_headers
    except (AttributeError, KeyError):
        current_headers = getattr(st, '_local_state', {}).get('current_retrieved_headers', [])
    
    if current_headers:
        st.success(f"Showing {len(current_headers)}/4 relevant articles")
        for idx, header in enumerate(current_headers, 1):
            # Use article title as the expander name (truncate if too long)
            display_title = UIHelper.truncate_text(header['article_title'], max_length=50)
            
            # Show expander with article title
            with st.expander(f"📄 {display_title} ({header['similarity_score']:.3f})", expanded=False):
                st.markdown(f"**Full Title:** {header['article_title']}")
                st.markdown(f"**Header:** {header['header_text'][:100]}...")
                
                # Embed the URL
                url = header['article_url']
                if url:
                    st.markdown(f"[🔗 Open Article]({url})")
                    try:
                        st.markdown(f"""
                        <div style="margin-top: 10px; border: 2px solid rgba(255, 107, 107, 0.4); border-radius: 8px; overflow: hidden; box-shadow: 0 4px 15px rgba(255, 107, 107, 0.2);">
                            <iframe 
                                src="{url}" 
                                width="100%" 
                                height="300" 
                                frameborder="0" 
                                style="display: block;"
                                sandbox="allow-same-origin allow-scripts allow-popups allow-forms"
                                loading="lazy">
                            </iframe>
                        </div>
                        """, unsafe_allow_html=True)
                    except Exception:
                        st.caption("⚠️ Could not embed preview")
    else:
        st.info("💭 No context retrieved yet.\n\nAsk a question to see relevant articles!")

# Main content
st.title("🤖 RAG Chat Assistant")
st.markdown("Ask me about HackerNews articles! I use **Retrieval-Augmented Generation (RAG)** to find relevant articles and provide informed answers.")

# Initialize RAG Service if not already done
try:
    service_initialized = st.session_state.get('initialized', False)
    current_rag_service = st.session_state.get('rag_service')
except (AttributeError, KeyError):
    service_initialized = getattr(st, '_local_state', {}).get('initialized', False)
    current_rag_service = getattr(st, '_local_state', {}).get('rag_service')

if not service_initialized or current_rag_service is None:
    with st.spinner("Initializing RAG Service..."):
        try:
            current_rag_service = initialize_rag_service()
            try:
                st.session_state.rag_service = current_rag_service
                st.session_state.initialized = True
            except (AttributeError, KeyError):
                if not hasattr(st, '_local_state'):
                    st._local_state = {}
                st._local_state['rag_service'] = current_rag_service
                st._local_state['initialized'] = True
        except Exception as e:
            st.error(f"Failed to initialize RAG Service: {str(e)}")
            st.stop()

# Display chat history
try:
    messages = st.session_state.messages
except (AttributeError, KeyError):
    messages = getattr(st, '_local_state', {}).get('messages', [])

for message in messages:
    with st.chat_message(message["role"]):
        st.markdown(message["content"])
        
        # If this is an assistant message with URLs, show embeds
        if message["role"] == "assistant":
            urls = UIHelper.extract_urls(message["content"])
            if urls:
                st.markdown("---")
                st.markdown("### 🔗 Embedded Links")
                for idx, url in enumerate(urls, 1):
                    try:
                        st.markdown(f"""
                        <div style="margin-bottom: 15px; border: 2px solid rgba(255, 107, 107, 0.4); border-radius: 12px; overflow: hidden; box-shadow: 0 6px 20px rgba(255, 107, 107, 0.3);">
                            <div style="background: linear-gradient(135deg, #ff6b6b 0%, #ee5a6f 100%); padding: 12px 20px; border-bottom: 2px solid rgba(255, 107, 107, 0.5);">
                                <a href="{url}" target="_blank" style="text-decoration: none; color: white; font-weight: 700; font-size: 15px; text-shadow: 0 2px 4px rgba(0,0,0,0.2);">
                                    🔗 Article {idx}: Open in new tab
                                </a>
                            </div>
                            <iframe 
                                src="{url}" 
                                width="100%" 
                                height="500" 
                                frameborder="0" 
                                style="border-radius: 0 0 12px 12px; display: block; background: rgba(0,0,0,0.2);"
                                sandbox="allow-same-origin allow-scripts allow-popups allow-forms allow-top-navigation"
                                loading="lazy">
                            </iframe>
                        </div>
                        """, unsafe_allow_html=True)
                        st.caption(f"📄 {url}")
                    except Exception:
                        st.markdown(f"🔗 [Open Link: {url}]({url})")

# Display suggested questions above chat input
try:
    suggested_questions = st.session_state.suggested_questions
except (AttributeError, KeyError):
    suggested_questions = getattr(st, '_local_state', {}).get('suggested_questions', [])

if suggested_questions:
    st.markdown("### 💡 Suggested Questions")
    cols = st.columns(3)
    for idx, question in enumerate(suggested_questions):
        with cols[idx]:
            if st.button(question, key=f"suggested_{idx}", use_container_width=True):
                # Set the prompt to the suggested question
                try:
                    st.session_state.selected_suggestion = question
                except (AttributeError, KeyError):
                    if not hasattr(st, '_local_state'):
                        st._local_state = {}
                    st._local_state['selected_suggestion'] = question
                st.rerun()

# Chat input
try:
    # Check if a suggestion was selected
    selected_suggestion = None
    try:
        selected_suggestion = st.session_state.get('selected_suggestion')
        if selected_suggestion:
            st.session_state.selected_suggestion = None  # Clear it after use
    except (AttributeError, KeyError):
        selected_suggestion = getattr(st, '_local_state', {}).get('selected_suggestion')
        if selected_suggestion and hasattr(st, '_local_state'):
            st._local_state['selected_suggestion'] = None
    
    prompt = selected_suggestion if selected_suggestion else st.chat_input("Ask me about HackerNews articles...")
except Exception:
    # Running as Python script - skip chat input
    prompt = None

if prompt:
    # Get messages list
    try:
        messages = st.session_state.messages
    except (AttributeError, KeyError):
        if not hasattr(st, '_local_state'):
            st._local_state = {'messages': []}
        messages = st._local_state['messages']
    
    # Add user message to chat history
    messages.append({"role": "user", "content": prompt})
    
    # Update session state or local state
    try:
        st.session_state.messages = messages
    except (AttributeError, KeyError):
        st._local_state['messages'] = messages
    
    with st.chat_message("user"):
        st.markdown(prompt)
    
    # Generate response
    with st.chat_message("assistant"):
        with st.spinner("Thinking..."):
            try:
                # Get RAG Service (should already be initialized above)
                try:
                    rag_service = st.session_state.rag_service
                except (AttributeError, KeyError):
                    rag_service = getattr(st, '_local_state', {}).get('rag_service')
                
                # If RAG service is still None, initialize it
                if rag_service is None:
                    rag_service = initialize_rag_service()
                    try:
                        st.session_state.rag_service = rag_service
                    except (AttributeError, KeyError):
                        if not hasattr(st, '_local_state'):
                            st._local_state = {}
                        st._local_state['rag_service'] = rag_service
                
                if rag_service is None:
                    raise Exception("Failed to initialize RAG Service. Please check your GOOGLE_API_KEY.")
                
                # Get response using RAG Service
                # Note: messages already includes the current user prompt
                conversation_history = messages[:-1]  # All messages except the last one (current prompt)
                response_text, retrieved_headers = rag_service.process_query(prompt, conversation_history)
                
                # Update session state with retrieved headers for sidebar display
                try:
                    st.session_state.current_retrieved_headers = retrieved_headers
                except (AttributeError, KeyError):
                    if hasattr(st, '_local_state'):
                        st._local_state['current_retrieved_headers'] = retrieved_headers
                
                # Generate suggested questions based on retrieved headers
                suggested = UIHelper.generate_suggested_questions(retrieved_headers)
                try:
                    st.session_state.suggested_questions = suggested
                except (AttributeError, KeyError):
                    if hasattr(st, '_local_state'):
                        st._local_state['suggested_questions'] = suggested
                
                # Display the LLM response
                st.markdown(response_text)
                
                # Show retrieved context summary
                if retrieved_headers:
                    with st.expander("🔍 View Retrieved Context", expanded=False):
                        st.success(f"Found {len(retrieved_headers)} relevant headers")
                        for idx, header in enumerate(retrieved_headers, 1):
                            st.write(f"**{idx}. {header['header_text'][:80]}...**")
                            st.caption(f"From: {header['article_title']} (Score: {header['similarity_score']:.3f})")
                else:
                    st.info("No relevant context found in knowledge base")
                
                # Extract and display embedded URLs immediately after response
                urls = UIHelper.extract_urls(response_text)
                if urls:
                    st.markdown("---")
                    st.markdown("### 🔗 Embedded Links")
                    st.info(f"Found {len(urls)} article link(s)")
                    
                    for idx, url in enumerate(urls, 1):
                        try:
                            # Create a nice embedded iframe with modern UI
                            st.markdown(f"""
                            <div style="margin-bottom: 15px; border: 1px solid #e0e0e0; border-radius: 8px; overflow: hidden; box-shadow: 0 2px 4px rgba(0,0,0,0.1);">
                                <div style="background: linear-gradient(135deg, #667eea 0%, #764ba2 100%); padding: 10px 15px; border-bottom: 1px solid #e0e0e0;">
                                    <a href="{url}" target="_blank" style="text-decoration: none; color: white; font-weight: 600; font-size: 14px;">
                                        🔗 Article {idx}: Open in new tab
                                    </a>
                                </div>
                                <iframe 
                                    src="{url}" 
                                    width="100%" 
                                    height="500" 
                                    frameborder="0" 
                                    style="border-radius: 0 0 8px 8px; display: block;"
                                    sandbox="allow-same-origin allow-scripts allow-popups allow-forms allow-top-navigation"
                                    loading="lazy">
                                </iframe>
                            </div>
                            """, unsafe_allow_html=True)
                            st.caption(f"📄 {url}")
                        except Exception as e:
                            # Fallback to simple link if embedding fails
                            st.markdown(f"🔗 [Open Link: {url}]({url})")
                
                # Add assistant response to chat history
                messages.append({"role": "assistant", "content": response_text})
                
                # Update session state or local state
                try:
                    st.session_state.messages = messages
                except (AttributeError, KeyError):
                    st._local_state['messages'] = messages
                
                # Trigger rerun to update sidebar immediately
                st.rerun()
                
            except Exception as e:
                error_msg = f"Sorry, I encountered an error: {str(e)}"
                st.error(error_msg)
                messages.append({"role": "assistant", "content": error_msg})
                try:
                    st.session_state.messages = messages
                except (AttributeError, KeyError):
                    st._local_state['messages'] = messages

# Footer
st.divider()
st.markdown("""
<div style='text-align: center; color: gray;'>
    <small>Arup | Jeavio Bootcamp e</small>
</div>
""", unsafe_allow_html=True)