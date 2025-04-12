from langgraph.graph import StateGraph
from typing import Annotated
from typing_extensions import TypedDict
from langgraph.graph.message import add_messages
from langchain_ollama import ChatOllama
from langchain_community.tools.tavily_search import TavilySearchResults
from langgraph.prebuilt import ToolNode,tools_condition
#from IPython.display import Image, display
from langchain_core.tools import tool
from langgraph.checkpoint.sqlite import SqliteSaver
from langgraph.checkpoint.memory import MemorySaver

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


#Lets create toolNode run the tools if they are called by adding the tools to a new node
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

#graph visualize uncomment in the import section 
#from IPython.display import Image, display

# display(Image(graph.get_graph().draw_mermaid_png))
# print(graph.get_graph().draw_ascii())

#Add memory to the graph
memory = SqliteSaver.from_conn_string(':memory:')
graph = graph_builder.compile(checkpointer=MemorySaver())


#Chatbot with memory
while True:
    user_input = input('User: ')
    if user_input.lower() in ['quit','exit','bye',':q','!q']:
        print('Goodbye!')
        break
    config = {'configurable' : {'thread_id': '1'}}
    for event in graph.stream({'messages': ('user', user_input)}, config=config):
        for value in event.values():
            print(f'Assistant: {value["messages"][-1].content}')
            print('-'* 20)


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
