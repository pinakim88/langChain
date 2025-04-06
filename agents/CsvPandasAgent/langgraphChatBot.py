import pprint
from langgraph.graph import StateGraph
from typing import Annotated
from typing_extensions import TypedDict
from langgraph.graph.message import add_messages
from langchain_ollama import ChatOllama
from tavily import TavilyClient
from langchain.prompts import ChatPromptTemplate
#from IPython.display import Image, display

# class State(TypedDict):
#     messages: Annotated[list, add_messages]

# graph_builder = StateGraph(State)

#Initialized the model

model = ChatOllama(temperature=0.5, model="deepseek-r1:7b")

# # Define the nodes
# def chatbot(state: State):
#     return {"messages": [model.invoke(state["messages"])]}

# # Add node to graph

# graph_builder.add_node("chatbot", chatbot)

# # setting the entry point and end point
# graph_builder.set_entry_point("chatbot")
# graph_builder.set_finish_point("chatbot")

# graph = graph_builder.compile()

#graph

# display(Image(graph.get_graph().draw_mermaid_png))
# print(graph.get_graph().draw_ascii())
# while True:
#     user_input = input('User: ')
#     if user_input.lower() in ['quit','exit','bye',':q','!q']:
#         print('Goodbye!')
#         break
#     for event in graph.stream({'messages': ('user', user_input)}):
#         for value in event.values():
#             print(f'Assistant: {value["messages"][-1].content}')
#             print('-'* 20)


# To install: pip install tavily-python

query='what is the latest news with NVDIA?'

client = TavilyClient("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")
response = client.search(query,max_results=8,search_depth='advanced')['results']

# print(response)

# Setting up the prompt to build the researcher
template = """You are an AI ciritical thinker reserch assistant. Your sole purpose is to write well written, 
objective and structured reports on given text.
Information: "{response}"
Using the above information, answer the following query: "{query}" in a detailed report."""

# Preparing the prompt with speafic data
prompt = ChatPromptTemplate.from_template(template)
formatted_prompt = prompt.format(response=response,query=query)

result = model.invoke(formatted_prompt)
print(result.content)
