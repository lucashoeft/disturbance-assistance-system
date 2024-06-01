import streamlit as st
import os
from dotenv import load_dotenv
from langchain_openai import OpenAIEmbeddings
from langchain_core.documents import Document
from langchain_postgres import PGVector
from langchain_postgres.vectorstores import PGVector

load_dotenv()

if 'rag_output' not in st.session_state:
    st.session_state['rag_output'] = ""

OPEN_API_KEY = os.getenv('OPEN_AI_API_KEY')

# See docker command above to launch a postgres instance with pgvector enabled.
connection = "postgresql+psycopg://admin:admin@postgres:5432/vectordb"  # Uses psycopg3!
collection_name = "my_docs"
embeddings = OpenAIEmbeddings()

vectorstore = PGVector(
    embeddings=embeddings,
    collection_name=collection_name,
    connection=connection,
    use_jsonb=True,
)

def classifyError():
    out = vectorstore.similarity_search_with_score(st.session_state.rag_input, k=3)
    st.session_state.rag_output = out
    # st.text(out.content)

st.header("Simple RAG")

st.text_input(
        "Input",
        "",
        key="rag_input",
)

st.button("Get Feedback to Error", use_container_width=True, on_click=classifyError)

st.write(st.session_state.rag_output)