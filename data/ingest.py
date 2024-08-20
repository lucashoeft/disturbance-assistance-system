import os

from dotenv import load_dotenv
from langchain.text_splitter import CharacterTextSplitter
from langchain_core.documents import Document
from langchain_community.document_loaders import TextLoader
from langchain_openai import OpenAIEmbeddings
from langchain_postgres import PGVector
from langchain_postgres.vectorstores import PGVector

load_dotenv()

OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")

connection = "postgresql+psycopg://admin:admin@localhost:5433/vectordb"  # Uses psycopg3

vector_store = PGVector(
    embeddings=OpenAIEmbeddings(model="text-embedding-3-large", api_key=OPENAI_API_KEY),
    collection_name="disturbances",
    connection=connection,
    use_jsonb=True,
)

text_splitter = CharacterTextSplitter(
    separator="\n\n\n",
    chunk_size=2,
    chunk_overlap=1,
    length_function=len
)

loader = TextLoader("störungen_beschichtung.txt")

for doc in loader.load():

    # Split the file in smaller text splits (based on separator character)
    texts_split = text_splitter.split_text(doc.page_content)
    
    # Create documents based on the text splits (metadata is from the original file)
    documents_split = text_splitter.create_documents(texts_split, metadatas=[doc.metadata] * len(texts_split))
    
    # Add the documents to the vector store (embeddings are created automatically)
    vector_store.add_documents(documents_split)
