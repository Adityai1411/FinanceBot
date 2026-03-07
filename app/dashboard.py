"""
Streamlit dashboard for FinanceBot.
Interactive UI for stock analysis.
"""
import streamlit as st
import requests
import json
from datetime import datetime
import os
from dotenv import load_dotenv

load_dotenv()

st.set_page_config(
    page_title="FinanceBot - AI Investment Analysis",
    page_icon="📈",
    layout="wide",
    initial_sidebar_state="expanded"
)

st.title("🤖 FinanceBot")
st.subheader("AI-Powered Investment Analysis")
st.write("Analyze stocks autonomously using AI. Get comprehensive analysis with reasoning and sources.")

with st.sidebar:
    st.header("Options")
    analysis_type = st.selectbox(
        "Analysis Type",
        ["comprehensive", "quick", "technical"],
        help="Type of analysis to perform"
    )
    api_url = st.text_input(
        "API URL",
        value="http://localhost:8000",
        help="FastAPI server URL"
    )

col1, col2 = st.columns([3, 1])

with col1:
    stock_symbol = st.text_input(
        "Enter Stock Symbol",
        value="AAPL",
        placeholder="e.g., AAPL, MSFT, GOOGL",
        help="Enter a valid stock symbol"
    ).upper()

with col2:
    analyze_button = st.button("🔍 Analyze", use_container_width=True, type="primary")

if analyze_button:
    if not stock_symbol:
        st.error("Please enter a stock symbol")
    else:
        with st.spinner(f"Analyzing {stock_symbol}... This may take 1-2 minutes."):
            try:
                response = requests.post(
                    f"{api_url}/analyze",
                    json={
                        "symbol": stock_symbol,
                        "analysis_type": analysis_type
                    },
                    timeout=180
                )
                
                if response.status_code == 200:
                    result = response.json()
                    st.success(f"Analysis complete for {stock_symbol}")
                    
                    tab1, tab2, tab3 = st.tabs(["📊 Analysis", "📈 Quick Stats", "💾 Download"])
                    
                    with tab1:
                        st.markdown(result['analysis'])
                    
                    with tab2:
                        col1, col2, col3, col4 = st.columns(4)
                        try:
                            price_resp = requests.get(
                                f"{api_url}/price/{stock_symbol}",
                                timeout=10
                            )
                            if price_resp.status_code == 200:
                                price_data = price_resp.json()
                                if price_data.get('status') == 'success':
                                    col1.metric("Current Price", f"${price_data.get('current_price', 'N/A')}")
                                    col2.metric("52W Change", f"{price_data.get('change_1y_percent', 'N/A')}%")
                                    col3.metric("52W High", f"${price_data.get('price_52w_high', 'N/A')}")
                                    col4.metric("52W Low", f"${price_data.get('price_52w_low', 'N/A')}")
                        except:
                            st.info("Unable to load quick stats")
                    
                    with tab3:
                        st.subheader("Export Report")
                        st.download_button(
                            label="📄 Download as Markdown",
                            data=result['analysis'],
                            file_name=f"{stock_symbol}_analysis_{datetime.now().strftime('%Y%m%d')}.md",
                            mime="text/markdown"
                        )
                        st.download_button(
                            label="📋 Download as Text",
                            data=result['analysis'],
                            file_name=f"{stock_symbol}_analysis_{datetime.now().strftime('%Y%m%d')}.txt",
                            mime="text/plain"
                        )
                else:
                    st.error(f"API Error: {response.status_code}")
                    st.error(response.text)
                    
            except requests.exceptions.ConnectionError:
                st.error(f"Cannot connect to API at {api_url}")
                st.info("Make sure the FastAPI server is running: `python -m uvicorn api/app:app --reload`")
            except requests.exceptions.Timeout:
                st.warning("Analysis took too long. Try a simpler analysis type (quick or technical)")
            except Exception as e:
                st.error(f"Error: {str(e)}")

st.divider()
st.subheader("🔄 Compare Stocks")

symbols_input = st.text_input(
    "Enter symbols to compare (comma-separated)",
    value="AAPL,MSFT,GOOGL",
    help="e.g., AAPL,MSFT,GOOGL"
)

if st.button("Compare"):
    if symbols_input:
        symbols = [s.strip().upper() for s in symbols_input.split(",")]
        with st.spinner("Comparing stocks..."):
            try:
                response = requests.post(
                    f"{api_url}/compare",
                    json={"symbols": symbols},
                    timeout=180
                )
                if response.status_code == 200:
                    result = response.json()
                    st.markdown(result['comparison'])
                else:
                    st.error(f"Error: {response.status_code}")
            except Exception as e:
                st.error(f"Error: {str(e)}")

st.divider()
col1, col2, col3 = st.columns(3)
with col1:
    st.info("ℹ️ This analysis is for informational purposes only. Not financial advice.")
with col2:
    st.info("📚 Check `/docs` endpoint for API documentation")
with col3:
    st.info("⚡ Powered by Hugging Face AI + Financial APIs")