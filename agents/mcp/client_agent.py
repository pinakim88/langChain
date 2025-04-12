import asyncio
from langchain_mcp_adapters.client import MultiServerMCPClient
from langgraph.prebuilt import create_react_agent
from langchain_ollama import ChatOllama

async def main():
    # Create a ChatOllama instance for the language model
    model = ChatOllama(model="qwen2.5:7b",verbose=True)
    # Initialize the client with the server address and port
    async with MultiServerMCPClient(
        {
            "weather": {
#make sure you start your weather server on port 8000
                "url":"http://localhost:8000/sse",
                "transport":"sse",
            }
        }
    ) as client:
        # Create a React agent with the chat model and the MCP client
        agent = create_react_agent(model, client.get_tools())

        # Use the agent to call the get_weather tool
        weather_response = await agent.ainvoke({"messages":[{"role":"user","content":"what is the current weather in New York?"}]})
        print("Weather Response:", weather_response["messages"][-1].content)

if __name__ == "__main__":
    print("hello")
    asyncio.run(main())