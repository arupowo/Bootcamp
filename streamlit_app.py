"""
Streamlit Chat UI for HackerNews Article Assistant
"""
import streamlit as st
import os
import re
from dotenv import load_dotenv
from langchain_google_genai import ChatGoogleGenerativeAI
from langchain.agents import create_agent
from langchain_core.messages import HumanMessage, AIMessage
from app.utils.tools import get_all_tools

load_dotenv()

# Page configuration
st.set_page_config(
    page_title="HackerNews Article Assistant",
    page_icon="📰",
    layout="wide"
)

# Initialize session state
try:
    if "messages" not in st.session_state:
        st.session_state.messages = []
    if "agent" not in st.session_state:
        st.session_state.agent = None
    if "initialized" not in st.session_state:
        st.session_state.initialized = False
except (AttributeError, KeyError):
    # Running as Python script - use regular variables instead
    if not hasattr(st, '_local_state'):
        st._local_state = {
            'messages': [],
            'agent': None,
            'initialized': False
        }


def initialize_agent():
    """Initialize the LangChain agent with tools"""
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
    
    tools = get_all_tools()
    
    # Create agent with tools
    agent = create_agent(
        llm,
        tools=tools,
        system_prompt="""You are a helpful assistant for browsing and summarizing HackerNews articles. 
        You have access to tools that can fetch articles from HackerNews API, search the database, 
        get article details, view trending articles, and get statistics.
        
        IMPORTANT: When users ask for article links or URLs, you MUST use the search_articles or 
        get_trending_articles_from_db tools first to find articles, then use get_article_details 
        with the article ID to retrieve the full URL. Always include URLs in your responses when 
        discussing articles.
        
        When summarizing articles, provide clear and concise information including URLs. 
        When searching, use appropriate filters to find relevant articles.
        Remember previous conversation context and refer back to it when relevant."""
    )
    
    return agent


def extract_urls(text):
    """Extract URLs from text - improved pattern"""
    if not text:
        return []
    
    urls = []
    
    # Pattern 1: Standard URLs (http:// or https://)
    url_pattern1 = r'https?://[^\s<>"{}|\\^`\[\]()]+[^\s<>"{}|\\^`\[\]().,;:!?]'
    urls.extend(re.findall(url_pattern1, text))
    
    # Pattern 2: URLs in parentheses
    url_pattern2 = r'\(https?://[^\)]+\)'
    matches2 = re.findall(url_pattern2, text)
    for match in matches2:
        clean_url = re.search(r'https?://[^\)]+', match)
        if clean_url:
            urls.append(clean_url.group())
    
    # Pattern 3: URLs in brackets
    url_pattern3 = r'\[https?://[^\]]+\]'
    matches3 = re.findall(url_pattern3, text)
    for match in matches3:
        clean_url = re.search(r'https?://[^\]]+', match)
        if clean_url:
            urls.append(clean_url.group())
    
    # Pattern 4: URLs at end of line or followed by punctuation
    url_pattern4 = r'https?://[^\s]+'
    urls.extend(re.findall(url_pattern4, text))
    
    # Clean and deduplicate
    cleaned_urls = []
    for url in urls:
        # Remove trailing punctuation that might have been captured
        url = url.rstrip('.,;:!?)')
        if url.startswith('http://') or url.startswith('https://'):
            cleaned_urls.append(url)
    
    return list(set(cleaned_urls))  # Remove duplicates


def get_agent_response(agent, conversation_history, user_prompt):
    # Build message history for the agent
    langchain_messages = []
    # Add conversation history
    for msg in conversation_history:
        if msg["role"] == "user":
            langchain_messages.append(HumanMessage(content=msg["content"]))
        elif msg["role"] == "assistant":
            langchain_messages.append(AIMessage(content=msg["content"]))
    
    # Add current user message
    langchain_messages.append(HumanMessage(content=user_prompt))
    
    # Invoke agent with messages
    result = agent.invoke({"messages": langchain_messages})
    
    # Extract response text from agent result - handle nested structures
    response_text = ""
    if isinstance(result, dict):
        messages_list = result.get("messages", [])
        if messages_list:
            last_message = messages_list[-1]
            # Handle different message types
            if hasattr(last_message, 'content'):
                content = last_message.content
                # Handle nested dict structure
                if isinstance(content, dict):
                    response_text = content.get('text', str(content))
                elif isinstance(content, list):
                    # Handle list of content blocks
                    text_parts = []
                    for block in content:
                        if isinstance(block, dict):
                            text_parts.append(block.get('text', str(block)))
                        else:
                            text_parts.append(str(block))
                    response_text = '\n'.join(text_parts)
                else:
                    response_text = str(content)
            else:
                response_text = str(last_message)
        else:
            response_text = result.get("output", str(result))
    else:
        response_text = str(result)
    
    return response_text


# Sidebar for configuration
with st.sidebar:
    st.title("⚙️ Configuration")
    
    api_base_url = st.text_input(
        "API Base URL",
        value=os.getenv("API_BASE_URL", "http://localhost:5000/api"),
        help="Base URL for the Flask API"
    )
    os.environ["API_BASE_URL"] = api_base_url
    
    if st.button("🔄 Reinitialize Agent"):
        try:
            st.session_state.agent = None
            st.session_state.messages = []
            st.session_state.initialized = False
        except (AttributeError, KeyError):
            if hasattr(st, '_local_state'):
                st._local_state['agent'] = None
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
    
    st.markdown("### 📚 Available Tools")
    st.markdown("""
    - **Fetch Articles**: Get articles from HackerNews
    - **Search Articles**: Search database with filters
    - **Get Article Details**: View specific article
    - **Get Trending**: View trending articles
    - **Get Statistics**: View database stats
    """)
    
    st.divider()
    
    st.markdown("### 💡 Example Queries")
    st.markdown("""
    - "Fetch the top 10 articles from HackerNews"
    - "Search for articles about Python"
    - "Show me trending articles"
    - "What are the statistics?"
    - "Find articles with score above 100"
    - "Get article with ID 1"
    """)

# Main content
st.title("📰 HackerNews Article Assistant")
st.markdown("Ask me anything about HackerNews articles! I can fetch, search, and summarize articles for you.")

# Initialize agent if not already done
try:
    agent_initialized = st.session_state.get('initialized', False)
    current_agent = st.session_state.get('agent')
except (AttributeError, KeyError):
    agent_initialized = getattr(st, '_local_state', {}).get('initialized', False)
    current_agent = getattr(st, '_local_state', {}).get('agent')

if not agent_initialized or current_agent is None:
    with st.spinner("Initializing AI agent..."):
        try:
            current_agent = initialize_agent()
            try:
                st.session_state.agent = current_agent
                st.session_state.initialized = True
            except (AttributeError, KeyError):
                if not hasattr(st, '_local_state'):
                    st._local_state = {}
                st._local_state['agent'] = current_agent
                st._local_state['initialized'] = True
        except Exception as e:
            st.error(f"Failed to initialize agent: {str(e)}")
            st.stop()

# Display chat history
try:
    messages = st.session_state.messages
except (AttributeError, KeyError):
    messages = getattr(st, '_local_state', {}).get('messages', [])

for message in messages:
    with st.chat_message(message["role"]):
        st.markdown(message["content"])

# Display embedded URLs from the last assistant message (just above chat input)
if messages:
    last_message = messages[-1]
    if last_message.get("role") == "assistant":
        urls = extract_urls(last_message.get("content", ""))
        if urls:
            st.markdown("---")
            st.markdown("### 🔗 Embedded Links")
            for url in urls:
                try:
                    # Create a nice embedded iframe with modern UI
                    st.markdown(f"""
                    <div style="margin-bottom: 15px; border: 1px solid #e0e0e0; border-radius: 8px; overflow: hidden; box-shadow: 0 2px 4px rgba(0,0,0,0.1);">
                        <div style="background: linear-gradient(135deg, #667eea 0%, #764ba2 100%); padding: 10px 15px; border-bottom: 1px solid #e0e0e0;">
                            <a href="{url}" target="_blank" style="text-decoration: none; color: white; font-weight: 600; font-size: 14px;">
                                🔗 Open in new tab: {url[:60]}{'...' if len(url) > 60 else ''}
                            </a>
                        </div>
                        <iframe 
                            src="{url}" 
                            width="100%" 
                            height="450" 
                            frameborder="0" 
                            style="border-radius: 0 0 8px 8px; display: block;"
                            sandbox="allow-same-origin allow-scripts allow-popups allow-forms allow-top-navigation"
                            loading="lazy"
                            onerror="this.style.display='none';">
                        </iframe>
                    </div>
                    """, unsafe_allow_html=True)
                except Exception as e:
                    # Fallback to simple link if embedding fails
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
                # Get agent (should already be initialized above)
                try:
                    agent = st.session_state.agent
                except (AttributeError, KeyError):
                    agent = getattr(st, '_local_state', {}).get('agent')
                
                # If agent is still None, initialize it
                if agent is None:
                    agent = initialize_agent()
                    try:
                        st.session_state.agent = agent
                    except (AttributeError, KeyError):
                        if not hasattr(st, '_local_state'):
                            st._local_state = {}
                        st._local_state['agent'] = agent
                
                if agent is None:
                    raise Exception("Failed to initialize agent. Please check your GOOGLE_API_KEY.")
                
                # Get response using LangChain agent
                # Note: messages already includes the current user prompt
                conversation_history = messages[:-1]  # All messages except the last one (current prompt)
                response_text = get_agent_response(agent, conversation_history, prompt)
                
                st.markdown(response_text)
                
                # Extract and display URLs immediately after response
                urls = extract_urls(response_text)
                if urls:
                    st.markdown("---")
                    st.markdown("### 🔗 Embedded Links")
                    for url in urls:
                        try:
                            # Create a nice embedded iframe with modern UI
                            st.markdown(f"""
                            <div style="margin-bottom: 15px; border: 1px solid #e0e0e0; border-radius: 8px; overflow: hidden; box-shadow: 0 2px 4px rgba(0,0,0,0.1);">
                                <div style="background: linear-gradient(135deg, #667eea 0%, #764ba2 100%); padding: 10px 15px; border-bottom: 1px solid #e0e0e0;">
                                    <a href="{url}" target="_blank" style="text-decoration: none; color: white; font-weight: 600; font-size: 14px;">
                                        🔗 Open in new tab: {url[:60]}{'...' if len(url) > 60 else ''}
                                    </a>
                                </div>
                                <iframe 
                                    src="{url}" 
                                    width="100%" 
                                    height="450" 
                                    frameborder="0" 
                                    style="border-radius: 0 0 8px 8px; display: block;"
                                    sandbox="allow-same-origin allow-scripts allow-popups allow-forms allow-top-navigation"
                                    loading="lazy"
                                    onerror="this.style.display='none';">
                                </iframe>
                            </div>
                            """, unsafe_allow_html=True)
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