"""
Finance tools for the agent to use.
Each tool is a self-contained function that returns JSON.
"""
import os
import sys
import json
import yfinance as yf
import requests
from datetime import datetime, timedelta
import numpy as np
import pandas as pd
from dotenv import load_dotenv

# Add parent directory to Python path
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

load_dotenv()

NEWS_API_KEY = os.getenv("NEWS_API_KEY")


class FinanceTools:
    """Collection of tools for financial analysis"""
    
    @staticmethod
    def search_news(query: str, days: int = 7) -> str:
        """
        Search for recent news about a stock.
        Returns: JSON with news articles
        """
        try:
            to_date = datetime.now().strftime("%Y-%m-%d")
            from_date = (datetime.now() - timedelta(days=days)).strftime("%Y-%m-%d")
            
            url = "https://newsapi.org/v2/everything"
            params = {
                'q': query,
                'from': from_date,
                'to': to_date,
                'sortBy': 'publishedAt',
                'language': 'en',
                'pageSize': 5,
                'apiKey': NEWS_API_KEY
            }
            
            response = requests.get(url, params=params, timeout=10)
            
            if response.status_code != 200:
                return json.dumps({
                    'status': 'error',
                    'message': f'NewsAPI error: {response.status_code}'
                })
            
            articles = response.json().get('articles', [])
            formatted_articles = []
            
            for article in articles:
                formatted_articles.append({
                    'title': article.get('title', 'N/A'),
                    'source': article.get('source', {}).get('name', 'Unknown'),
                    'published_at': article.get('publishedAt', 'N/A'),
                    'url': article.get('url', 'N/A'),
                    'description': article.get('description', '')[:200]
                })
            
            return json.dumps({
                'status': 'success',
                'count': len(formatted_articles),
                'articles': formatted_articles
            })
        except Exception as e:
            return json.dumps({'status': 'error', 'message': str(e)})
    
    @staticmethod
    def get_stock_price(symbol: str) -> str:
        """
        Get current stock price, historical trend, and key levels.
        Returns: JSON with price data
        """
        try:
            stock = yf.Ticker(symbol)
            info = stock.info
            current_price = info.get('currentPrice') or info.get('regularMarketPrice')
            
            hist = stock.history(period='1y')
            
            if len(hist) == 0:
                return json.dumps({'status': 'error', 'message': f'No data for {symbol}'})
            
            price_6m_ago = hist['Close'].iloc[-126] if len(hist) >= 126 else hist['Close'].iloc[0]
            price_1y_ago = hist['Close'].iloc[0]
            change_6m = ((hist['Close'].iloc[-1] - price_6m_ago) / price_6m_ago) * 100
            change_1y = ((hist['Close'].iloc[-1] - price_1y_ago) / price_1y_ago) * 100
            high_52w = hist['Close'].max()
            low_52w = hist['Close'].min()
            
            return json.dumps({
                'status': 'success',
                'symbol': symbol,
                'current_price': round(float(current_price), 2) if current_price else 'N/A',
                'price_52w_high': round(float(high_52w), 2),
                'price_52w_low': round(float(low_52w), 2),
                'change_6m_percent': round(change_6m, 2),
                'change_1y_percent': round(change_1y, 2),
                'last_updated': datetime.now().isoformat()
            })
        except Exception as e:
            return json.dumps({'status': 'error', 'message': str(e)})
    
    @staticmethod
    def get_financial_metrics(symbol: str) -> str:
        """
        Get key financial metrics: PE ratio, EPS, dividend, debt, etc.
        Returns: JSON with financial data
        """
        try:
            stock = yf.Ticker(symbol)
            info = stock.info
            
            metrics = {
                'status': 'success',
                'symbol': symbol,
                'pe_ratio': round(info.get('trailingPE', 0), 2) if info.get('trailingPE') else 'N/A',
                'forward_pe': round(info.get('forwardPE', 0), 2) if info.get('forwardPE') else 'N/A',
                'eps': round(info.get('eps', 0), 2) if info.get('eps') else 'N/A',
                'dividend_yield_percent': round(info.get('dividendYield', 0) * 100, 2) if info.get('dividendYield') else 0,
                'debt_to_equity': round(info.get('debtToEquity', 0), 2) if info.get('debtToEquity') else 'N/A',
                'profit_margin_percent': round(info.get('profitMargins', 0) * 100, 2) if info.get('profitMargins') else 'N/A',
                'roe_percent': round(info.get('returnOnEquity', 0) * 100, 2) if info.get('returnOnEquity') else 'N/A',
                'market_cap_billions': round(info.get('marketCap', 0) / 1e9, 2) if info.get('marketCap') else 'N/A',
                'revenue_billions': round(info.get('totalRevenue', 0) / 1e9, 2) if info.get('totalRevenue') else 'N/A',
                'beta': round(info.get('beta', 0), 2) if info.get('beta') else 'N/A'
            }
            
            return json.dumps(metrics)
        except Exception as e:
            return json.dumps({'status': 'error', 'message': str(e)})
    
    @staticmethod
    def calculate_technical_indicators(symbol: str) -> str:
        """
        Calculate moving averages, RSI, and trend signals.
        Returns: JSON with technical analysis
        """
        try:
            stock = yf.Ticker(symbol)
            hist = stock.history(period='1y')
            
            if len(hist) < 200:
                return json.dumps({'status': 'error', 'message': 'Insufficient data'})
            
            ma_20 = hist['Close'].rolling(window=20).mean().iloc[-1]
            ma_50 = hist['Close'].rolling(window=50).mean().iloc[-1]
            ma_200 = hist['Close'].rolling(window=200).mean().iloc[-1]
            current_price = hist['Close'].iloc[-1]
            
            if current_price > ma_50 > ma_200:
                trend = "Strong Uptrend"
                trend_strength = "Bullish"
            elif current_price > ma_50:
                trend = "Uptrend"
                trend_strength = "Moderately Bullish"
            elif current_price < ma_50 < ma_200:
                trend = "Strong Downtrend"
                trend_strength = "Bearish"
            elif current_price < ma_50:
                trend = "Downtrend"
                trend_strength = "Moderately Bearish"
            else:
                trend = "Consolidation"
                trend_strength = "Neutral"
            
            delta = hist['Close'].diff()
            gain = (delta.where(delta > 0, 0)).rolling(window=14).mean()
            loss = (-delta.where(delta < 0, 0)).rolling(window=14).mean()
            rs = gain / loss
            rsi = 100 - (100 / (1 + rs.iloc[-1]))
            
            if rsi > 70:
                rsi_signal = "Overbought (potential pullback)"
            elif rsi < 30:
                rsi_signal = "Oversold (potential bounce)"
            else:
                rsi_signal = "Neutral"
            
            return json.dumps({
                'status': 'success',
                'symbol': symbol,
                'current_price': round(float(current_price), 2),
                'ma_20': round(float(ma_20), 2),
                'ma_50': round(float(ma_50), 2),
                'ma_200': round(float(ma_200), 2),
                'trend': trend,
                'trend_strength': trend_strength,
                'rsi_14': round(float(rsi), 2),
                'rsi_signal': rsi_signal
            })
        except Exception as e:
            return json.dumps({'status': 'error', 'message': str(e)})
    
    @staticmethod
    def analyze_sentiment(text: str) -> str:
        """
        Analyze sentiment of text (news articles, analyst reports, etc).
        Returns: JSON with sentiment analysis
        """
        try:
            from transformers import pipeline
            
            sentiment_pipeline = pipeline(
                "sentiment-analysis",
                model="distilbert-base-uncased-finetuned-sst-2-english"
            )
            
            text_limited = text[:512]
            result = sentiment_pipeline(text_limited)
            
            sentiment = result[0]['label']
            confidence = round(result[0]['score'], 3)
            
            return json.dumps({
                'status': 'success',
                'sentiment': sentiment,
                'confidence': confidence,
                'interpretation': f"{sentiment} sentiment with {confidence*100:.1f}% confidence"
            })
        except Exception as e:
            return json.dumps({'status': 'error', 'message': str(e)})


# Wrapper functions for LangChain
def search_stock_news(symbol: str) -> str:
    """Tool: Search for stock news"""
    return FinanceTools.search_news(symbol)


def get_current_price(symbol: str) -> str:
    """Tool: Get current stock price and trend"""
    return FinanceTools.get_stock_price(symbol)


def get_fundamentals(symbol: str) -> str:
    """Tool: Get financial metrics and fundamentals"""
    return FinanceTools.get_financial_metrics(symbol)


def get_technical_analysis(symbol: str) -> str:
    """Tool: Get technical indicators and trend"""
    return FinanceTools.calculate_technical_indicators(symbol)


def analyze_text_sentiment(text: str) -> str:
    """Tool: Analyze sentiment of text"""
    return FinanceTools.analyze_sentiment(text)


# Test
if __name__ == "__main__":
    print("=== Testing Tools ===\n")
    symbol = "AAPL"
    
    print("1. Stock Price:")
    print(FinanceTools.get_stock_price(symbol))
    print("\n2. Financial Metrics:")
    print(FinanceTools.get_financial_metrics(symbol))
    print("\n3. Technical Indicators:")
    print(FinanceTools.calculate_technical_indicators(symbol))
    print("\n4. News:")
    print(FinanceTools.search_news(symbol))
    print("\n5. Sentiment:")
    print(FinanceTools.analyze_sentiment("Apple stock is looking strong with great financial performance"))