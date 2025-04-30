from typing import Dict, Any, List, Optional
import pandas as pd
from langchain_openai import ChatOpenAI
from langchain.agents.agent_types import AgentType
from langchain_experimental.agents.agent_toolkits import create_pandas_dataframe_agent
import os
from dotenv import load_dotenv
import logging
from pydantic import SecretStr

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

load_dotenv()

class CSVAgent:
    def __init__(self):
        api_key = os.getenv("OPENAI_API_KEY")
        if not api_key:
            logger.error("OPENAI_API_KEY not found in environment variables")
            raise ValueError("OPENAI_API_KEY not found in environment variables")
        
        # Validate API key format
        if not api_key.startswith('sk-'):
            logger.error("Invalid API key format. Key should start with 'sk-'")
            raise ValueError("Invalid API key format")
            
        try:
            # Initialize with validated API key
            self.llm = ChatOpenAI(
                model="gpt-4",
                temperature=0,
                api_key=api_key.strip()  # Remove any whitespace
            )
            logger.info("ChatOpenAI initialized successfully")
            
            # Verify API key by making a test call
            try:
                self.llm.invoke("test")
                logger.info("API key verified successfully")
            except Exception as e:
                logger.error(f"API key verification failed: {str(e)}")
                raise ValueError("API key verification failed")
                
        except Exception as e:
            logger.error(f"Error initializing ChatOpenAI: {str(e)}")
            raise
            
        self.df: Optional[pd.DataFrame] = None
        self.agent = None

    def load_csv(self, file_path: str) -> bool:
        try:
            logger.info(f"Attempting to load CSV from path: {file_path}")
            if not os.path.exists(file_path):
                logger.error(f"File not found: {file_path}")
                return False
                
            # Try reading with different encodings
            encodings = ['utf-8', 'latin1', 'iso-8859-1']
            for encoding in encodings:
                try:
                    self.df = pd.read_csv(file_path, encoding=encoding)
                    logger.info(f"Successfully loaded CSV with encoding: {encoding}")
                    logger.info(f"DataFrame shape: {self.df.shape}")
                    logger.info(f"Columns: {list(self.df.columns)}")
                    self._create_agent()
                    return True
                except UnicodeDecodeError:
                    continue
                except Exception as e:
                    logger.error(f"Error reading CSV with encoding {encoding}: {str(e)}")
                    continue
                    
            logger.error("Failed to read CSV with any encoding")
            return False
            
        except Exception as e:
            logger.error(f"Error loading CSV: {str(e)}")
            return False

    def _create_agent(self):
        try:
            if self.df is None:
                logger.error("Cannot create agent: DataFrame is None")
                return None
                
            logger.info("Creating pandas dataframe agent")
            agent = create_pandas_dataframe_agent(
                llm=self.llm,
                df=self.df,
                verbose=True,
                agent_type=AgentType.OPENAI_FUNCTIONS,
                handle_parsing_errors={"max_retries": 3}
            )
            logger.info("Successfully created pandas dataframe agent")
            return agent
        except Exception as e:
            logger.error(f"Error creating agent: {str(e)}")
            raise

    def process_query(self, query: str) -> Dict[str, Any]:
        """Process a query about the CSV data"""
        try:
            if self.df is None:
                return {"success": False, "error": "No CSV file loaded"}
            
            # Log the query for debugging
            logger.info(f"Processing query: {query}")
            
            # Create the agent with the current DataFrame
            agent = self._create_agent()
            if agent is None:
                return {"success": False, "error": "Failed to create agent"}
            
            # Process the query
            result = agent.invoke({"input": query})
            
            # Log the result for debugging
            logger.info(f"Query result: {result}")
            
            # Validate if the result contains actual data from the DataFrame
            if isinstance(result, str):
                # Check if the result contains any values from the DataFrame
                has_data = any(str(value) in result for value in self.df.values.flatten())
                if not has_data:
                    return {
                        "success": True,
                        "result": "I apologize, but I cannot find this information in the provided dataset. The data available only includes information about the following devices: " + 
                                ", ".join(self.df['Model'].tolist()) + 
                                ". Would you like me to search for this information online?"
                    }
            
            return {"success": True, "result": result}
            
        except Exception as e:
            logger.error(f"Error processing query: {str(e)}")
            return {"success": False, "error": str(e)}

    def get_basic_stats(self) -> Dict[str, Any]:
        if self.df is None:
            return {"error": "No CSV file loaded"}

        try:
            stats = {
                "total_rows": len(self.df),
                "columns": list(self.df.columns),
                "data_types": self.df.dtypes.to_dict(),
                "missing_values": self.df.isnull().sum().to_dict(),
                "summary_stats": self.df.describe().to_dict() if len(self.df.select_dtypes(include=['number']).columns) > 0 else {}
            }
            
            # Add value counts for categorical columns
            categorical_cols = self.df.select_dtypes(include=['object']).columns
            for col in categorical_cols:
                stats[f"{col}_value_counts"] = self.df[col].value_counts().head(5).to_dict()
            
            return stats
        except Exception as e:
            return {
                "error": f"Error calculating statistics: {str(e)}"
            }

    def filter_by_date_range(self, column: str, start_date: str, end_date: str) -> pd.DataFrame:
        if self.df is None:
            return pd.DataFrame()

        try:
            self.df[column] = pd.to_datetime(self.df[column])
            mask = (self.df[column] >= start_date) & (self.df[column] <= end_date)
            return self.df[mask]
        except Exception as e:
            logger.error(f"Error filtering by date: {str(e)}")
            return pd.DataFrame()

    def get_column_info(self, column: str) -> Dict[str, Any]:
        if self.df is None or column not in self.df.columns:
            return {"error": "Column not found"}

        try:
            info = {
                "data_type": str(self.df[column].dtype),
                "unique_values": self.df[column].nunique(),
                "missing_values": self.df[column].isnull().sum(),
                "sample_values": self.df[column].head(5).tolist()
            }

            if pd.api.types.is_numeric_dtype(self.df[column]):
                info.update({
                    "mean": self.df[column].mean(),
                    "median": self.df[column].median(),
                    "std": self.df[column].std(),
                    "min": self.df[column].min(),
                    "max": self.df[column].max()
                })
            elif pd.api.types.is_datetime64_any_dtype(self.df[column]):
                info.update({
                    "earliest_date": self.df[column].min(),
                    "latest_date": self.df[column].max(),
                    "date_range": (self.df[column].max() - self.df[column].min()).days
                })

            return info
        except Exception as e:
            return {"error": f"Error getting column info: {str(e)}"} 
