import streamlit as st
import pandas as pd
from agents.csv_agent import CSVAgent
from agents.search_agent import SearchAgent
import os
from dotenv import load_dotenv
import logging
import tempfile

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Load environment variables
load_dotenv()

# Initialize session state for chat history
if 'messages' not in st.session_state:
    st.session_state.messages = []

# Initialize agents
@st.cache_resource
def get_agents():
    try:
        csv_agent = CSVAgent()
        search_agent = SearchAgent()
        return csv_agent, search_agent
    except Exception as e:
        logger.error(f"Error initializing agents: {str(e)}")
        st.error(f"Error initializing agents: {str(e)}")
        return None, None

def display_chat_message(role, content):
    """Display a chat message with appropriate styling"""
    with st.chat_message(role):
        st.write(content)

def main():
    st.set_page_config(
        page_title="CSV Analysis Agent",
        page_icon="📊",
        layout="wide"
    )
    
    st.title("📊 CSV Analysis Agent")
    st.markdown("""
    This application helps you analyze CSV files using AI. Upload your CSV file and ask questions about the data.
    If the information is not found in the CSV, the agent can search the internet for additional context.
    """)
    
    # Initialize agents
    csv_agent, search_agent = get_agents()
    if not csv_agent or not search_agent:
        st.error("Failed to initialize agents. Please check your environment variables and try again.")
        return
    
    # File uploader
    uploaded_file = st.file_uploader("Upload your CSV file", type=['csv'])
    
    if uploaded_file is not None:
        try:
            # Save the uploaded file temporarily
            with tempfile.NamedTemporaryFile(delete=False, suffix='.csv') as tmp_file:
                tmp_file.write(uploaded_file.getvalue())
                tmp_path = tmp_file.name

            # Load the CSV into the agent
            if csv_agent.load_csv(tmp_path):
                # Read and display the CSV data
                df = pd.read_csv(tmp_path)
                st.subheader("Data Preview")
                st.dataframe(df.head())
                
                # Display data statistics
                st.subheader("Data Statistics")
                col1, col2, col3 = st.columns(3)
                with col1:
                    st.metric("Total Rows", len(df))
                with col2:
                    st.metric("Total Columns", len(df.columns))
                with col3:
                    st.metric("Missing Values", df.isnull().sum().sum())
                
                # Display chat history
                for message in st.session_state.messages:
                    display_chat_message(message["role"], message["content"])
                
                # Chat input
                if prompt := st.chat_input("Ask a question about your data"):
                    # Add user message to chat history
                    st.session_state.messages.append({"role": "user", "content": prompt})
                    display_chat_message("user", prompt)
                    
                    with st.spinner("Analyzing your data..."):
                        try:
                            # First try to get answer from CSV data
                            response = csv_agent.process_query(prompt)
                            
                            if response["success"]:
                                csv_response = response["result"]
                                result_lower = str(csv_response).lower()
                                
                                # Check if the answer indicates missing data
                                missing_data_indicators = [
                                    "no data found",
                                    "does not contain",
                                    "not found",
                                    "not available",
                                    "not listed",
                                    "cannot find",
                                    "sorry",
                                    "not in the dataset",
                                    "not present",
                                    "only",
                                    "please provide",
                                    "adjust your query",
                                    "dataset provided does not"
                                ]
                                
                                # Simplified check for missing data
                                should_search = any(indicator in result_lower for indicator in missing_data_indicators)
                                
                                if should_search:
                                    # Automatically perform web search
                                    with st.spinner("Data not found in CSV. Searching online..."):
                                        try:
                                            # Clean up the query
                                            search_terms = prompt.lower()
                                            search_terms = search_terms.replace("what is", "")
                                            search_terms = search_terms.replace("the price of", "")
                                            search_terms = search_terms.replace("cost of", "")
                                            search_terms = search_terms.replace("if data not available search it", "")
                                            search_terms = search_terms.strip()
                                            
                                            # Format search query based on the type of information requested
                                            if any(word in search_terms for word in ["price", "cost", "value", "worth"]):
                                                search_query = f"What is the current market price and value for {search_terms}? Include any relevant market context or trends."
                                            elif any(word in search_terms for word in ["spec", "feature", "detail", "information"]):
                                                search_query = f"What are the specifications and features of {search_terms}? Include technical details and capabilities."
                                            elif any(word in search_terms for word in ["company", "business", "organization"]):
                                                search_query = f"What is the current status and information about {search_terms}? Include recent developments and market position."
                                            else:
                                                search_query = f"What is the current information about {search_terms}? Include relevant details, specifications, and market context."
                                            
                                            search_result = search_agent.search(search_query)
                                            if search_result and search_result.get("success"):
                                                combined_response = f"{csv_response}\n\n🌐 Web Search Results:\n\n{search_result['result']}\n\nNote: Prices may vary by region and retailer."
                                                st.session_state.messages.append({"role": "assistant", "content": combined_response})
                                                display_chat_message("assistant", combined_response)
                                            else:
                                                st.session_state.messages.append({"role": "assistant", "content": csv_response})
                                                display_chat_message("assistant", csv_response)
                                        except Exception as e:
                                            logger.error(f"Search error: {str(e)}")
                                            st.session_state.messages.append({"role": "assistant", "content": csv_response})
                                            display_chat_message("assistant", csv_response)
                                else:
                                    st.session_state.messages.append({"role": "assistant", "content": csv_response})
                                    display_chat_message("assistant", csv_response)
                                
                        except Exception as e:
                            logger.error(f"Error processing question: {str(e)}")
                            error_message = f"Error processing your question: {str(e)}"
                            st.session_state.messages.append({"role": "assistant", "content": error_message})
                            display_chat_message("assistant", error_message)

            # Clean up the temporary file
            os.unlink(tmp_path)
                        
        except Exception as e:
            logger.error(f"Error reading CSV file: {str(e)}")
            st.error(f"Error reading CSV file: {str(e)}")
    
    # Add sidebar with information
    with st.sidebar:
        st.header("About")
        st.markdown("""
        This application uses:
        - OpenAI's GPT-4 for natural language understanding
        - Pandas for data manipulation
        - Tavily for web searches
        - Streamlit for the user interface
        
        The agent can:
        1. Analyze CSV data
        2. Answer questions about the data
        3. Search for additional context when needed
        4. Provide market insights and company information
        """)
        
        st.header("Tips")
        st.markdown("""
        - Upload a CSV file to get started
        - Ask specific questions about your data
        - If information isn't in the CSV, the agent will offer to search the web
        - The search results focus on business context and market information
        """)
        
        # Add a button to clear chat history
        if st.button("Clear Chat History"):
            st.session_state.messages = []
            st.rerun()

if __name__ == "__main__":
    main() 
