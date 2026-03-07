"""
FinanceBot Agent - Uses tools to research stocks autonomously.
Uses Hugging Face Inference API (FREE)
"""
import os
import sys
import json
from typing import List
from dotenv import load_dotenv

# Add parent directory to Python path
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from langchain_huggingface import HuggingFaceEndpoint, ChatHuggingFace
from langchain_core.tools import Tool
from langchain_core.prompts import PromptTemplate
from langchain_classic.agents import AgentExecutor, create_react_agent
from src.tools import (
    search_stock_news,
    get_current_price,
    get_fundamentals,
    get_technical_analysis,
    analyze_text_sentiment
)

load_dotenv()


class FinanceAgent:
    """AI Agent for stock analysis with REAL ReAct reasoning"""
    
    def __init__(self):
        """Initialize the agent with tools"""
        # Define 5 tools (agent will autonomously decide which to call)
        self.tools = [
            Tool(
                name="search_news",
                func=search_stock_news,
                description="Search for recent news about a stock. Input: stock symbol (e.g., AAPL)"
            ),
            Tool(
                name="get_price",
                func=get_current_price,
                description="Get current stock price and 52-week range. Input: stock symbol (e.g., AAPL)"
            ),
            Tool(
                name="get_fundamentals",
                func=get_fundamentals,
                description="Get financial metrics (PE, EPS, debt, margins). Input: stock symbol (e.g., AAPL)"
            ),
            Tool(
                name="get_technical",
                func=get_technical_analysis,
                description="Get technical indicators (MA, RSI, trend). Input: stock symbol (e.g., AAPL)"
            ),
            Tool(
                name="analyze_sentiment",
                func=analyze_text_sentiment,
                description="Analyze sentiment of text. Input: text to analyze (max 500 chars)"
            )
        ]
        
        # Initialize Hugging Face LLM
        hf_token = os.getenv("HF_TOKEN")
        
        if not hf_token or not hf_token.startswith("hf_"):
            raise ValueError("HF_TOKEN not found or invalid in .env file")
        
        # 1. Initialize the base endpoint with a globally supported model
        base_llm = HuggingFaceEndpoint(
            repo_id="Qwen/Qwen2.5-7B-Instruct", 
            huggingfacehub_api_token=hf_token,
            temperature=0.2,
            max_new_tokens=2048,
            return_full_text=False,
            do_sample=True
        )
        
        # 2. Wrap it in ChatHuggingFace to force the supported "conversational" API task
        self.llm = ChatHuggingFace(llm=base_llm)
        # Hardcoded ReAct prompt to avoid LangSmith deprecation warnings
        template = """Answer the following questions as best you can. You have access to the following tools:

{tools}

Use the following format:

Question: the input question you must answer
Thought: you should always think about what to do
Action: the action to take, should be one of [{tool_names}]
Action Input: the input to the action
Observation: the result of the action
... (this Thought/Action/Action Input/Observation can repeat N times)
Thought: I now know the final answer
Final Answer: the final answer to the original input question

Begin!

Question: {input}
Thought:{agent_scratchpad}"""

        self.prompt = PromptTemplate.from_template(template)
        
        # Create the ReAct agent (REAL autonomous tool calling)
        self.agent = create_react_agent(
            llm=self.llm,
            tools=self.tools,
            prompt=self.prompt
        )
        
        self.agent_executor = AgentExecutor(
            agent=self.agent,
            tools=self.tools,
            verbose=True,
            max_iterations=15,
            handle_parsing_errors=True
        )
    
    def analyze_stock(self, symbol: str, analysis_type: str = "comprehensive") -> dict:
        """
        Analyze a stock autonomously.
        Agent will autonomously decide which tools to call and in what order.
        """
        if analysis_type == "comprehensive":
            prompt = f"""
Provide a comprehensive investment analysis for {symbol}:
1. Get current stock price and 52-week range
2. Fetch financial metrics (PE ratio, EPS, debt-to-equity, margins)
3. Search for recent news about {symbol}
4. Get technical indicators and trend analysis
5. Analyze sentiment from the news

Structure your response as:
## Price Information
[Current price and trend]
## Fundamentals
[Key metrics]
## Recent News & Sentiment
[What's happening with the company]
## Technical Analysis
[Chart patterns and signals]
## Investment Assessment
[Your analysis: bullish/bearish/neutral with reasons]

Be specific with numbers and cite your findings.
"""
        elif analysis_type == "quick":
            prompt = f"""
Quick investment check for {symbol}:
1. Current price and 52-week performance
2. Key financial metrics (PE, EPS)
3. Current trend (up/down)
4. Overall assessment in 1-2 sentences
"""
        else:
            prompt = f"""
Technical analysis of {symbol}:
1. Get technical indicators (moving averages, RSI)
2. Analyze the trend
3. Technical recommendation
"""
        
        try:
            # Agent will autonomously call tools in a reasoning loop
            response = self.agent_executor.invoke({"input": prompt})
            return {
                'status': 'success',
                'symbol': symbol,
                'analysis': response.get('output', ''),
                'type': analysis_type
            }
        except Exception as e:
            return {
                'status': 'error',
                'symbol': symbol,
                'error': str(e)
            }
    
    def compare_stocks(self, symbols: List[str]) -> dict:
        """Compare multiple stocks"""
        prompt = f"""
Compare these stocks: {', '.join(symbols)}
For each stock get price, fundamentals, and technical indicators.
Create a comparison table and recommend which to invest in.
"""
        try:
            response = self.agent_executor.invoke({"input": prompt})
            return {
                'status': 'success',
                'symbols': symbols,
                'comparison': response.get('output', '')
            }
        except Exception as e:
            return {
                'status': 'error',
                'symbols': symbols,
                'error': str(e)
            }


# Test
if __name__ == "__main__":
    print("Testing FinanceBot Agent with Hugging Face API...\n")
    try:
        agent = FinanceAgent()
        print("\n✅ Agent initialized successfully!")
        print("\nAnalyzing AAPL stock (quick analysis)...\n")
        result = agent.analyze_stock("AAPL", analysis_type="quick")
        print(f"Status: {result['status']}")
        if result['status'] == 'success':
            print(f"\nAnalysis:\n{result['analysis']}")
        else:
            print(f"\nError: {result.get('error', 'Unknown error')}")
    except Exception as e:
        print(f"❌ Failed: {str(e)}")
        print("\nTroubleshooting:")
        print("1. Check HF_TOKEN in .env (must start with hf_)")
        print("2. Get new token from https://huggingface.co/settings/tokens")
        print("3. Restart terminal after updating .env")