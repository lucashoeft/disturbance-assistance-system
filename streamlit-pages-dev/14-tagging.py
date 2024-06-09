import streamlit as st

from langchain_core.prompts import ChatPromptTemplate
from langchain_core.pydantic_v1 import BaseModel, Field
from langchain_openai import ChatOpenAI

tagging_prompt = ChatPromptTemplate.from_template(
    """
Extract the desired information from the following passage.

Only extract the properties mentioned in the 'Classification' function.

Passage:
{input}
"""
)

class Classification(BaseModel):
    sentiment: str = Field(description="The sentiment of the text")
    aggressiveness: int = Field(
        description="How aggressive the text is on a scale from 1 to 10"
    )
    language: str = Field(description="The language the text is written in")


# LLM
llm = ChatOpenAI(temperature=0, model="gpt-3.5-turbo").with_structured_output(
    Classification
)

tagging_chain = tagging_prompt | llm

inp = "Estoy increiblemente contento de haberte conocido! Creo que seremos muy buenos amigos!"
res = tagging_chain.invoke({"input": inp})
print(res)
print("")
print(res.dict())


class Classification2(BaseModel):
    sentiment: str = Field(..., enum=["happy", "neutral", "sad"])
    aggressiveness: int = Field(
        ...,
        description="describes how aggressive the statement is, the higher the number the more aggressive",
        enum=[1, 2, 3, 4, 5],
    )
    language: str = Field(
        ..., enum=["spanish", "english", "french", "german", "italian"]
    )

tagging_prompt2 = ChatPromptTemplate.from_template(
    """
Extract the desired information from the following passage.

Only extract the properties mentioned in the 'Classification' function.

Passage:
{input}
"""
)

llm2 = ChatOpenAI(temperature=0, model="gpt-3.5-turbo").with_structured_output(
    Classification2
)

chain2 = tagging_prompt2 | llm2

inp2 = "Estoy increiblemente contento de haberte conocido! Creo que seremos muy buenos amigos!"
res = chain2.invoke({"input": inp})


st.write(res)

