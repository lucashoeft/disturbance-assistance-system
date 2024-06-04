import os
import dotenv 

import streamlit as st
from operator import itemgetter
from langchain_openai import ChatOpenAI
from langchain.prompts import ChatPromptTemplate
from langchain.schema import StrOutputParser
from langfuse.callback import CallbackHandler

LANGFUSE_PUBLIC_KEY = os.getenv('LANGFUSE_PUBLIC_KEY')
LANGFUSE_SECRET_KEY = os.getenv('LANGFUSE_SECRET_KEY')

langfuse_handler = CallbackHandler(
    public_key=LANGFUSE_PUBLIC_KEY,
    secret_key=LANGFUSE_SECRET_KEY,
    host="http://172.18.0.4:3000"
)
 
prompt1 = ChatPromptTemplate.from_template("what is the city {person} is from?")
prompt2 = ChatPromptTemplate.from_template(
    "what country is the city {city} in? respond in {language}"

)

dotenv.load_dotenv()
OPEN_API_KEY = os.getenv('OPEN_AI_API_KEY')

model = ChatOpenAI(model_name="gpt-3.5-turbo")

chain1 = prompt1 | model | StrOutputParser()
chain2 = (
    {"city": chain1, "language": itemgetter("language")}
    | prompt2
    | model
    | StrOutputParser()
)

st.write("what is the city {person} is from? what country is the city {city} in? respond in {language}")

st.text_input(
        "Person",
        "",
        key="city",
)

st.text_input(
        "language",
        "",
        key="language",
)

def classifyError():
    st.session_state.output_text_city_lang = chain2.invoke({"person": st.session_state.city, "language": st.session_state.language}, config={"callbacks":[langfuse_handler]})

st.button("Run it!", use_container_width=True, on_click=classifyError)

if 'output_text_city_lang' not in st.session_state:
    st.session_state['output_text_city_lang'] = ""

st.write(st.session_state.output_text_city_lang)




