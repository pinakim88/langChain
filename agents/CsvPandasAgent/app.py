from langchain.agents.agent_types import AgentType
from langchain_experimental.agents.agent_toolkits import create_csv_agent
from langchain_ollama import ChatOllama

## Creating the CSV agent

agent = create_csv_agent(
    ChatOllama(temperature=0, model="llama3.2:3b"),
    "products-10000.csv",
    verbose=True,
    AgentType=AgentType.OPENAI_FUNCTIONS,
    allow_dangerous_code=True
)

##Run the agent

result = agent.invoke("what is the Name of product which has internal ID 54?")

##Display result
print(result['output'])
