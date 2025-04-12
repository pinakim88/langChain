from langchain_ollama import ChatOllama
from langchain_core.messages import HumanMessage, BaseMessage
from langchain_core.prompts import ChatPromptTemplate, MessagesPlaceholder
from typing import List, Sequence
from langgraph.graph import END, MessageGraph
#STEP - 1 GENERATE 
#BUILD GENERATE PROMPT & CHAIN
# Creating a chat promt template
generation_prompt = ChatPromptTemplate.from_messages(
    [
        (
            'system',
            '''You are a awesome linkedin content writer expert assigned to craft innovative and outstanding linkedin posts.
            Generate the most reader engaging and very impactful posts possible based on the user's request.
            If the user provides feedback, refine and enhance your previous attempts accordingly for maximum engagement. ''',
        ),
        MessagesPlaceholder(variable_name='messages'),
    ]
)
# Create the model for generation
generation_model = ChatOllama(temperature=1, model="llama3.2:3b")

#Using LCEL to create the generate_chain
generate_chain = generation_prompt | generation_model
# generate_chain
#test the generation chain
linkedinpost = ''
# request = HumanMessage(
#     content='U.S.A Election 2024'
# )
# result = generate_chain.invoke({'messages': [request]})
# pprint.pprint(result.content)

#BUILD REFLECTION PROMPT & CHAIN
reflection_prompt = ChatPromptTemplate.from_messages(
    [
        (
            'system',
            '''You are a awesome linkedin influencer known for your innovative and reader engaging outstanding content and sharp insights.
            Review and ciritique the user's linkedin messages.
            provide constructive feedback, focusing on enhancing its depth, style and overall impact on the readers.
            Offer specific suggestions to make the linkedin posts more compelling engaging and impactful for the audience ''',
        ),
        MessagesPlaceholder(variable_name='messages'),
    ]
)
# Create the model for critic
reflection_model = ChatOllama(temperature=0, model="deepseek-r1:7b")
#Using LCEL to create the generate_chain
reflect_chain = reflection_prompt | reflection_model

#Test the reflection chain
reflection = ''
#stream the response
# for chunk in reflect_chain.stream(
#     {'messages': [request,HumanMessage(content=linkedinpost)]}
# ):
#     print(chunk.content,end='')
#     reflection += chunk.content

## define a function for the generation node
def generation_node(state: Sequence[BaseMessage]):
    print("[Generation Node] Input State:", state)
    result = generate_chain.invoke(
        {'messages': state}
    )
    print("[Generation Node] Output:", result.content)
    return result

#define a function for the reflection node
# Switching the roles of 'human' and 'ai' in the reflection_node function
def reflection_node(messages: Sequence[BaseMessage]) -> List[BaseMessage]:
    print("[Reflection Node] Input Messages:", messages)
    # Convert messages to a format supported by Ollama
    ollama_messages = [
        {
            "role": "ai" if msg.type == "human" else "ai",  # Switched roles
            "content": msg.content
        }
        for msg in messages
    ]
    print("[Reflection Node] Converted Messages:", ollama_messages)

    res = reflect_chain.invoke(
        {"messages": ollama_messages}
    )

    print("[Reflection Node] Output:", res.content)
    # Return the result as a HumanMessage
    return HumanMessage(
        content=res.content,
        type="human"  # Ensuring the type is always 'human'
    )
# Create the graph
builder = MessageGraph()
builder.add_node('generate', generation_node)
builder.add_node('reflect', reflection_node)

builder.set_entry_point('generate')

#define the conditional edge
MAX_ITARATIONS = 5
def should_continue(state: List[BaseMessage]):
    #check the number of iterations
    if len(state) > MAX_ITARATIONS:
        return END
    #check the content of the last message
    if state[-1].content == END:
        return False
    #otherwise continue
    return 'reflect'

#add the edge to graph
builder.add_conditional_edges(
    'generate', should_continue
)
builder.add_edge('reflect', 'generate')

graph = builder.compile()

input = HumanMessage(
    content='Generate a linkedin post for the topic of USA election 2024.'
)
#run the graph
response = graph.invoke(input)

for message in response:
    print(message.content)
    print('\n' + '-' * 100 + '\n')