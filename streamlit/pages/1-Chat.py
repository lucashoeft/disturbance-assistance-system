import os
import dotenv
import streamlit as st
from langchain.chains import create_history_aware_retriever, create_retrieval_chain
from langchain.chains.combine_documents import create_stuff_documents_chain
from langchain_core.prompts import ChatPromptTemplate, MessagesPlaceholder
from langchain_core.runnables.history import RunnableWithMessageHistory
from langchain_openai import ChatOpenAI, OpenAIEmbeddings
from langchain_postgres import PGVector
from langchain_postgres.vectorstores import PGVector
from langchain_postgres.chat_message_histories import PostgresChatMessageHistory
import uuid
import psycopg
import random
from langfuse.callback import CallbackHandler

dotenv.load_dotenv()

OPEN_API_KEY = os.getenv('OPEN_AI_API_KEY')
LANGFUSE_PUBLIC_KEY = os.getenv('LANGFUSE_PUBLIC_KEY')
LANGFUSE_SECRET_KEY = os.getenv('LANGFUSE_SECRET_KEY')

if 'db_session_id' not in st.session_state:
    try:
        st.session_state['db_session_id'] = st.query_params.sessionId
    except:
        st.session_state['db_session_id'] = 'chat_session_1'

if 'db_user_id' not in st.session_state:
    st.session_state['db_user_id'] = 'user1'

rnd = random.Random()
rnd.seed(st.session_state.db_session_id) # NOTE: Of course don't use a static seed in production
random_uuid = uuid.UUID(int=rnd.getrandbits(128), version=4)
session_id = str(random_uuid)

langfuse_handler = CallbackHandler(
    public_key=LANGFUSE_PUBLIC_KEY,
    secret_key=LANGFUSE_SECRET_KEY,
    host="http://host.docker.internal:3000",
    session_id=session_id,
    user_id=st.session_state.db_user_id
)

print(":3000")
print()

llm = ChatOpenAI(model="gpt-3.5-turbo-0125")

connection = "postgresql+psycopg://admin:admin@postgres:5432/vectordb"  # Uses psycopg3!

vectorstore = PGVector(
    embeddings=OpenAIEmbeddings(),
    collection_name="my_docs",
    connection=connection,
    use_jsonb=True,
)

retriever = vectorstore.as_retriever()

st.set_page_config(
    # initial_sidebar_state="collapsed",
    layout="wide",
    page_title="Chat - Assistenzsystem",
    page_icon="https://static.wikia.nocookie.net/minecraft_gamepedia/images/b/b7/Crafting_Table_JE4_BE3.png"
)

st.header("Chat", anchor=False)

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
    "don't know. If multiple context information seem relevant list all of them"
    "\n\n"
    "{context}"
)

# Use three sentences maximum and keep the "answer concise.

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

col1, col2 = st.columns(2)

with col1:
    text_input = st.text_input("Chat Session ID", key="db_session_id")

with col2:
    text_input = st.text_input("Nutzer ID", key="db_user_id")

# st.markdown('<button href="/?key=value" target="_self">View all</a>',unsafe_allow_html=True)

st.page_link("http://localhost:8501/Dokumentation?sessionId=" + st.session_state.db_session_id, label="Störung dokumentieren")

if len(history.messages) == 0:
    history.add_ai_message("Hey! I'm happy to answer any question you have about the machines, processes and disturbances of the production.")

for msg in history.messages:
    st.chat_message(msg.type).write(msg.content)

user_input = st.chat_input("Sende eine Nachricht an das Assistenzsystem")

if user_input:
    st.chat_message("human").write(user_input)
    
    config = {"configurable": {"session_id": session_id,}, "callbacks":[langfuse_handler]}
    
    response = conversational_rag_chain.invoke(
        {"input": user_input},
        config=config
    )

    st.chat_message("ai").write(response['answer'])