import uuid
import psycopg

import streamlit as st 
import langchain
# import langchain_postgres
# from langchain_community.chat_message_histories import PostgresChatMessageHistory
from langchain_postgres.chat_message_histories import PostgresChatMessageHistory
from langchain_core.messages import SystemMessage, AIMessage, HumanMessage

import os
from dotenv import load_dotenv
import streamlit as st
from langchain_core.output_parsers import StrOutputParser
from langchain_core.runnables.history import RunnableWithMessageHistory
from langchain_core.prompts import ChatPromptTemplate, MessagesPlaceholder
from langchain_community.chat_models import ChatOpenAI
from langchain_community.chat_message_histories import StreamlitChatMessageHistory

load_dotenv()

OPEN_API_KEY = os.getenv('OPEN_AI_API_KEY')

# postgresql+psycopg://admin:admin@localhost:5433/vectordb
# postgresql://admin:admin@0.0.0.0:5433/chat_history

conn_info = "postgresql://admin:admin@postgres:5432/chat_history"

sync_connection = psycopg.connect(conn_info)

table_name ="chat_history"
PostgresChatMessageHistory.create_tables(sync_connection, table_name)

import random
import uuid

rnd = random.Random()

if 'db_session_id' not in st.session_state:
    st.session_state['db_session_id'] = '1'
    
rnd.seed(st.session_state.db_session_id) # NOTE: Of course don't use a static seed in production

random_uuid = uuid.UUID(int=rnd.getrandbits(128), version=4)

session_id = str(random_uuid)
# session_id = str(uuid.uuid4())

history = PostgresChatMessageHistory(
    table_name,
    session_id,
    sync_connection=sync_connection,
)

if len(history.messages) == 0:
    history.add_ai_message("I'm a technical assistance system, how can I help you?")

prompt = ChatPromptTemplate.from_messages(
    [
        ("system", "You are an technical assistance system having a conversation with a factory worker. Your name is Bob. Always ask conter questions."),
        MessagesPlaceholder(variable_name="history"),
        ("human", "{question}"),
    ]
)

chain = prompt | ChatOpenAI(api_key=OPEN_API_KEY)

chain_with_history = RunnableWithMessageHistory(
    chain,
    lambda session_id: history,
    input_messages_key="question",
    history_messages_key="history"
)

text_input = st.text_input(
        "DB Session ID",
        key="db_session_id"
    )

for msg in history.messages:
    st.chat_message(msg.type).write(msg.content)

prompt = st.chat_input("Say something")
if prompt:

    st.chat_message("human").write(prompt)
    
    # new messages are saved to history automatically by Langchain during run
    config = {"configurable": {"session_id": session_id}}
    response = chain_with_history.invoke({"question": prompt}, config)
    st.chat_message("ai").write(response.content)

    # message streaming (issues with profile pictures)
    # with st.chat_message("ai"):
    #     response1 = chain_with_history.stream({"question": prompt}, config)
    #     st.write_stream(response1)