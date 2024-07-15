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

    rnd = random.Random()
    # rnd.seed(st.session_state.db_session_id) # NOTE: Of course don't use a static seed in production
    random_uuid = uuid.UUID(int=rnd.getrandbits(128), version=4)
    session_id = str(random_uuid)
    
    st.session_state['db_session_id'] = session_id

print(st.session_state.db_session_id)
session_id = st.session_state.db_session_id

langfuse_handler = CallbackHandler(
    public_key=LANGFUSE_PUBLIC_KEY,
    secret_key=LANGFUSE_SECRET_KEY,
    host="http://host.docker.internal:3000",
    session_id=session_id
)

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
    # layout="wide",
    page_title="Assistenzsystem"
)

st.header("Assistenzsystem", anchor=False)

### Contextualize question ###
contextualize_q_system_prompt = (
        "Basierend auf den Nachrichtenverlauf und die letzte Nutzereingabe "
        "welche sich eventuell auf den Nachrichtenverlauf bezieht "
        "erstelle eine eigenständige Frage welche auch ohne den "
        "Nachrichtenverlauf verstanden werden kann . Beantworte diese Frage nicht"
        "formuliere sie nur um wenn nötig oder gebe sie nur aus"
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
        "Du bist ein Assistent zum Beantworten von Fragen zu Störungen "
        "im Beschichtungsprozess in der Produktion von optischen Linsen. "
        "Nutze die folgenden Kontextinformationen um darauf basierend "
        "eine Antwort zu generieren. Sage ich weiß nicht, wenn du die Frage "
        "nicht beantworten kannst. Frage nach einer Beschreibung der Situation "
        "um mehr Informationen zu erhalten. Frage jedes mal nach ob die Antwort "
        "die Störung behoben hat. Sieze immer, also verwende Sie anstatt Du."
        "Der Hinweis darf nicht sein die Maschine auzuschalten. Die Kontextinformationen "
        "aus den Dokumenten sind wichtiger als der Nachrichtenverlauf"
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

if len(history.messages) == 0:
    history.add_ai_message("Hallo Werker bzw. Werkerin, ich unterstützte Sie bei Ihrer Tätigkeit in der Produktion. \n Ich verfüge über Informationen darüber, wie man Störungen beheben kann. Wie kann ich Ihnen weiterhelfen?")

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