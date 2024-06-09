import streamlit as st
from dotenv import load_dotenv
from langchain_core.messages import HumanMessage
from langgraph.graph import END, MessageGraph

load_dotenv()

st.header("Langgraph")

def add_one(input: list[HumanMessage]):
    input[0].content = input[0].content + "a"
    return input

graph = MessageGraph()

graph.add_node("branch_a", add_one)
graph.add_edge("branch_a", "branch_b")
graph.add_edge("branch_a", "branch_c")

graph.add_node("branch_b", add_one)
graph.add_node("branch_c", add_one)

graph.add_edge("branch_b", "final_node")
graph.add_edge("branch_c", "final_node")

graph.add_node("final_node", add_one)
graph.add_edge("final_node", END)

graph.set_entry_point("branch_a")

runnable = graph.compile()

img1 = runnable.get_graph().draw_mermaid_png()
st.image(img1)

print(runnable.invoke("b"))