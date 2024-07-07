from langchain.text_splitter import CharacterTextSplitter
import os
from dotenv import load_dotenv
from langchain_openai import OpenAIEmbeddings
from langchain_core.documents import Document
from langchain_postgres import PGVector
from langchain_postgres.vectorstores import PGVector
from langchain_community.document_loaders import TextLoader

load_dotenv()

OPEN_API_KEY = os.getenv('OPEN_AI_API_KEY')

connection = "postgresql+psycopg://admin:admin@localhost:5433/vectordb"  # Uses psycopg3!

vectorstore = PGVector(
    embeddings=OpenAIEmbeddings(),
    collection_name="my_docs",
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
