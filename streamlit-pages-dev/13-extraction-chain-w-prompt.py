import streamlit as st
from langchain_openai import ChatOpenAI

model = ChatOpenAI(model="gpt-3.5-turbo")

from typing import List, Optional

from langchain_core.output_parsers import PydanticOutputParser
from langchain_core.prompts import ChatPromptTemplate
from langchain_core.pydantic_v1 import BaseModel, Field, validator


class Person(BaseModel):
    """Information about a person."""

    name: str = Field(..., description="The name of the person")
    height_in_meters: Optional[float] = Field(
        ..., description="The height of the person expressed in meters."
    )


class People(BaseModel):
    """Identifying information about all people in a text."""

    people: List[Person]


# Set up a parser
parser = PydanticOutputParser(pydantic_object=People)

# Prompt
prompt = ChatPromptTemplate.from_messages(
    [
        (
            "system",
            "Answer the user query. Wrap the output in `json` tags\n{format_instructions}",
        ),
        ("human", "{query}"),
    ]
).partial(format_instructions=parser.get_format_instructions())

chain = prompt | model | parser

# prompt.format_prompt(query=query).to_string()

if 'output_text_extraction_with_prompt' not in st.session_state:
    st.session_state['output_text_extraction_with_prompt'] = ""

def invokeQuery():
    query = st.session_state.query_text
    res = chain.invoke({"query": query})
    st.session_state.output_text_extraction_with_prompt = res

st.text_input("Query Text", "", key="query_text")

st.button("Extract Chain [Name & Height (Optional)]", use_container_width=True, on_click=invokeQuery)

st.code(st.session_state.output_text_extraction_with_prompt)