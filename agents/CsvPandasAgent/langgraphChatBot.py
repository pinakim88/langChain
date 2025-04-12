import pprint
from langgraph.graph import StateGraph
from typing import Annotated
from typing_extensions import TypedDict
from langgraph.graph.message import add_messages
from langchain_ollama import ChatOllama
from tavily import TavilyClient
from langchain.prompts import ChatPromptTemplate
from langchain_community.tools.tavily_search import TavilySearchResults
from langgraph.prebuilt import ToolNode,tools_condition
from IPython.display import Image, display
from langchain_core.tools import tool
from langchain_core.messages import HumanMessage, AIMessage, ToolMessage
from langchain_community.utilities import DuckDuckGoSearchAPIWrapper,WikipediaAPIWrapper
from langchain_community.tools import WikipediaQueryRun




#Initialized the model
model = ChatOllama(temperature=0.5, model="qwen2.5:7b")

class State(TypedDict):
 messages: Annotated[list, add_messages]

graph_builder = StateGraph(State)

tool = TavilySearchResults(max_result=3,tavily_api_key="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")
tools = [tool]

model_with_tools = model.bind_tools(tools)

# # Define chatbot node function
def chatbot(state: State):
    return {"messages": [model_with_tools.invoke(state["messages"])]}

# Add node to graph

graph_builder.add_node("chatbot", chatbot)


#Lets create tooNode run the tools if they are called by adding the tools to a new node
#this node runs the tools requested in the AIMessage

tool_node = ToolNode(tools=[tool])
graph_builder.add_node("tools", tool_node)


# define conditional edges
# we will use prebuild tools_condtion in the condoitional edge to route to the ToolNode if the last message has tool calls,
# otherwise , route to the end.

graph_builder.add_conditional_edges(
    "chatbot",
    tools_condition,
)

# any time a tool is called we return to the chatbot
graph_builder.add_edge("tools","chatbot")


# setting the entry point and end point
graph_builder.set_entry_point("chatbot")
#graph_builder.set_finish_point("chatbot")

graph = graph_builder.compile()

#graph visualize

# display(Image(graph.get_graph().draw_mermaid_png))
# print(graph.get_graph().draw_ascii())
while True:
    user_input = input('User: ')
    if user_input.lower() in ['quit','exit','bye',':q','!q']:
        print('Goodbye!')
        break
    for event in graph.stream({'messages': ('user', user_input)}):
        for value in event.values():
            print(f'Assistant: {value["messages"][-1].content}')
            print('-'* 20)

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

# To install: pip install tavily-python

# query='what is the latest news with Google Next 2025?'

# client = TavilyClient("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")
# response = client.search(query,max_results=8,search_depth='advanced')['results']

# # print(response)

# # Setting up the prompt to build the researcher
# template = """You are an AI ciritical thinker reserch assistant. Your sole purpose is to write well written, 
# objective and structured reports on given text.
# Information: "{response}"
# Using the above information, answer the following query: "{query}" in a detailed report."""

# # Preparing the prompt with speafic data
# prompt = ChatPromptTemplate.from_template(template)
# formatted_prompt = prompt.format(response=response,query=query)

# result = model.invoke(formatted_prompt)
# print(result.content)
