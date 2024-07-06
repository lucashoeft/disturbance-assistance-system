import chainlit as cl
from chainlit.types import ThreadDict
import chainlit.data as cl_data
import json

class CustomDataLayer(cl_data.BaseDataLayer):
  async def upsert_feedback(self, feedback: cl_data.Feedback) -> str:
        filename = "results.json"
        with open(filename,"r") as file:
            try:
                existing_data = json.load(file)
            except json.JSONDecodeError:
                existing_data = []
        for data in existing_data:
            # print(data)
            try:
                if data['id']==feedback.forId:
                    data['feedback']=feedback.comment
                    if feedback.value==0:
                        data['positiveORnegative']="Negative"
                    else:
                        data['positiveORnegative']="Positive"
            except:
                pass
        with open(filename, "w") as file:
            json.dump(existing_data, file, indent=4)   

from chainlit.input_widget import Select, Switch, Slider


@cl.on_chat_start
async def start():
    settings = await cl.ChatSettings(
        [
            Select(
                id="Model",
                label="OpenAI - Model",
                values=["gpt-3.5-turbo", "gpt-3.5-turbo-16k", "gpt-4", "gpt-4-32k"],
                initial_index=0,
            ),
            Switch(id="Streaming", label="OpenAI - Stream Tokens", initial=True),
            Slider(
                id="Temperature",
                label="OpenAI - Temperature",
                initial=1,
                min=0,
                max=2,
                step=0.1,
            ),
            Slider(
                id="SAI_Steps",
                label="Stability AI - Steps",
                initial=30,
                min=10,
                max=150,
                step=1,
                description="Amount of inference steps performed on image generation.",
            ),
            Slider(
                id="SAI_Cfg_Scale",
                label="Stability AI - Cfg_Scale",
                initial=7,
                min=1,
                max=35,
                step=0.1,
                description="Influences how strongly your generation is guided to match your prompt.",
            ),
            Slider(
                id="SAI_Width",
                label="Stability AI - Image Width",
                initial=512,
                min=256,
                max=2048,
                step=64,
                tooltip="Measured in pixels",
            ),
            Slider(
                id="SAI_Height",
                label="Stability AI - Image Height",
                initial=512,
                min=256,
                max=2048,
                step=64,
                tooltip="Measured in pixels",
            ),
        ]
    ).send()


@cl.on_settings_update
async def setup_agent(settings):
    print("on_settings_update", settings)

@cl.set_chat_profiles
async def chat_profile():
    return [
        cl.ChatProfile(
            name="GPT-3.5",
            markdown_description="The underlying LLM model is **GPT-3.5**.",
            icon="https://picsum.photos/200",
        ),
        cl.ChatProfile(
            name="GPT-4",
            markdown_description="The underlying LLM model is **GPT-4**.",
            icon="https://picsum.photos/250",
        ),
    ]

@cl.on_chat_start
async def on_chat_start():
    chat_profile = cl.user_session.get("chat_profile")
    await cl.Message(
        content=f"starting chat using the {chat_profile} chat profile"
    ).send()

cl_data._data_layer=CustomDataLayer()

@cl.step(type="message") 
async def tool(name: str):
    # Fake tool
    tool()
    await cl.sleep(1)
    return "Hello" + name

@cl.on_chat_start
def on_chat_start():
    print("A new chat session has started!")

@cl.on_stop
def on_stop():
    print("The user wants to stop the task!")

@cl.on_chat_end
def on_chat_end():
    print("The user disconnected!")


@cl.on_chat_resume
async def on_chat_resume(thread: ThreadDict):
    print("The user resumed a previous chat session!")

@cl.on_message  # this function will be called every time a user inputs a message in the UI
async def main(message: cl.Message):
    """
    This function is called every time a user inputs a message in the UI.
    It sends back an intermediate response from the tool, followed by the final answer.

    Args:
        message: The user's message.

    Returns:
        None.
    """
    print("hello darkness")

    response = f"Hello, you just sent: {message.content}!"
    await cl.Message(response).send()

