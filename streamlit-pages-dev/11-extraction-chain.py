import streamlit as st
from typing import Optional
from langchain_core.pydantic_v1 import BaseModel, Field
from langchain_core.prompts import ChatPromptTemplate, MessagesPlaceholder
from langchain_openai import ChatOpenAI

class MachineError(BaseModel):
    """Information about a person."""

    error_name: Optional[str] = Field(
        default=None, description="A short title of the error in up to 5 words"
    )
    error_code: Optional[str] = Field(
        default=None, description="The error code"
    )
    error_symptoms: Optional[str] = Field(
        default=None, description="The described symptoms of the error"
    )

# Define a custom prompt to provide instructions and any additional context.
# 1) You can add examples into the prompt template to improve extraction quality
# 2) Introduce additional parameters to take context into account (e.g., include metadata
#    about the document from which the text was extracted.)
prompt = ChatPromptTemplate.from_messages(
    [
        (
            "system",
            "You are an expert extraction algorithm. "
            "Only extract relevant information from the text. "
            "If you do not know the value of an attribute asked to extract, "
            "return null for the attribute's value.",
        ),
        # Please see the how-to about improving performance with
        # reference examples.
        # MessagesPlaceholder('examples'),
        ("human", "{text}"),
    ]
)

llm = ChatOpenAI(model="gpt-3.5-turbo", temperature=0)

runnable = prompt | llm.with_structured_output(schema=MachineError)

text = "It shows error code E11. For the machine everything excepted for the temperature. It spiked and is now in the red area. Machine is probably overheating"
print(runnable.invoke({"text": text}))