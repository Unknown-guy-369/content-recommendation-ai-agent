#  AI ReAct Agent with Keyword Extraction & Web Scraping

This project uses a **LangGraph-based ReAct agent** to:

- Extract **search keywords** from a user query.
- Use **Firecrawl MCP tools** to search and summarize web content.
- Return a **summarized response** via a React frontend.

---

##  Tech Stack

- **Frontend**: React + Tailwind CSS  
- **Backend**: Flask + LangGraph + Firecrawl + MCP Tools  
- **LLM Model**: DeepSeek (via OpenRouter)  
- **Keyword Extraction**: Custom tool with LangChain  
- **Web Scraping & Summarization**: Firecrawl MCP  
- **Agent Orchestration**: LangGraph (ReAct agent)

---

##  How It Works

1. **User enters a query** in the React frontend.
2. **Flask backend**:
   - Extracts keywords using a system prompt.
   - Sends keywords to a ReAct agent (LangGraph).
   - Agent uses Firecrawl tools to search and summarize content.
3. **Summarized result** is returned and displayed in the frontend.

---

 Built for intelligent, explainable, and reactive content recommendations.
