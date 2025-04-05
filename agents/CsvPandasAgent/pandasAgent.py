from langchain_ollama import ChatOllama
from langchain_experimental.agents.agent_toolkits import create_pandas_dataframe_agent
import pandas as pd
from IPython.display import display

#Create pandas dataframe
df = pd.read_csv("product.txt")
display(df)
#Create Ollama LLM

llm = ChatOllama(temperature=1, model="llama3.2:3b")

#Create Agent
pandas_agent = create_pandas_dataframe_agent(
    llm,
    df,
    agent_type = "tool-calling",
     verbose=False,
     allow_dangerous_code=True
)

#Running the Agent

response = pandas_agent.invoke("what is the total Names are listed in the document?")

#Display AI output

print(response['output'])
