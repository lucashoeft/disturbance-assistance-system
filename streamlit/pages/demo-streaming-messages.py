import streamlit as st
from langchain_community.chat_models import ChatOpenAI
import os
from dotenv import load_dotenv
from langchain_core.output_parsers import StrOutputParser
from langchain_community.chat_message_histories import StreamlitChatMessageHistory
from langchain_core.prompts import ChatPromptTemplate, MessagesPlaceholder
from langchain_core.runnables.history import RunnableWithMessageHistory

load_dotenv()

OPEN_API_KEY = os.getenv('OPEN_AI_API_KEY')

def generate_response(input_text):
    llm = ChatOpenAI(temperature=0.7, openai_api_key=OPEN_API_KEY, model="gpt-3.5-turbo")
    
    with st.chat_message("user"):
        st.write(input_text)
    
    with st.chat_message("assistant"):
        
        parser = StrOutputParser()

        chain = llm | parser
        st.write_stream(chain.stream(input_text))

prompt = st.chat_input("Say something")
if prompt:
    generate_response(prompt)