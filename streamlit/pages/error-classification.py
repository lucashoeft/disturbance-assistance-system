import streamlit as st
import langchain
from langchain_core.prompts import ChatPromptTemplate
from langchain_core.messages import BaseMessage
from langchain_openai import ChatOpenAI

model = ChatOpenAI()

if 'output_text' not in st.session_state:
    st.session_state['output_text'] = BaseMessage(content="", type="")

def classifyError():
    prompt = ChatPromptTemplate.from_template("{topic} The disturbance is: {disturbance}. End the output with the information that not worth risking life, talking supervisor is recommended.")
    chain = prompt | model
    out = chain.invoke({"topic": st.session_state.prompt, "disturbance": st.session_state.disturbance})
    st.session_state.output_text = out
    # st.text(out.content)

st.text_area(
        "Prompt ",
        "Classify the disturbance based on following scale: 1 is is all good, 10 is everthing is bad. Write short explanation why you think like that.",
        key="prompt",
)

st.text_input(
        "Description of Disturbance",
        "",
        key="disturbance",
)

st.button("Get Feedback to Error", use_container_width=True, on_click=classifyError)

st.write(st.session_state.output_text.content)
