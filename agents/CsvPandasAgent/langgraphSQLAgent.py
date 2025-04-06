#import sqlite3
#import pandas as pd
import pprint
#from IPython.display import display
from langchain_community.utilities import SQLDatabase
from langchain_community.agent_toolkits.sql.toolkit import SQLDatabaseToolkit
from langchain_ollama import ChatOllama
from langchain import hub
from langchain_core.messages import HumanMessage, AIMessage, ToolMessage
from langgraph.prebuilt import create_react_agent


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

# # Connect to sqlite3 database
# conn = sqlite3.connect("chinook.db")

# # Write a query to get the data from a table (e.g., ['albums', 'artists', 'customers', 'employees', 'genres', 'invoice_items', 'invoices', 'media_types', 'playlist_track', 'playlists', 'tracks'] etc.)
# query = "SELECT * FROM customers" # CUSTOMERS TABLE

# # Load the query in into Pandas dataframe
# df = pd.read_sql_query(query, conn)

# # Display the table
# display(df)

# #Close the connection to the database
# conn.close()

# Connect to SQLLite database !make sure the path is correct
db = SQLDatabase.from_uri("sqlite:///chinook.db")
# print(db.dialect)
# print(db.get_usable_table_names())

# Add LLM model
model = ChatOllama( model="llama3.2:3b")

toolkit =  SQLDatabaseToolkit(db=db,llm=model)
sql_tools = toolkit.get_tools()
# pprint.pprint(sql_tools)
prompt_template = hub.pull("langchain-ai/sql-agent-system-prompt")
print(prompt_template.input_variables)
formatted_prompt_template = prompt_template.format(dialect="sqlite", top_k=5)

sql_agent = create_react_agent(model, sql_tools, state_modifier=formatted_prompt_template)

result = sql_agent.invoke(
    {"messages" : [HumanMessage(content="how many customers are from USA?")]},{"recursion_limit": 100}
)
parse_agent_messages(result["messages"])


