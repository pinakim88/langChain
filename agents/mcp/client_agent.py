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
                # Make sure you start your weather server on port 8000
                "url": "http://localhost:8000/sse",
                "transport": "sse",
            },
            "math": {
                # Make sure you start your math server on port 8001
                "url": "http://localhost:8001/sse",
                "transport": "sse",
            }
        }
    ) as client:
        # Create a React agent with the chat model and the MCP client
        agent = create_react_agent(model, client.get_tools())
        print(agent, debug=True)

        # Use the agent to call the get_weather tool
        response = await agent.ainvoke({"messages": [{"role": "user", "content": "Ram has 2 banana and Sam has 3 banana ,\
        How many total Banana they have ? now they gave have 2 banana to Hari how many total banana Ram and Sam has now? after\
        this Jadu asked can you multily total left banana with ram and sam by 10?"}]})
        print("Response:", response["messages"][-1].content)

if __name__ == "__main__":
    asyncio.run(main())