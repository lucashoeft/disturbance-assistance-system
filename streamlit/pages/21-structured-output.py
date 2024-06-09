import streamlit as st
from typing import Optional
from langchain_core.pydantic_v1 import BaseModel, Field
from langchain_openai import ChatOpenAI
import psycopg2
from psycopg2.sql import Identifier, SQL

conn = psycopg2.connect(database = "postgres",
                        user = "admin",
                        password = "admin",
                        host = "postgres",
                        port = "5432")

st.set_page_config(
   page_icon="https://static.wikia.nocookie.net/minecraft_gamepedia/images/b/b7/Crafting_Table_JE4_BE3.png"
)

hide_decoration_bar_style = '''
    <style>
         header {visibility: hidden;}
         [data-testid="stSidebarCollapseButton"] {visibility: hidden;}
    </style>
'''
st.markdown(hide_decoration_bar_style, unsafe_allow_html=True)

st.logo("https://static.wikia.nocookie.net/minecraft_gamepedia/images/b/b7/Crafting_Table_JE4_BE3.png")

class Disturbance(BaseModel):
    disturbance_name: Optional[str] = Field(
        default=None, description="The name or description of the disturbance or error."
    )

model = ChatOpenAI(model="gpt-3.5-turbo", temperature=0)
structured_llm = model.with_structured_output(Disturbance)


import os
from langfuse.callback import CallbackHandler

LANGFUSE_PUBLIC_KEY = os.getenv('LANGFUSE_PUBLIC_KEY')
LANGFUSE_SECRET_KEY = os.getenv('LANGFUSE_SECRET_KEY')

langfuse_handler = CallbackHandler(
    public_key=LANGFUSE_PUBLIC_KEY,
    secret_key=LANGFUSE_SECRET_KEY,
    host="http://172.20.0.4:3000"
)

config = {"callbacks":[langfuse_handler]}

st.header("New Disturbance", anchor=False)

st.text_area("Error Description", key="disturbance_text")

if 'extraction' not in st.session_state:
    st.session_state.extraction = Disturbance(disturbance_name="")

if 'disturbance_name' not in st.session_state:
    st.session_state.disturbance_name = ""

def click_extraction():
    st.session_state.extraction = structured_llm.invoke(st.session_state.disturbance_text, config=config)

st.button('Click me', on_click=click_extraction)

# st.write()
st.divider()

st.text_input(label="Disturbance", key="disturbance_name", value=st.session_state.extraction.disturbance_name)

col1, col2 = st.columns(2)

with col1:
    st.date_input(label="Start Point")

with col2:
    st.time_input(label="Start Point")

import time

def submitDisturbance():
    print(st.session_state)
    query = """
        INSERT INTO disturbances (disturbance_name)
        VALUES (%s)
    """
    args = [st.session_state.disturbance_name]
    cursor = conn.cursor()
    conn.autocommit = True
    cursor.execute(query, args)
    cursor.close()
    # successMessage = st.success("success")
    # st.toast("Disturbance successfully added to the database!")

st.button("Submit Disturbance", on_click=submitDisturbance)





