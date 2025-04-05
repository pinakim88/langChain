# Import the needed modules
import wikipedia
import pprint
from langchain_core.tools import tool
from langchain_core.messages import HumanMessage, AIMessage, ToolMessage
from langchain_community.utilities import DuckDuckGoSearchAPIWrapper,WikipediaAPIWrapper
from langchain_community.tools import WikipediaQueryRun
from langgraph.prebuilt import create_react_agent
from langchain_ollama import ChatOllama

# Parse the message as do not have LangSmith paid version

def parse_agent_messages(messages):
    for msg in messages:
        if isinstance(msg, HumanMessage):
            print(f"User: {msg.content}\n")
        elif isinstance(msg, AIMessage):
            if 'tool_calls' in msg.additional_kwargs and msg.additional_kwargs['tool_calls']:
                print("Agent is deciding to use tools...\n")
                for tool_call in msg.additional_kwargs['tool_calls']:
                    tool_name = tool_call['function']['name']
                    arguments = tool_call['function']['arguments']
                    print(f"Agent calls tool: {tool_name} with arguments {arguments}\n")
            else:
                print(f"Agents Final response:\n{msg.content}\n")
        elif isinstance(msg, ToolMessage):
            tool_name = msg.name
            print(f"Tool [{tool_name}] Response:\n{msg.content}\n")
        else:
            print(f"Unknown message type: {msg}\n")






# Define the tool for DuckDuckGo search
@tool
def search_duckduckgo(query: str) -> str:
    """Search DuckDuckGo for a given query and return the first result snippet."""
    wrapper = DuckDuckGoSearchAPIWrapper(max_results=10) #customizable as needed
    results = wrapper.results(query=query,max_results=10)
    if results:
        #print(results)
        result = results[0] #get only the first result
        return f"Title: {result['title']}\nSnippet: {result['snippet']}\nLink: {result['link']}"
    return "No Results Found"
@tool
def search_wikipedia(query: str) -> str:
    """Search Wikipedia for a given query and return a summary."""
    wikipedia = WikipediaQueryRun(api_wrapper=WikipediaAPIWrapper())
    return wikipedia.run(query)

# Test the wikipedia tool
#wiki_result = search_wikipedia.invoke("Donald Trump")
#print("WIKI RESULT", wiki_result)


# Test the duckduckgo tool
#duck_result = search_duckduckgo.invoke("Donald Trump")
#pprint.pprint(duck_result)

#Setup a language Model

model = ChatOllama(temperature=1, model="llama3.2:3b")

# List of tools creeated 

tools = [search_duckduckgo,search_wikipedia]

# Create Langgraph agent with tools
react_agent = create_react_agent(model, tools=tools)

# Define simple user query
query = "what is todays date?"

# Invoke the agent
messages = react_agent.invoke({"messages": [("human", query)]})

# Print the final result
parse_agent_messages(messages["messages"])


