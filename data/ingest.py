import os

from dotenv import load_dotenv
from langchain.text_splitter import CharacterTextSplitter
from langchain_core.documents import Document
from langchain_community.document_loaders import TextLoader
from langchain_openai import OpenAIEmbeddings
from langchain_postgres import PGVector
from langchain_postgres.vectorstores import PGVector

load_dotenv()

OPEN_API_KEY = os.getenv('OPEN_AI_API_KEY')
VECTOR_DB = os.getenv('VECTOR_DB')

connection = VECTOR_DB  # Uses psycopg3!

vectorstore = PGVector(
    embeddings=OpenAIEmbeddings(model="text-embedding-3-large"),
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
    vectorstore.add_documents(documents_split)
