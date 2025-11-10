"""
Streamlit Chat UI - Simple RAG Interface with LLM Only
"""
import streamlit as st
import os
import re
from dotenv import load_dotenv
from langchain_google_genai import ChatGoogleGenerativeAI
from langchain_core.messages import HumanMessage, AIMessage, SystemMessage
from header_search import search_headers

load_dotenv()

# Page configuration
st.set_page_config(
    page_title="RAG Chat Assistant",
    page_icon="🤖",
    layout="wide"
)

# Initialize session state
try:
    if "messages" not in st.session_state:
        st.session_state.messages = []
    if "llm" not in st.session_state:
        st.session_state.llm = None
    if "initialized" not in st.session_state:
        st.session_state.initialized = False
except (AttributeError, KeyError):
    # Running as Python script - use regular variables instead
    if not hasattr(st, '_local_state'):
        st._local_state = {
            'messages': [],
            'llm': None,
            'initialized': False
        }


def initialize_llm():
    """Initialize the LLM"""
    api_key = os.getenv("GOOGLE_API_KEY")
    if not api_key:
        st.error("⚠️ Please set GOOGLE_API_KEY in your .env file")
        st.stop()
    
    llm = ChatGoogleGenerativeAI(
        model="gemini-2.5-flash",
        google_api_key=api_key,
        temperature=0.7,
        convert_system_message_to_human=True
    )
    
    return llm


def extract_urls(text):
    """Extract URLs from text - simplified and more reliable pattern"""
    # Simpler pattern that catches most URLs including those with slashes
    url_pattern = r'https?://[^\s<>"\'\)\]]+(?:/[^\s<>"\'\)\]]*)?'
    urls = re.findall(url_pattern, text)
    
    # Clean up URLs - remove trailing punctuation
    cleaned_urls = []
    for url in urls:
        # Remove trailing punctuation
        url = url.rstrip('.,;:!?')
        if url:
            cleaned_urls.append(url)
    
    return list(set(cleaned_urls))  # Remove duplicates


def get_llm_response(llm, conversation_history, user_prompt):
    """Get response from the LLM with RAG using header search"""
    
    # Step 1: Search for relevant headers (RAG - Retrieval step)
    try:
        retrieved_headers = search_headers(user_prompt, top_k=2)
    except Exception as e:
        st.warning(f"Could not retrieve headers: {e}")
        retrieved_headers = []
    
    # Step 2: Build context from retrieved headers
    context = ""
    if retrieved_headers:
        context = "\n\n**CONTEXT FROM KNOWLEDGE BASE:**\n\n"
        for idx, result in enumerate(retrieved_headers, 1):
            context += f"Article {idx}: {result['article_title']}\n"
            context += f"Header: {result['header_text']}\n"
            context += f"URL: {result['article_url']}\n"
            context += f"Relevance Score: {result['similarity_score']:.3f}\n\n"
    
    # Step 3: Build message history with RAG context
    system_prompt = """You are a helpful AI assistant with access to a knowledge base of HackerNews articles. 
    
When provided with context from the knowledge base, use it to answer questions accurately and cite the sources.
If the context is relevant, reference the article titles and provide the URLs.
If the context is not relevant to the question, you can answer based on your general knowledge."""
    
    messages = [SystemMessage(content=system_prompt)]
    
    # Add conversation history
    for msg in conversation_history:
        if msg["role"] == "user":
            messages.append(HumanMessage(content=msg["content"]))
        elif msg["role"] == "assistant":
            messages.append(AIMessage(content=msg["content"]))
    
    # Add current user message with context
    user_message_with_context = user_prompt
    if context:
        user_message_with_context = f"{context}\n\n**USER QUESTION:**\n{user_prompt}"
    
    messages.append(HumanMessage(content=user_message_with_context))
    
    # Step 4: Get response from LLM (RAG - Generation step)
    response = llm.invoke(messages)
    
    return response.content, retrieved_headers


# Sidebar for configuration
with st.sidebar:
    st.title("⚙️ Configuration")
    
    if st.button("🔄 Reinitialize LLM"):
        try:
            st.session_state.llm = None
            st.session_state.messages = []
            st.session_state.initialized = False
        except (AttributeError, KeyError):
            if hasattr(st, '_local_state'):
                st._local_state['llm'] = None
                st._local_state['messages'] = []
                st._local_state['initialized'] = False
        try:
            st.rerun()
        except Exception:
            pass
    
    if st.button("🗑️ Clear Conversation"):
        try:
            st.session_state.messages = []
        except (AttributeError, KeyError):
            if hasattr(st, '_local_state'):
                st._local_state['messages'] = []
        try:
            st.rerun()
        except Exception:
            pass
    
    st.divider()
    
    st.markdown("### 💡 Example Queries")
    st.markdown("""
    - "Tell me about machine learning articles"
    - "What are the latest AI developments?"
    - "Show me articles about web development"
    - "What's new in blockchain technology?"
    - "Find articles about Python programming"
    """)
    
    st.divider()
    
    st.markdown("### 🧠 How RAG Works")
    st.markdown("""
    1. **Retrieval**: Searches knowledge base for relevant headers
    2. **Augmentation**: Adds context to your query
    3. **Generation**: LLM generates informed response
    """)

# Main content
st.title("🤖 RAG Chat Assistant")
st.markdown("Ask me about HackerNews articles! I use **Retrieval-Augmented Generation (RAG)** to find relevant articles and provide informed answers.")

# Initialize LLM if not already done
try:
    llm_initialized = st.session_state.get('initialized', False)
    current_llm = st.session_state.get('llm')
except (AttributeError, KeyError):
    llm_initialized = getattr(st, '_local_state', {}).get('initialized', False)
    current_llm = getattr(st, '_local_state', {}).get('llm')

if not llm_initialized or current_llm is None:
    with st.spinner("Initializing AI..."):
        try:
            current_llm = initialize_llm()
            try:
                st.session_state.llm = current_llm
                st.session_state.initialized = True
            except (AttributeError, KeyError):
                if not hasattr(st, '_local_state'):
                    st._local_state = {}
                st._local_state['llm'] = current_llm
                st._local_state['initialized'] = True
        except Exception as e:
            st.error(f"Failed to initialize LLM: {str(e)}")
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
            urls = extract_urls(message["content"])
            if urls:
                st.markdown("---")
                st.markdown("### 🔗 Embedded Links")
                for idx, url in enumerate(urls, 1):
                    try:
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
                    except Exception:
                        st.markdown(f"🔗 [Open Link: {url}]({url})")

# Chat input
try:
    prompt = st.chat_input("Ask me about HackerNews articles...")
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
                # Get LLM (should already be initialized above)
                try:
                    llm = st.session_state.llm
                except (AttributeError, KeyError):
                    llm = getattr(st, '_local_state', {}).get('llm')
                
                # If LLM is still None, initialize it
                if llm is None:
                    llm = initialize_llm()
                    try:
                        st.session_state.llm = llm
                    except (AttributeError, KeyError):
                        if not hasattr(st, '_local_state'):
                            st._local_state = {}
                        st._local_state['llm'] = llm
                
                if llm is None:
                    raise Exception("Failed to initialize LLM. Please check your GOOGLE_API_KEY.")
                
                # Get response using LLM with RAG
                # Note: messages already includes the current user prompt
                conversation_history = messages[:-1]  # All messages except the last one (current prompt)
                
                # Show a status for retrieval
                with st.status("🔍 Retrieving relevant context...", expanded=False) as status:
                    response_text, retrieved_headers = get_llm_response(llm, conversation_history, prompt)
                    
                    # Display retrieved headers
                    if retrieved_headers:
                        st.success(f"Found {len(retrieved_headers)} relevant headers")
                        for idx, header in enumerate(retrieved_headers, 1):
                            st.write(f"**{idx}. {header['header_text']}**")
                            st.caption(f"From: {header['article_title']} (Score: {header['similarity_score']:.3f})")
                    else:
                        st.info("No relevant context found in knowledge base")
                    
                    status.update(label="✅ Context retrieved!", state="complete")
                
                # Display the LLM response
                st.markdown(response_text)
                
                # Extract and display embedded URLs immediately after response
                urls = extract_urls(response_text)
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