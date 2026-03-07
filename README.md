```
123456
User Input (Stock Symbol)
↓
Hugging Face LLM (Agent Brain - Qwen2.5-7B-Instruct)
↓
Tool Calling (5 Financial Tools)
├─ Price & Trends (yfinance)
├─ Financial Metrics (yfinance)
├─ News & Sentiment (NewsAPI + Transformers)
├─ Technical Analysis (yfinance)
└─ Sentiment Analysis (DistilBERT)
↓
Reasoning Loop (Multi-step ReAct analysis)
↓
Report Generation (Markdown)
↓
Output: Professional Investment Report
123456

## Quick Start

### 1. Install Dependencies
```bash
pip install -r requirements.txt
2. Get Free API Keys
Hugging Face: https://huggingface.co/settings/tokens
NewsAPI: https://newsapi.org
3. Create .env File
12
4. Run Locally
bash
12345
Tech Stack
LLM: Hugging Face Inference API (Qwen2.5-7B-Instruct)
Agent Framework: LangChain 0.1.0 (ReAct Agent)
Data: yfinance, NewsAPI
Backend: FastAPI
Frontend: Streamlit
Author
Your Name
License
MIT
12345678910111213

---

# 🚀 HOW TO RUN EVERYTHING

## ✅ Step 1: Install Dependencies

```powershell
# Make sure venv is activated
.\venv\Scripts\Activate.ps1

✅ Step 2: Configure .env
Open .env and add your keys:
env
12
Get Keys:
Hugging Face: https://huggingface.co/settings/tokens
NewsAPI: https://newsapi.org/register
