# https://python.langchain.com/v0.2/docs/tutorials/qa_chat_history/


# 
# not working & not understand why - probably missing packages 
# 

from langchain.agents import AgentExecutor, create_tool_calling_agent
from langchain.tools.retriever import create_retriever_tool
from langchain_community.chat_message_histories import ChatMessageHistory
from langchain_community.document_loaders import WebBaseLoader
from langchain_core.chat_history import BaseChatMessageHistory
from langchain_core.prompts import ChatPromptTemplate, MessagesPlaceholder
from langchain_core.runnables.history import RunnableWithMessageHistory
from langchain_openai import ChatOpenAI, OpenAIEmbeddings
from langchain_postgres import PGVector
from langchain_postgres.vectorstores import PGVector
from langchain.agents import AgentExecutor, create_react_agent

# from psycopg_pool import ConnectionPool
# from langchain_postgres import (
#     PostgresCheckpoint, PickleCheckpointSerializer
# )

# pool = ConnectionPool(
    # Example configuration
#    conninfo="postgresql+psycopg://admin:admin@postgres:5432/langgraph_checkpoints",
#     max_size=20,
# )

# Uses the pickle module for serialization
# Make sure that you're only de-serializing trusted data
# (e.g., payloads that you have serialized yourself).
# Or implement a custom serializer.
# checkpoint = PostgresCheckpoint(
#     serializer=PickleCheckpointSerializer(),
#    sync_connection=pool,
# )

llm = ChatOpenAI(model="gpt-3.5-turbo", temperature=0)

"""
connection = "postgresql+psycopg://admin:admin@postgres:5432/vectordb"  # Uses psycopg3!
collection_name = "my_docs"
embeddings = OpenAIEmbeddings()

vectorstore = PGVector(
    embeddings=embeddings,
    collection_name=collection_name,
    connection=connection,
    use_jsonb=True,
)
"""

retriever = vectorstore.as_retriever()


### Build retriever tool ###
tool = create_retriever_tool(
    retriever,
    "blog_post_retriever",
    "Searches and returns excerpts from the Autonomous Agents blog post.",
)
tools = [tool]

# agent_executor = create_react_agent(llm, tools, checkpointer=checkpoint)
agent_executor = create_react_agent(llm, tools, prompt="Hello")

config = {"configurable": {"thread_id": "abc123"}}

query = "What in the pond?"

for s in agent_executor.stream(
    {"messages": [HumanMessage(content=query)]}, config=config
):
    print(s)
    print("----")