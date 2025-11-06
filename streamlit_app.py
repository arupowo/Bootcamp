"""
Streamlit Chat UI for HackerNews Article Assistant
"""
import streamlit as st
import os
from dotenv import load_dotenv
from langchain_google_genai import ChatGoogleGenerativeAI
from langchain.agents import initialize_agent, AgentType
from langchain.memory import ConversationBufferMemory
from app.utils.tools import get_all_tools

load_dotenv()

# Page configuration
st.set_page_config(
    page_title="HackerNews Article Assistant",
    page_icon="📰",
    layout="wide"
)

# Initialize session state
if "messages" not in st.session_state:
    st.session_state.messages = []
if "agent" not in st.session_state:
    st.session_state.agent = None
if "memory" not in st.session_state:
    st.session_state.memory = ConversationBufferMemory(
        memory_key="chat_history",
        return_messages=True,
        output_key="output"
    )
if "initialized" not in st.session_state:
    st.session_state.initialized = False


def initialize_llm_agent():
    """Initialize the Gemini LLM agent with tools"""
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
    
    # Create agent with memory - this will maintain conversation context
    agent = initialize_agent(
        tools=tools,
        llm=llm,
        agent=AgentType.STRUCTURED_CHAT_ZERO_SHOT_REACT_DESCRIPTION,
        memory=st.session_state.memory,
        verbose=True,
        handle_parsing_errors=True,
        agent_kwargs={
            "system_message": """You are a helpful assistant for browsing and summarizing HackerNews articles. 
            You have access to tools that can fetch articles from HackerNews API, search the database, 
            get article details, view trending articles, and get statistics.
            
            When summarizing articles, provide clear and concise information. 
            When searching, use appropriate filters to find relevant articles.
            Remember previous conversation context and refer back to it when relevant."""
        }
    )
    
    return agent


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
        st.session_state.agent = None
        st.session_state.memory = ConversationBufferMemory(
            memory_key="chat_history",
            return_messages=True,
            output_key="output"
        )
        st.session_state.messages = []
        st.session_state.initialized = False
        st.rerun()
    
    if st.button("🗑️ Clear Conversation"):
        st.session_state.memory.clear()
        st.session_state.messages = []
        st.rerun()
    
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
if st.session_state.agent is None or not st.session_state.initialized:
    with st.spinner("Initializing AI agent..."):
        st.session_state.agent = initialize_llm_agent()
        st.session_state.initialized = True

# Display chat history
for message in st.session_state.messages:
    with st.chat_message(message["role"]):
        st.markdown(message["content"])

# Chat input
if prompt := st.chat_input("Ask me about HackerNews articles..."):
    # Add user message to chat history
    st.session_state.messages.append({"role": "user", "content": prompt})
    with st.chat_message("user"):
        st.markdown(prompt)
    
    # Generate response
    with st.chat_message("assistant"):
        with st.spinner("Thinking..."):
            try:
                # Use the agent's run method which automatically uses memory
                # The memory will include previous conversation context
                response = st.session_state.agent.run(prompt)
                st.markdown(response)
                
                # Add assistant response to chat history
                st.session_state.messages.append({"role": "assistant", "content": response})
                
            except Exception as e:
                error_msg = f"Sorry, I encountered an error: {str(e)}"
                st.error(error_msg)
                st.session_state.messages.append({"role": "assistant", "content": error_msg})

# Footer
st.divider()
st.markdown("""
<div style='text-align: center; color: gray;'>
    <small>Powered by Gemini 1.5 Pro & LangChain | HackerNews API Integration</small>
</div>
""", unsafe_allow_html=True)
