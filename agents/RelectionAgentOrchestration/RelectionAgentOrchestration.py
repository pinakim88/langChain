from langchain.agents import AgentExecutor, Tool
from langchain_community.tools import WebSearchTool
from langgraph.graph import Graph, Node, Edge
from ollama import OllamaAgent

# Define the agents
class PlannerAgent(OllamaAgent):
    def __init__(self):
        super().__init__(name="PlannerAgent")

class PlanResearcherAgent(OllamaAgent):
    def __init__(self):
        super().__init__(name="PlanResearcherAgent", tools=[WebSearchTool()])

class EssayWriterAgent(OllamaAgent):
    def __init__(self):
        super().__init__(name="EssayWriterAgent")

class ReflectionAgent(OllamaAgent):
    def __init__(self, max_revisions=3):
        super().__init__(name="ReflectionAgent")
        self.max_revisions = max_revisions

    def reflect(self, draft, revision_count):
        if revision_count > self.max_revisions:
            return "Max revisions reached. Finalizing draft."
        return f"Revised Draft (Revision {revision_count}): {draft}"

# Create the agents
planner_agent = PlannerAgent()
plan_researcher_agent = PlanResearcherAgent()
essay_writer_agent = EssayWriterAgent()
reflection_agent = ReflectionAgent(max_revisions=3)

# Create the graph
graph = Graph()

# Add nodes
planner_node = Node(name="PlannerAgent", agent=planner_agent)
researcher_node = Node(name="PlanResearcherAgent", agent=plan_researcher_agent)
writer_node = Node(name="EssayWriterAgent", agent=essay_writer_agent)
reflection_node = Node(name="ReflectionAgent", agent=reflection_agent)

graph.add_node(planner_node)
graph.add_node(researcher_node)
graph.add_node(writer_node)
graph.add_node(reflection_node)

# Add edges
graph.add_edge(Edge(source=planner_node, target=researcher_node, edge_type="Normal"))
graph.add_edge(Edge(source=researcher_node, target=writer_node, edge_type="Normal"))
graph.add_edge(Edge(source=writer_node, target=reflection_node, edge_type="Conditional", condition="max_revisions"))

# Define interaction
def interact_with_planner(user_input):
    # Planner interacts with the researcher
    research_plan = planner_agent.run(user_input)
    research_results = plan_researcher_agent.run(research_plan)

    # Researcher interacts with the writer
    initial_draft = essay_writer_agent.run(research_results)

    # Writer interacts with the reflection agent
    revision_count = 0
    draft = initial_draft
    while revision_count <= reflection_agent.max_revisions:
        revised_draft = reflection_agent.reflect(draft, revision_count)
        if "Max revisions reached" in revised_draft:
            break
        draft = revised_draft
        revision_count += 1

    return draft

# Example usage
if __name__ == "__main__":
    user_input = "Create a plan for writing an essay on climate change."
    final_output = interact_with_planner(user_input)
    print("Final Output:", final_output)