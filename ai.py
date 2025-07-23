from flask import Flask, request, jsonify
import asyncio
from typing import Annotated, Optional, List, Sequence
from typing_extensions import TypedDict

from langchain_core.messages import AIMessage, HumanMessage, SystemMessage, BaseMessage
from langchain_openai import ChatOpenAI
from langgraph.prebuilt import create_react_agent
from langgraph.graph.message import add_messages
from langchain.tools import tool
from langgraph.prebuilt import ToolNode
from flask_cors import CORS
from langchain_google_genai import ChatGoogleGenerativeAI
import nest_asyncio
nest_asyncio.apply()


from firecrawl import FirecrawlApp
from mcp import ClientSession, StdioServerParameters
from mcp.client.stdio import stdio_client
from langchain_mcp_adapters.tools import load_mcp_tools
from dotenv import load_dotenv
import os
import json
load_dotenv()
app = Flask(__name__)
CORS(app)

FIRECRAWL_API_KEY = os.getenv("FIRECRAWL_API_KEY")
DEEPSEEK_API_KEY=os.getenv("DEEPSEEK_API_KEY")
DEEPSEEK_MODEL_NAME=os.getenv("DEEPSEEK_MODEL_NAME")
MODEL_BASE_URL=os.getenv("MODEL_BASE_URL")
GEMINI_API_KEY=os.getenv("GEMINI_API_KEY")

class AgentState(TypedDict, total=False):
    messages: Annotated[Sequence[BaseMessage], add_messages]
    keywords: Optional[List[str]]

# Model
model = ChatOpenAI(
    api_key=DEEPSEEK_API_KEY,
    model=DEEPSEEK_MODEL_NAME,
    base_url=MODEL_BASE_URL
)



# model = ChatGoogleGenerativeAI(
#     model="gemini-2.5-pro",
#     google_api_key=GEMINI_API_KEY
# )



@tool
def Keyword_extractor(state: AgentState) -> AgentState:
    """Extract keywords from user input"""
    prompt = SystemMessage(
        content=(
            "You are a helpful assistant.You don't need to generate keyword for general question . Extract **search keywords** from the user query. "
            "Return only a Python list of keywords. Example: [\"flutter\", \"state management\"]"
        )
    )
    response = model.invoke([prompt] + state["messages"])
    
    try:
        keywords = json.loads(response.content)
        print("keyord : ",keywords)
        if isinstance(keywords, list) and all(isinstance(k, str) for k in keywords):
            state["keywords"] = keywords
        else:
            state["keywords"] = ["[Invalid response format]"]
    except json.JSONDecodeError:
        
        state["keywords"] = ["[Failed to parse keywords]"]
    return state

# Firecrawl MCP
server_params = StdioServerParameters(
    command="npx",
    env={"FIRECRAWL_API_KEY": FIRECRAWL_API_KEY},
    args=["firecrawl-mcp"]
)



async def agent_main(state: AgentState) -> AgentState:
    async with stdio_client(server_params) as (read, write):
        async with ClientSession(read, write) as session:
            await session.initialize()
            tools = await load_mcp_tools(session)
            agent = create_react_agent(model, tools)

            keywords = state.get("keywords", [])
            search_query = " ".join(keywords)

            system_message = {
                "role": "system",
                "content": (
                    "You are a helpful assistant that you can response general message without keyword+ or scrapes and analyzes content using Firecrawl tools. "
                    "Use appropriate tools and respond clearly."
                )
            }
            user_message = {"role": "user", "content": f"Search and summarize:{state['messages']} {search_query}"}

            messages = [system_message, user_message]
            result = await agent.ainvoke({"messages": messages})

            final_response = result["messages"][-1].content
            state["messages"].append(AIMessage(content=final_response))
            return state


@app.route("/agent", methods=["POST"])
def run_agent():
    data = request.json
    user_input = data.get("query")

    if not user_input:
        return jsonify({"error": "Query is required"}), 400

    async def run_pipeline():
        state: AgentState = {
            "messages": [HumanMessage(content=user_input)]
        }
        state = await Keyword_extractor.ainvoke({"state": state})

        state = await agent_main(state)

        return {
            "keywords": state.get("keywords", []),
            "response": state["messages"][-1].content
        }

    result = asyncio.run(run_pipeline())
    return jsonify(result)

if __name__ == "__main__":
    app.run(debug=True)
