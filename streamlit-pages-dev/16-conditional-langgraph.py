import streamlit as st
from dotenv import load_dotenv
from langchain_core.messages import HumanMessage
from langgraph.graph import END, MessageGraph


load_dotenv()

st.header("Conditional Langgraph")

def entry(input: list[HumanMessage]):
    return input

def work_with_b(input: list[HumanMessage]):
    print("Using branch B")
    return input

def work_with_c(input: list[HumanMessage]):
    print("Using branch C")
    return input

def router(input: list[HumanMessage]):
    if "use_b" in input[0].content:
        return "branch_b"
    else:
        return "branch_c"
    
graph = MessageGraph()

graph.add_node("branch_a", entry)
graph.add_node("branch_b", work_with_b)
graph.add_node("branch_c", work_with_c)

graph.add_conditional_edges(
    "branch_a",
    router,
    {
        "branch_b": "branch_b",
        "branch_c": "branch_c"
    }
)

graph.add_edge("branch_b", END)
graph.add_edge("branch_c", END)

graph.set_entry_point("branch_a")

runnable = graph.compile()

img1 = runnable.get_graph().draw_mermaid_png()
st.image(img1)

res = runnable.invoke("hello")
st.write(res)