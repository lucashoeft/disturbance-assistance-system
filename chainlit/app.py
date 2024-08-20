import os
import random
import time
import uuid

import dotenv
import psycopg
import chainlit as cl
import chainlit.data as cl_data
from chainlit.types import ThreadDict
from langchain.prompts import ChatPromptTemplate
from langchain.chains import create_history_aware_retriever, create_retrieval_chain
from langchain.chains.combine_documents import create_stuff_documents_chain
from langchain_core.prompts import ChatPromptTemplate, MessagesPlaceholder
from langchain_core.runnables.history import RunnableWithMessageHistory
from langchain_openai import ChatOpenAI, OpenAIEmbeddings
from langchain_postgres import PGVector
from langchain_postgres.vectorstores import PGVector
from langchain_postgres.chat_message_histories import PostgresChatMessageHistory
from langfuse.callback import CallbackHandler
from langfuse import Langfuse
from langchain.schema.runnable.config import RunnableConfig

dotenv.load_dotenv()

OPENAI_API_KEY = os.getenv("OPEN_AI_API_KEY")
LANGFUSE_PUBLIC_KEY = os.getenv("LANGFUSE_PUBLIC_KEY")
LANGFUSE_SECRET_KEY = os.getenv("LANGFUSE_SECRET_KEY")
VECTOR_DB = os.getenv("VECTOR_DB")

class UserFeedbackDataLayer(cl_data.BaseDataLayer):
    
    async def upsert_feedback(self, feedback: cl_data.Feedback) -> str:
        
        langfuse = Langfuse(
            public_key=LANGFUSE_PUBLIC_KEY,
            secret_key=LANGFUSE_SECRET_KEY,
            host="http://host.docker.internal:3000",
        )
        
        feedback_trace = langfuse.trace()
        
        feedback_trace.score(
            name="user-feedback",
            value=feedback.value,
            comment=feedback.comment
        )

cl_data._data_layer=UserFeedbackDataLayer()

@cl.on_chat_start
async def on_chat_start():

    # split with https://platform.openai.com/tokenizer
    # message = "Hallo Werker bzw. Werkerin, ich unterstütze Sie bei 
    #            Ihrer Tätigkeit in der Produktion.\n Ich verfüge 
    #            über Informationen darüber, wie man Störungen 
    #            beheben kann. Wie kann ich Ihnen weiterhelfen?"
    message_chunks = ["Hallo", " Werker", " bzw", ".", " Wer", "ker", 
                      "in", ",", " ich", " unterst", "ütze", " Sie", 
                      " bei", " Ihrer", " T", "ät", "igkeit", " in", 
                      " der", " Produ", "ktion", ".", "\n", "Ich", 
                      " ver", "fü", "ge", " über", " Informationen", 
                      " darüber", ",", " wie", " man", " St", "ör", 
                      "ungen", " be", "he", "ben", " kann", ".", 
                      " Wie", " kann", " ich", " Ihnen", " weiter", 
                      "h", "elf", "en", "?"]
    
    msg = cl.Message(content="")

    for chunk in message_chunks:
        time.sleep(0.01)
        await msg.stream_token(chunk)

    await msg.send()

    # Create session_id to store in chainlit cache
    rnd = random.Random()
    session_id = str(uuid.UUID(int=random.getrandbits(128), version=4))
    cl.user_session.set("session_id", session_id)

    # Connection to Vector DB uses psycopg3
    connection_vector_db = "postgresql+psycopg://admin:admin@postgres:5432/vectordb" 
    
    vector_store = PGVector(
        embeddings=OpenAIEmbeddings(model="text-embedding-3-large", 
                                    api_key=OPENAI_API_KEY),
        collection_name="disturbances",
        connection=connection_vector_db,
        use_jsonb=True,
    )

    retriever = vector_store.as_retriever()

    # Connection to Chat History
    connection_string = "postgresql://admin:admin@postgres:5432/chat_history"
    connection_chat_history = psycopg.connect(connection_string)
    table_name ="chat_history"

    # Create table the first time
    # PostgresChatMessageHistory.create_tables(
    #   sync_connection, 
    #   table_name
    # )

    history = PostgresChatMessageHistory(
        table_name,
        session_id,
        sync_connection=connection_chat_history
    )

    # Build RAG Chain

    contextualize_question_system_prompt = (
        "Basierend auf den Nachrichtenverlauf und der letzten "
        "Nutzereingabe welche sich eventuell auf den "
        "Nachrichtenverlauf bezieht erstelle eine eigenständige "
        "Frage, die auch ohne den Nachrichtenverlauf verstanden "
        "werden kann. Beantworte diese Frage nicht."
    )

    contextualize_quesion_prompt = ChatPromptTemplate.from_messages(
        [
            ("system", contextualize_question_system_prompt),
            MessagesPlaceholder("chat_history"),
            ("human", "{input}"),
        ]
    )

    llm = ChatOpenAI(
        model="gpt-4o-mini", 
        streaming=True, 
        api_key=OPENAI_API_KEY
    )

    history_aware_retriever = create_history_aware_retriever(
        llm, 
        retriever, 
        contextualize_quesion_prompt
    )

    system_prompt = (
        "Du bist ein Assistent zum Beantworten von Fragen zu " 
        "Störungen im Beschichtungsprozess in der Produktion von " 
        "optischen Linsen. Nutze die folgenden Kontextinformationen "
        "um darauf basierend eine Antwort zu generieren. Sage ich "
        "weiß nicht, wenn du die Frage nicht beantworten kannst. "
        "Frage nach einer Beschreibung der Situation, um mehr "
        "Informationen zu erhalten und ob die Informationen geholfen " 
        "haben. Sieze immer, also verwende Sie anstatt Du. Der "
        "Hinweis darf nicht sein die Maschine auzuschalten. Die "
        "Kontextinformationen aus den Dokumenten sind wichtiger als "
        "der Nachrichtenverlauf"
        "\n\n"
        "{context}"
    )

    question_prompt = ChatPromptTemplate.from_messages(
        [
            ("system", system_prompt),
            MessagesPlaceholder("chat_history"),
            ("human", "{input}"),
        ]
    )

    question_answer_chain = create_stuff_documents_chain(
        llm, 
        question_prompt
    )

    rag_chain = create_retrieval_chain(
        history_aware_retriever,
        question_answer_chain
    )

    conversational_rag_chain = RunnableWithMessageHistory(
        rag_chain,
        lambda session_id: history,
        input_messages_key="input",
        history_messages_key="chat_history",
        output_messages_key="answer"
    )

    cl.user_session.set("conversational_rag_chain", conversational_rag_chain)

    # Connection to Langfuse
    langfuse_handler = CallbackHandler(
        public_key=LANGFUSE_PUBLIC_KEY,
        secret_key=LANGFUSE_SECRET_KEY,
        host="http://host.docker.internal:3000",
        session_id=session_id
    )

    cl.user_session.set("langfuse_handler", langfuse_handler)

@cl.on_message
async def main(message: cl.Message):

    user_sesion_id = cl.user_session.get("session_id")
    conversational_rag_chain = cl.user_session.get("conversational_rag_chain")
    langfuse_handler = cl.user_session.get("langfuse_handler")
    
    config = RunnableConfig(
        callbacks=[langfuse_handler], 
        configurable= {
            "session_id": user_sesion_id, 
            "message_id": message.id}
    )
    
    msg = cl.Message(content="")

    for chunk in await cl.make_async(conversational_rag_chain.stream)(
        {"input": message.content},
        config=config,
    ):
        if "answer" in chunk:
            await msg.stream_token(chunk["answer"])

    await msg.send()


@cl.on_stop
def on_stop():
    print("User stopped task (text generation)")

@cl.on_chat_end
def on_chat_end():
    print("User disconnected")

@cl.on_chat_resume
async def on_chat_resume(thread: ThreadDict):
    print("User resumed chat from previous session")