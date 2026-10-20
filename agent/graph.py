from langgraph.graph import StateGraph, START, END
from agent.state import IncidentState
from agent.nodes import collect_evidence, analyze_root_cause, retrieve_history

def build_graph():
    graph = StateGraph(IncidentState)
    graph.add_node("collect_evidence", collect_evidence)
    graph.add_node("analyze_root_cause", analyze_root_cause)
    graph.add_node("retrieve_history", retrieve_history)
    graph.add_edge(START, "collect_evidence")
    graph.add_edge("collect_evidence", "analyze_root_cause")
    graph.add_edge("analyze_root_cause", "retrieve_history")
    graph.add_edge("retrieve_history", END)
    return graph.compile()

incident_graph = build_graph()
