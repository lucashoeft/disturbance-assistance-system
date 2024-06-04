import os
import dotenv
import streamlit as st

from langchain.chains import create_history_aware_retriever, create_retrieval_chain
from langchain.chains.combine_documents import create_stuff_documents_chain
from langchain_community.chat_message_histories import ChatMessageHistory
from langchain_community.document_loaders import WebBaseLoader
from langchain_core.chat_history import BaseChatMessageHistory
from langchain_core.prompts import ChatPromptTemplate, MessagesPlaceholder
from langchain_core.runnables.history import RunnableWithMessageHistory
from langchain_openai import ChatOpenAI, OpenAIEmbeddings
from langchain_text_splitters import RecursiveCharacterTextSplitter

from langchain_postgres import PGVector
from langchain_postgres.vectorstores import PGVector
import uuid
import psycopg

import streamlit as st 
import langchain
from langchain_postgres.chat_message_histories import PostgresChatMessageHistory
from langchain_core.messages import SystemMessage, AIMessage, HumanMessage

import os
import streamlit as st
from langchain_core.output_parsers import StrOutputParser
from langchain_core.runnables.history import RunnableWithMessageHistory
from langchain_core.prompts import ChatPromptTemplate, MessagesPlaceholder
# from langchain_community.chat_models import ChatOpenAI
from langchain_community.chat_message_histories import StreamlitChatMessageHistory
import random
from langfuse.callback import CallbackHandler
import langfuse

# https://python.langchain.com/v0.2/docs/tutorials/qa_chat_history/

dotenv.load_dotenv()

OPEN_API_KEY = os.getenv('OPEN_AI_API_KEY')
LANGFUSE_PUBLIC_KEY = os.getenv('LANGFUSE_PUBLIC_KEY')
LANGFUSE_SECRET_KEY = os.getenv('LANGFUSE_SECRET_KEY')

print(LANGFUSE_PUBLIC_KEY)

if 'db_session_id' not in st.session_state:
    st.session_state['db_session_id'] = '1'

if 'db_user_id' not in st.session_state:
    st.session_state['db_user_id'] = '1'

rnd = random.Random()
rnd.seed(st.session_state.db_session_id) # NOTE: Of course don't use a static seed in production
random_uuid = uuid.UUID(int=rnd.getrandbits(128), version=4)
session_id = str(random_uuid)

langfuse_handler = CallbackHandler(
    public_key=LANGFUSE_PUBLIC_KEY,
    secret_key=LANGFUSE_SECRET_KEY,
    host="http://172.18.0.4:3000",
    session_id=session_id,
    user_id=st.session_state.db_user_id
)

llm = ChatOpenAI(model="gpt-3.5-turbo-0125")

connection = "postgresql+psycopg://admin:admin@postgres:5432/vectordb"  # Uses psycopg3!
collection_name = "my_docs"
embeddings = OpenAIEmbeddings()

vectorstore = PGVector(
    embeddings=embeddings,
    collection_name=collection_name,
    connection=connection,
    use_jsonb=True,
)

retriever = vectorstore.as_retriever()

### Contextualize question ###
contextualize_q_system_prompt = (
    "Given a chat history and the latest user question "
    "which might reference context in the chat history, "
    "formulate a standalone question which can be understood "
    "without the chat history. Do NOT answer the question, "
    "just reformulate it if needed and otherwise return it as is."
)

contextualize_q_prompt = ChatPromptTemplate.from_messages(
    [
        ("system", contextualize_q_system_prompt),
        MessagesPlaceholder("chat_history"),
        ("human", "{input}"),
    ]
)

history_aware_retriever = create_history_aware_retriever(
    llm, retriever, contextualize_q_prompt
)

system_prompt = (
    "You are an assistant for question-answering tasks. "
    "Use the following pieces of retrieved context to answer "
    "the question. If you don't know the answer, say that you "
    "don't know. Use three sentences maximum and keep the "
    "answer concise."
    "\n\n"
    "{context}"
)

qa_prompt = ChatPromptTemplate.from_messages(
    [
        ("system", system_prompt),
        MessagesPlaceholder("chat_history"),
        ("human", "{input}"),
    ]
)

question_answer_chain = create_stuff_documents_chain(llm, qa_prompt)

rag_chain = create_retrieval_chain(history_aware_retriever, question_answer_chain)

conn_info = "postgresql://admin:admin@postgres:5432/chat_history"
sync_connection = psycopg.connect(conn_info)
table_name ="chat_history"

history = PostgresChatMessageHistory(
    table_name,
    session_id,
    sync_connection=sync_connection,
)

conversational_rag_chain = RunnableWithMessageHistory(
    rag_chain,
    lambda session_id: history,
    input_messages_key="input",
    history_messages_key="chat_history",
    output_messages_key="answer",
)

if len(history.messages) == 0:
    history.add_ai_message("I'm a technical assistance system, how can I help you?")

"""
chain_with_history = RunnableWithMessageHistory(
    chain,
    lambda session_id: history,
    input_messages_key="question",
    history_messages_key="history"
)
"""

text_input = st.text_input("DB Session ID", key="db_session_id")

text_input = st.text_input("DB User ID", key="db_user_id")


for msg in history.messages:
    st.chat_message(msg.type).write(msg.content)

user_input = st.chat_input("Say something")

if user_input:
    st.chat_message("human").write(user_input)
    
    config = {"configurable": {"session_id": session_id,}, "callbacks":[langfuse_handler]}
    
    response = conversational_rag_chain.invoke(
        {"input": user_input},
        config=config
    )

    st.chat_message("ai").write(response['answer'])