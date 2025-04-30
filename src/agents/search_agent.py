from typing import Dict, Any, List, Optional
from langchain_openai import ChatOpenAI
from langchain.agents import AgentExecutor, create_openai_functions_agent
from langchain.tools import Tool
from langchain.prompts import ChatPromptTemplate, MessagesPlaceholder
from langchain.tools.tavily_search import TavilySearchResults
from langchain.schema import SystemMessage, HumanMessage, AIMessage
import os
from dotenv import load_dotenv
import logging
from pydantic import SecretStr

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

load_dotenv()

class SearchAgent:
    def __init__(self):
        try:
            # Get API keys
            openai_api_key = os.getenv("OPENAI_API_KEY")
            tavily_api_key = os.getenv("TAVILY_API_KEY")
            
            if not openai_api_key or not tavily_api_key:
                raise ValueError("Missing required API keys")
            
            # Initialize the language model
            self.llm = ChatOpenAI(
                model="gpt-4",
                temperature=0,
                api_key=openai_api_key.strip()
            )
            
            # Initialize the search tool
            self.search_tool = TavilySearchResults(
                api_key=tavily_api_key.strip(),
                max_results=5
            )
            
            # Create the prompt template
            prompt = ChatPromptTemplate.from_messages([
                ("system", """You are a versatile data analysis and research assistant. Your role is to:
                1. Provide accurate information from the available data
                2. When data is not available, search for relevant information online
                3. Adapt your response format based on the type of data being queried

                When responding to queries:
                - For financial data: Include current values, trends, and relevant market context
                - For product information: Include current prices, specifications, and market availability
                - For company information: Include relevant metrics, performance data, and market position
                - For trend analysis: Include current trends, historical context, and future projections
                
                Always structure your response with:
                1. Direct Answer (based on available data or search results)
                2. Supporting Details
                3. Additional Context (if relevant)
                4. Source Information (for web searches)
                
                Be clear and concise, focusing on the most relevant information for the query."""),
                MessagesPlaceholder(variable_name="chat_history"),
                ("human", "{input}"),
                MessagesPlaceholder(variable_name="agent_scratchpad"),
            ])
            
            # Create the agent
            tools = [self.search_tool]
            agent = create_openai_functions_agent(self.llm, tools, prompt)
            
            # Create the agent executor
            self.agent_executor = AgentExecutor(
                agent=agent,
                tools=tools,
                verbose=True,
                handle_parsing_errors=True
            )
            
            logger.info("Search agent initialized successfully")
            
        except Exception as e:
            logger.error(f"Error initializing search agent: {str(e)}")
            raise

    def search(self, query: str) -> Dict[str, Any]:
        """
        Perform a web search for the given query
        """
        try:
            logger.info(f"Processing search query: {query}")
            
            if not query:
                return {
                    "success": False,
                    "error": "Empty search query"
                }
            
            # Execute the search
            result = self.agent_executor.invoke(
                {
                    "input": query,
                    "chat_history": []
                }
            )
            
            if result and "output" in result:
                return {
                    "success": True,
                    "result": result["output"]
                }
            else:
                return {
                    "success": False,
                    "error": "No results found"
                }
                
        except Exception as e:
            logger.error(f"Search error: {str(e)}")
            return {
                "success": False,
                "error": str(e)
            }

    def get_company_info(self, company_name: str) -> Dict[str, Any]:
        """Get comprehensive information about a company"""
        query = f"Find detailed information about {company_name} including their business model, market position, and recent developments"
        return self.search(query)

    def get_market_trends(self, industry: str) -> Dict[str, Any]:
        """Get current market trends for a specific industry"""
        query = f"Find current market trends and analysis for the {industry} industry"
        return self.search(query)

    def get_competitor_analysis(self, company_name: str) -> Dict[str, Any]:
        """Get information about a company's competitors"""
        query = f"Find information about {company_name}'s main competitors and market position"
        return self.search(query) 
