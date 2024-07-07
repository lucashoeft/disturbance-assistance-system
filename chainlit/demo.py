import chainlit as cl
from chainlit.types import ThreadDict
import chainlit.data as cl_data
import json
import os
from langchain_community.chat_models import ChatOpenAI
from langchain.prompts import ChatPromptTemplate
from langchain.schema import StrOutputParser
from langchain.schema.runnable import Runnable
from langchain.schema.runnable.config import RunnableConfig
from chainlit.input_widget import Select, Switch, Slider
from langfuse.callback import CallbackHandler
import os
import dotenv
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
from langfuse import Langfuse

dotenv.load_dotenv()

OPEN_API_KEY = os.getenv('OPEN_AI_API_KEY')
LANGFUSE_PUBLIC_KEY = os.getenv('LANGFUSE_PUBLIC_KEY')
LANGFUSE_SECRET_KEY = os.getenv('LANGFUSE_SECRET_KEY')

rnd = random.Random()
rnd.seed("chat_session_1") # NOTE: Of course don't use a static seed in production
random_uuid = uuid.UUID(int=rnd.getrandbits(128), version=4)
session_id = str(random_uuid)

langfuse_handler = CallbackHandler(
    public_key=LANGFUSE_PUBLIC_KEY,
    secret_key=LANGFUSE_SECRET_KEY,
    host="http://host.docker.internal:3000",
    session_id='chat_session_1',
    user_id='user1'
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

config = {"configurable": {"session_id": session_id,}, "callbacks":[langfuse_handler]}
    
@cl.on_message
async def main(message: cl.Message):

    model = ChatOpenAI(streaming=True)
    
    config = {"configurable": {"session_id": 1,}, "callbacks":[langfuse_handler]}
    
    response = conversational_rag_chain.invoke(
        {"input": message.content},
        config=config
    )

    await cl.Message(response['answer']).send()

# dotenv.load_dotenv()
# OPEN_API_KEY = os.getenv('OPEN_AI_API_KEY')
# LANGFUSE_PUBLIC_KEY = os.getenv('LANGFUSE_PUBLIC_KEY')
# LANGFUSE_SECRET_KEY = os.getenv('LANGFUSE_SECRET_KEY')

class CustomDataLayer(cl_data.BaseDataLayer):
  async def upsert_feedback(self, feedback: cl_data.Feedback) -> str:
        print(self, feedback) 

        langfuse = Langfuse(
            public_key=LANGFUSE_PUBLIC_KEY,
            secret_key=LANGFUSE_SECRET_KEY,
            host="http://host.docker.internal:3000",
        )
        
        trace = langfuse.trace(name = "llm-feature")

        trace.score(
            name="user-explicit-feedback",
            value=feedback.value,
            comment=feedback.comment,
        )
        
@cl.on_settings_update
async def setup_agent(settings):
    print("on_settings_update", settings)

@cl.on_chat_start
async def on_chat_start():
    chat_profile = cl.user_session.get("chat_profile")
    await cl.Message(
        content=f"Hey Buddy, chat using the {chat_profile} chat profile"
    ).send()

    model = ChatOpenAI(streaming=True)
    prompt = ChatPromptTemplate.from_messages(
        [
            (
                "system",
                "You're a very knowledgeable historian who provides accurate and eloquent answers to historical questions.",
            ),
            ("human", "{question}"),
        ]
    )
    runnable = prompt | model | StrOutputParser()

    

    cl.user_session.set("runnable", runnable)


cl_data._data_layer=CustomDataLayer()

@cl.step(type="message") 
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



