import os
from dotenv import load_dotenv
import streamlit as st
from langchain_core.output_parsers import StrOutputParser
from langchain_core.runnables.history import RunnableWithMessageHistory
from langchain_core.prompts import ChatPromptTemplate, MessagesPlaceholder
from langchain_community.chat_models import ChatOpenAI
from langchain_community.chat_message_histories import StreamlitChatMessageHistory

load_dotenv()

OPEN_API_KEY = os.getenv('OPEN_AI_API_KEY')

st.set_page_config(
   page_title="Störungsassistent",
   page_icon="🏭"
)

st.title("Assistenzsystem")
st.caption("Ich bin ein Wartungsassistenzsystem für das Beheben von Störungen.")

# prompt = st.text_input("Prompt Anweisung")

msgs = StreamlitChatMessageHistory(key="langchain_messages")
if len(msgs.messages) == 0:
    msgs.add_ai_message("I'm a technical assistance system, how can I help you?")

# view_messages = st.expander("View the message contents in session state")

# Set up the LangChain, passing in Message History

prompt = ChatPromptTemplate.from_messages(
    [
        ("system", "You are an technical assistance system having a conversation with a factory worker. Your name is Bob. Always ask conter questions."),
        MessagesPlaceholder(variable_name="history"),
        ("human", "{question}"),
    ]
)

chain = prompt | ChatOpenAI(api_key=OPEN_API_KEY)
chain_with_history = RunnableWithMessageHistory(
    chain,
    lambda session_id: msgs,
    input_messages_key="question",
    history_messages_key="history",
)

# Render current messages from StreamlitChatMessageHistory
for msg in msgs.messages:
    st.chat_message(msg.type).write(msg.content)

# If user inputs a new prompt, generate and draw a new response
if prompt := st.chat_input():
    st.chat_message("human").write(prompt)
    
    # new messages are saved to history automatically by Langchain during run
    config = {"configurable": {"session_id": "any"}}
    response = chain_with_history.invoke({"question": prompt}, config)
    st.chat_message("ai").write(response.content)

# Draw the messages at the end, so newly generated ones show up immediately
# with view_messages:
    # Message History initialized with:
    # msgs = StreamlitChatMessageHistory(key="langchain_messages")

    # Contents of `st.session_state.langchain_messages`:
  #  view_messages.json(st.session_state.langchain_messages)

