import os
import dotenv
import uuid
import psycopg
import random
import chainlit as cl
from chainlit.types import ThreadDict
import chainlit.data as cl_data
# from langchain_community.chat_models import ChatOpenAI
from langchain.prompts import ChatPromptTemplate
from langchain.schema import StrOutputParser
from langchain.schema.runnable import Runnable
from langchain.schema.runnable.config import RunnableConfig
from langfuse.callback import CallbackHandler
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
from literalai.helper import utc_now
# from chainlit.data.sql_alchemy import SQLAlchemyDataLayer
import re

dotenv.load_dotenv()



mode = "control"
# mode = "treatment"
print(os.getenv('LITERAL_API_KEY'))
OPEN_API_KEY = os.getenv('OPEN_AI_API_KEY')
LANGFUSE_PUBLIC_KEY = os.getenv('LANGFUSE_PUBLIC_KEY')
LANGFUSE_SECRET_KEY = os.getenv('LANGFUSE_SECRET_KEY')

@cl.cache
def getChain():
    return "chain"

@cl.on_message
async def main(message: cl.Message):

    user_sesion_id = cl.user_session.get("session_id")
    print(user_sesion_id)

    langfuse_handler = CallbackHandler(
        public_key=LANGFUSE_PUBLIC_KEY,
        secret_key=LANGFUSE_SECRET_KEY,
        host="http://host.docker.internal:3000",
        session_id=user_sesion_id
    )  

    connection = "postgresql+psycopg://admin:admin@postgres:5432/vectordb"  # Uses psycopg3!

    vectorstore = PGVector(
        embeddings=OpenAIEmbeddings(),
        collection_name="my_docs",
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

    llm = ChatOpenAI(model="gpt-3.5-turbo-0125", streaming=True)

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
        user_sesion_id,
        sync_connection=sync_connection,
    )

    conversational_rag_chain = RunnableWithMessageHistory(
        rag_chain,
        lambda session_id: history,
        input_messages_key="input",
        history_messages_key="chat_history",
        output_messages_key="answer",
    )
    
    config = {"configurable": {"session_id": user_sesion_id, "message_id": message.id}, "callbacks":[langfuse_handler]}
    
    response = conversational_rag_chain.invoke(
       {"input": message.content},
       config=config
    )
    
    answer = response['answer']
    
    await cl.Message(answer).send()

class CustomDataLayer(cl_data.BaseDataLayer):
    
    async def get_user(self, identifier: str):
        return cl.PersistedUser(id="test", createdAt=now, identifier=identifier)

    async def create_user(self, user: cl.User):
        return cl.PersistedUser(id="test", createdAt=now, identifier=user.identifier)

    async def upsert_feedback(self, feedback: cl_data.Feedback) -> str:
        print(self, feedback) 

        langfuse = Langfuse(
            public_key=LANGFUSE_PUBLIC_KEY,
            secret_key=LANGFUSE_SECRET_KEY,
            host="http://host.docker.internal:3000",
        )
        
        # trace = langfuse.trace(metadata=feedback.forId)
        # bug, does only work if voting is on the latest message
        trace = langfuse.trace()
        
        trace.score(
            name="user-feedback",
            value=feedback.value,
            comment=feedback.comment
        )
        
@cl.on_settings_update
async def setup_agent(settings):
    print("on_settings_update", settings)

@cl.on_chat_start
async def on_chat_start():
    await cl.Message(
        content=f"Hallo Werker bzw. Werkerin, ich unterstützte Sie bei Ihrer Tätigkeit in der Produktion. \n Ich verfüge über Informationen darüber, wie man Störungen beheben kann. Wie kann ich Ihnen weiterhelfen?"
    ).send()

    rnd = random.Random()
    random_uuid = uuid.UUID(int=rnd.getrandbits(128), version=4)
    session_id = str(random_uuid)

    cl.user_session.set("session_id", session_id)


# cl_data._data_layer=CustomDataLayer()
# cl_data._data_layer = SQLAlchemyDataLayer(conninfo="postgresql+asyncmy://admin:admin@postgres:5432/chat_history1")

@cl.step(type="tool") 
async def tool(name: str):
    tool()
    await cl.sleep(1)
    return "Hello" + name

@cl.on_stop
def on_stop():
    print("The user wants to stop the task!")

@cl.on_chat_end
def on_chat_end():
    print("The user disconnected!")

@cl.on_chat_resume
async def on_chat_resume(thread: ThreadDict):
    print("The user resumed a previous chat session!")



