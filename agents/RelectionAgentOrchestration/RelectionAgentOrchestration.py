from langchain_ollama import ChatOllama
from langchain_core.messages import AnyMessage, SystemMessage, HumanMessage, AIMessage, ChatMessage
from langgraph.graph import StateGraph, END
from typing import List, Annotated
from pydantic import BaseModel
from tavily import TavilyClient
from langgraph.checkpoint.sqlite import SqliteSaver
from langgraph.checkpoint.memory import MemorySaver
from IPython.display import Image, display
import pprint

# STEP 1: THE PREPARATION PHASE
# STEP 1.1 define the model
model = ChatOllama(model="qwen2.5:7b",verbose=True)
# STEP 1.2 Define the agent state
class AgentState(BaseModel):
    task: str
    plan: str = ""
    draft: str = ""
    critique: str = ""
    content: List[str] = []
    revision_number: int
    max_revisions: int
# STEP 1.3 set the query data type and  & tooling
class Queries(BaseModel):
    queries: List[str]

tavily = TavilyClient(api_key="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")

# STEP 2: IMPLEMENTING THE NODES/AGENTS
# STEP 2.1 define planning prompt

PLAN_PROMPT = '''You are an expert Writter tasked with writing a high level outline of an essay.
write such outline for the user provided topic.
Give an outline of the eassy along with any relavant notes or instructions for the sections.'''
# STEP 2.2 define the plann node

def plan_node(state: AgentState):
    messages = [
        SystemMessage(content=PLAN_PROMPT),
        HumanMessage(content=state.task)  # Changed from state['task'] to state.task
    ]
    response = model.invoke(messages)
    return{"plan": response.content}

# STEP 2.3 define the research planner prompt

RESEARCH_PLAN_PROMPT = '''You are an expert researcher charged with providing information that can be used when writing the following.
Generate a list of search queries that will gather any relavant information. Only generate 3 queries maximum.'''

# STEP 2.4 define the research planner node/agent node

def research_plan_node(state: AgentState):
    queries = model.with_structured_output(Queries).invoke(
        [
            SystemMessage(content=RESEARCH_PLAN_PROMPT),
            HumanMessage(content=state.task)  # Changed from state['task'] to state.task
        ]
    )

    content = state.content or []  # Changed from state.get('content', []) to state.content

    for q in queries.queries:
        response = tavily.search(query=q, max_results=2)
        for r in response['results']:
            content.append(r['content'])
    return {"content": content}

# STEP 2.5 define the writer prompt
WRITER_PROMPT = '''You are an expert essay writer assistant tasked with writing excellent 5-paragraph essays.
Generate the best essay possible for the user's request and the initial outline.
If the user provides critique, respond with a revised version of your previous attempts incorporating the critique feedbacks.
Utilize all the information below as needed:
----------------

{content}'''  # Fixed placeholder to match the variable name

# STEP 2.6 define the writer or generation node/agent node
def generation_node(state: AgentState):
    content = "\n\n".join(state.content or [])  # Changed from state['content'] to state.content
    user_message = HumanMessage(
        content=f"{state.task}\n\nHere is my plan:\n\n{state.plan}")
    messages = [
        SystemMessage(
            content=WRITER_PROMPT.format(content=content)),
        user_message
    ]
    response = model.invoke(messages)

    return {"draft": response.content, "revision_number": state.revision_number + 1}  # Changed from state['revision_number'] to state.revision_number

# STEP 2.7 define the reflection prompt

REFLECTION_PROMPT = '''You are experienced Teacher grading an eassy submission.
Generate critique and recomendations for the user's submission,
Provide very detailed recomendations, including requests for length, depts, style, power of the content,
impact on the reader, resourcefullness, etc..'''

# STEP 2.8 define the reflection node/agent node
def reflection_node(state: AgentState):
    messages = [
        SystemMessage(content=REFLECTION_PROMPT),
        HumanMessage(content=state.draft)  # Changed from state['draft'] to state.draft
    ]
    response = model.invoke(messages)
    return {"critique": response.content}

# STEP 2.9 define the critique researcher prompt
RESEARCH_CRITIQUE_PROMPT = '''You are a experienced researcher charged with providing information that can be 
used when making any requested revisions (as out;ined below).
Generate a list of search queries that will gather any relavant information. Only generate 3 queries maximum.'''

# STEP 2.9 define the critique node/agent node
def research_critique_node(state: AgentState):
    queries = model.with_structured_output(Queries).invoke(
        [
            SystemMessage(content=RESEARCH_CRITIQUE_PROMPT),
            HumanMessage(content=state.critique)  # Changed from state['critique'] to state.critique
        ]
    )
    content = state.content or []  # Changed from state['content'] to state.content
    for q in queries.queries:
        response = tavily.search(query=q, max_results=2)
        for r in response['results']:
            content.append(r['content'])
    return {"content": content}

# STEP 3: THE GRAPH
# STEP 3.1 define the conditional edge

def should_continue(state: AgentState):
    if state.revision_number > state.max_revisions:  # Changed from state['revision_number'] and state['max_revisions'] to dot notation
        return END
    return 'reflect'
# STEP 3.2 define the graph
builder = StateGraph(AgentState)

# add node to the graph
builder.add_node('planner', plan_node)
builder.add_node('generate', generation_node)
builder.add_node('reflect', reflection_node)
builder.add_node('research_plan', research_plan_node)
builder.add_node('research_critique', research_critique_node)
#Entry point
builder.set_entry_point('planner')
#add conditional edges
builder.add_conditional_edges(
    'generate', should_continue, {END: END, 'reflect': 'reflect'})
#add regular edges

builder.add_edge('planner', 'research_plan')
builder.add_edge('research_plan', 'generate')
builder.add_edge('reflect', 'research_critique')
builder.add_edge('research_critique', 'generate')

# STEP 4: ADD MEMORY
memory = SqliteSaver.from_conn_string(':memory:')
graph = builder.compile(checkpointer=MemorySaver())

# STEP 5: THE GRAPH IN ACTION
# STEP 5.1 view the graph

# display(Image(graph.get_graph().draw_mermaid_png))
# print(graph.get_graph().draw_ascii())

# STEP 5.2 Running the grapg

thread = {'configurable' : {'thread_id': '1'}}
task = 'Reflection vs Reflexion Agents'

prompt = {
    'task': task,
    'revision_number': 1,
    'max_revisions': 2,
}

events = graph.stream(prompt,thread)
for e in events:
    print(e)
    print("===" * 100)       
#The final product

