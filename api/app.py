"""
FastAPI backend for FinanceBot.
Provides REST API for stock analysis.
"""
import os
import sys
import json
from datetime import datetime
from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from typing import List
from dotenv import load_dotenv

# Add project root to Python path (CRITICAL FIX)
project_root = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, project_root)

load_dotenv()

app = FastAPI(
    title="FinanceBot API",
    description="AI-powered stock analysis API",
    version="1.0.0"
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

from src.agent import FinanceAgent
from src.report_generator import ReportGenerator

agent = FinanceAgent()
report_gen = ReportGenerator()


class AnalysisRequest(BaseModel):
    symbol: str
    analysis_type: str = "comprehensive"


class AnalysisResponse(BaseModel):
    symbol: str
    status: str
    analysis: str
    timestamp: str


class ComparisonRequest(BaseModel):
    symbols: List[str]


@app.get("/")
def root():
    """Health check and info"""
    return {
        "name": "FinanceBot API",
        "version": "1.0.0",
        "status": "healthy",
        "docs": "/docs"
    }


@app.post("/analyze", response_model=AnalysisResponse)
async def analyze_stock(request: AnalysisRequest):
    """Analyze a stock."""
    try:
        result = agent.analyze_stock(request.symbol, request.analysis_type)
        
        if result['status'] != 'success':
            raise HTTPException(status_code=500, detail=result.get('error', 'Analysis failed'))
        
        report = report_gen.generate_markdown(
            request.symbol,
            result['analysis'],
            request.analysis_type
        )
        
        report_gen.save_report(report, request.symbol)
        
        return AnalysisResponse(
            symbol=request.symbol,
            status='success',
            analysis=report,
            timestamp=datetime.now().isoformat()
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@app.post("/compare")
async def compare_stocks(request: ComparisonRequest):
    """Compare multiple stocks."""
    try:
        result = agent.compare_stocks(request.symbols)
        
        if result['status'] != 'success':
            raise HTTPException(status_code=500, detail=result.get('error', 'Comparison failed'))
        
        return {
            'status': 'success',
            'symbols': request.symbols,
            'comparison': result['comparison'],
            'timestamp': datetime.now().isoformat()
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@app.get("/price/{symbol}")
async def get_price(symbol: str):
    """Quick price check"""
    from src.tools import FinanceTools
    result = FinanceTools.get_stock_price(symbol)
    return json.loads(result)


@app.get("/fundamentals/{symbol}")
async def get_fundamentals(symbol: str):
    """Get financial metrics"""
    from src.tools import FinanceTools
    result = FinanceTools.get_financial_metrics(symbol)
    return json.loads(result)


@app.get("/technical/{symbol}")
async def get_technical(symbol: str):
    """Get technical analysis"""
    from src.tools import FinanceTools
    result = FinanceTools.calculate_technical_indicators(symbol)
    return json.loads(result)


@app.get("/news/{symbol}")
async def get_news(symbol: str):
    """Get recent news"""
    from src.tools import FinanceTools
    result = FinanceTools.search_news(symbol)
    return json.loads(result)


@app.on_event("startup")
async def startup_event():
    print("FinanceBot API started successfully!")


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)