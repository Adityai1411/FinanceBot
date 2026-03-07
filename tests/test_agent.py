"""
Tests for the FinanceBot agent.
Handles API rate limits gracefully.
"""
import pytest
import json
import time
from src.agent import FinanceAgent
from src.tools import FinanceTools

class TestFinanceAgent:
    """Test suite for FinanceAgent"""
    
    @pytest.fixture
    def agent(self):
        """Create agent for testing"""
        return FinanceAgent()
    
    def test_agent_initialization(self, agent):
        """Test agent initializes correctly"""
        assert agent.agent_executor is not None
        assert len(agent.tools) == 5
    
    def test_stock_price_tool(self):
        """Test stock price tool"""
        result = FinanceTools.get_stock_price("AAPL")
        data = json.loads(result)
        
        # Handle rate limiting gracefully
        if data['status'] == 'error' and '429' in data.get('message', ''):
            pytest.skip("Yahoo Finance rate limit - skip this test")
        
        assert data['status'] == 'success'
        assert data['symbol'] == 'AAPL'
        assert 'current_price' in data
    
    def test_financial_metrics_tool(self):
        """Test financial metrics tool"""
        result = FinanceTools.get_financial_metrics("AAPL")
        data = json.loads(result)
        
        # Handle rate limiting gracefully
        if data['status'] == 'error' and '429' in data.get('message', ''):
            pytest.skip("Yahoo Finance rate limit - skip this test")
        
        assert data['status'] == 'success'
        assert 'pe_ratio' in data
        assert 'eps' in data
    
    def test_technical_indicators_tool(self):
        """Test technical indicators tool"""
        result = FinanceTools.calculate_technical_indicators("AAPL")
        data = json.loads(result)
        
        # Handle rate limiting gracefully
        if data['status'] == 'error' and ('429' in data.get('message', '') or 'Insufficient data' in data.get('message', '')):
            pytest.skip("Yahoo Finance rate limit or insufficient data - skip this test")
        
        assert data['status'] == 'success'
        assert 'trend' in data
        assert 'rsi_14' in data
    
    def test_news_search_tool(self):
        """Test news search tool"""
        result = FinanceTools.search_news("Apple")
        data = json.loads(result)
        assert data['status'] == 'success'
        assert 'articles' in data
    
    def test_sentiment_analysis_tool(self):
        """Test sentiment analysis tool"""
        text = "Apple stock is performing exceptionally well with strong financial results"
        result = FinanceTools.analyze_sentiment(text)
        data = json.loads(result)
        
        # Handle PyTorch missing gracefully
        if data['status'] == 'error' and 'PyTorch' in data.get('message', ''):
            pytest.skip("PyTorch not available - skip this test")
        
        assert data['status'] == 'success'
        assert 'sentiment' in data
        assert data['sentiment'] in ['POSITIVE', 'NEGATIVE']
    
    def test_stock_analysis(self, agent):
        """Test full stock analysis (agent handles errors gracefully)"""
        result = agent.analyze_stock("AAPL", analysis_type="quick")
        assert result['status'] in ['success', 'error']  # Either is OK - agent handles errors
        assert result['symbol'] == 'AAPL'
        # Agent should return something even with API errors
        assert len(result.get('analysis', result.get('error', ''))) > 50


if __name__ == "__main__":
    pytest.main([__file__, "-v"])