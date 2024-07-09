import os
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
from langfuse.callback import CallbackHandler

LANGFUSE_PUBLIC_KEY = os.getenv('LANGFUSE_PUBLIC_KEY')
LANGFUSE_SECRET_KEY = os.getenv('LANGFUSE_SECRET_KEY')

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
    try:
        st.session_state['db_session_id'] = st.query_params.sessionId
    except:
        st.session_state['db_session_id'] = 'chat_session_1'
    
if 'extraction' not in st.session_state:
    st.session_state.extraction = Disturbance(disturbance_name="", disturbance_cause="", disturbance_resolution="")

if 'extraction2' not in st.session_state:
    st.session_state.extraction2 = Disturbance(disturbance_name="", disturbance_cause="", disturbance_resolution="")


rnd = random.Random()
rnd.seed(st.session_state.db_session_id) # NOTE: Of course don't use a static seed in production
random_uuid = uuid.UUID(int=rnd.getrandbits(128), version=4)
session_id = str(random_uuid)

langfuse_handler = CallbackHandler(
    public_key=LANGFUSE_PUBLIC_KEY,
    secret_key=LANGFUSE_SECRET_KEY,
    host="http://172.27.0.4:3000",
    session_id=session_id
)

config = {"callbacks":[langfuse_handler]}

history = PostgresChatMessageHistory(
    table_name,
    session_id,
    sync_connection=sync_connection,
)

st.set_page_config(
    # initial_sidebar_state="collapsed",
    layout="wide",
    page_title="Dokumentation - Assistenzsystem",
    page_icon="https://static.wikia.nocookie.net/minecraft_gamepedia/images/b/b7/Crafting_Table_JE4_BE3.png"
)

st.header("Dokumentation", anchor=False)

model = ChatOpenAI(model="gpt-3.5-turbo", temperature=0)

st.text_input("Chat Session ID", key="db_session_id")

def extractInformation():
    structured_model = model.with_structured_output(Disturbance)

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

    if len(history.get_messages()) > 1:
        st.session_state.extraction2 = runnabl2.invoke({ "history": history.get_messages() }, config=config)

    st.session_state.disturbance_name2 = st.session_state.extraction2.disturbance_name
    st.session_state.disturbance_cause2 = st.session_state.extraction2.disturbance_cause
    st.session_state.disturbance_resolution2 = st.session_state.extraction2.disturbance_resolution

st.button("Informationen extrahieren", on_click=extractInformation)
          
# st.session_state.extraction = structured_model.invoke(history.get_messages())

# Create a MessagesPlaceholder for the chat history


def submitDisturbance():
    print(st.session_state)
    query = """
        INSERT INTO disturbances (disturbance_name, disturbance_cause, disturbance_resolution)
        VALUES (%s, %s, %s)
    """
    args = [st.session_state.disturbance_name2, st.session_state.disturbance_cause2, st.session_state.disturbance_resolution2]
    cursor = conn.cursor()
    conn.autocommit = True
    cursor.execute(query, args)
    cursor.close()
    # successMessage = st.success("success")
    st.toast("Disturbance successfully added to the database!")

st.subheader("Extrahierten Informationen")
st.caption("(basierend auf Chatnachrichten inkl. Instruktionen)")
st.text_input(label="Beschreibung der Störung", key="disturbance_name2", value=st.session_state.extraction2.disturbance_name)
st.text_area(label="Grund der Störung", key="disturbance_cause2", value=st.session_state.extraction2.disturbance_cause)
st.text_area(label="Lösung der Störung", key="disturbance_resolution2", value=st.session_state.extraction2.disturbance_resolution)


col1, col2 = st.columns(2)

with col1:
    st.date_input(label="Start der Störung (Datum)")
    st.date_input(label="Ende der Störung (Datum)")

with col2:
    st.time_input(label="Start der Störung (Zeit)")
    st.time_input(label="Ende der Störung (Zeit)")

st.selectbox(label="Status", options=["Offen", "Gelöst"])

st.button("Störung dokumentieren", on_click=submitDisturbance)



