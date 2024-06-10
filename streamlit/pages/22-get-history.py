import streamlit as st
import psycopg
from langchain_postgres.chat_message_histories import PostgresChatMessageHistory
from langchain_core.prompts import ChatPromptTemplate, MessagesPlaceholder
from langchain_openai import ChatOpenAI
from langchain_core.pydantic_v1 import BaseModel, Field
from typing import Optional
import random
import uuid
import psycopg2

class Disturbance(BaseModel):
    disturbance_name: Optional[str] = Field(
        default=None, description="The name or description of the disturbance or the error."
    )
    disturbance_cause: Optional[str] = Field(
        default=None, description="The cause of the disturbance or the error."
    )
    disturbance_resolution: Optional[str] = Field(
        default=None, description="The resolution or solutions steps to fix the disturbance or the error."
    )

conn = psycopg2.connect(database = "postgres",
                        user = "admin",
                        password = "admin",
                        host = "postgres",
                        port = "5432")

conn_info = "postgresql://admin:admin@postgres:5432/chat_history"
sync_connection = psycopg.connect(conn_info)
table_name ="chat_history"

if 'db_session_id' not in st.session_state:
    st.session_state['db_session_id'] = '345344523424234'

if 'extraction' not in st.session_state:
    st.session_state.extraction = Disturbance(disturbance_name="", disturbance_cause="", disturbance_resolution="")

if 'extraction2' not in st.session_state:
    st.session_state.extraction2 = Disturbance(disturbance_name="", disturbance_cause="", disturbance_resolution="")


rnd = random.Random()
rnd.seed(st.session_state.db_session_id) # NOTE: Of course don't use a static seed in production
random_uuid = uuid.UUID(int=rnd.getrandbits(128), version=4)
session_id = str(random_uuid)

history = PostgresChatMessageHistory(
    table_name,
    session_id,
    sync_connection=sync_connection,
)

model = ChatOpenAI(model="gpt-3.5-turbo", temperature=0)

st.text_input("DB Session ID", key="db_session_id")

st.write(history.get_messages())

structured_model = model.with_structured_output(Disturbance)

st.session_state.extraction = structured_model.invoke(history.get_messages())

# Create a MessagesPlaceholder for the chat history
history_placeholder = MessagesPlaceholder("history")

prompt = ChatPromptTemplate.from_messages(
    [
        (
            "system",
            "You are an expert extraction algorithm. "
            "Only extract relevant information from the text. "
            "If you do not know the value of an attribute asked to extract, "
            "return null for the attribute's value.",
        ),
        history_placeholder
    ]
)

llm2 = ChatOpenAI(model="gpt-3.5-turbo", temperature=0)

runnabl2 = prompt | llm2.with_structured_output(schema=Disturbance)

st.session_state.extraction2 = runnabl2.invoke({ "history": history.get_messages() })

def submitDisturbance():
    print(st.session_state)
    query = """
        INSERT INTO disturbances (disturbance_name, disturbance_cause, disturbance_resolution)
        VALUES (%s, %s, %s)
    """
    args = [st.session_state.extraction2.disturbance_name, st.session_state.extraction2.disturbance_cause, st.session_state.extraction2.disturbance_resolution]
    cursor = conn.cursor()
    conn.autocommit = True
    cursor.execute(query, args)
    cursor.close()
    # successMessage = st.success("success")
    st.toast("Disturbance successfully added to the database!")

col1, col2 = st.columns(2)

with col1:
    st.subheader("Version 1")
    st.caption("(only chat history)")
    st.text_input(label="Disturbance Name", key="disturbance_name", value=st.session_state.extraction.disturbance_name)
    st.text_area(label="Disturbance Cause", key="disturbance_cause", value=st.session_state.extraction.disturbance_cause)
    st.text_area(label="Disturbance Resolution", key="disturbance_resolution", value=st.session_state.extraction.disturbance_resolution)

with col2:
    st.subheader("Version 2")
    st.caption("(chat history with instructions)")
    st.text_input(label="Disturbance Name", key="disturbance_name2", value=st.session_state.extraction2.disturbance_name)
    st.text_area(label="Disturbance Cause", key="disturbance_cause2", value=st.session_state.extraction2.disturbance_cause)
    st.text_area(label="Disturbance Resolution", key="disturbance_resolution2", value=st.session_state.extraction2.disturbance_resolution)
    st.button("Submit Disturbance", on_click=submitDisturbance)

    # st.text_input(label="Start", value=str(history.get_messages()[0].to_json))

# st.text_input(label="Disturbance", key="disturbance_name", value=st.session_state.extraction.disturbance_name)




