import gradio as gr
import random

def alternatingly_agree(message, history):
    if len(history) % 2 == 0:
        return f"Yes, I do think that '{message}'"
    else:
        return "I don't think so"

def greet(name):
    return f"Hello Mr {name}!"

with gr.Blocks(css="footer{display:none !important}") as demo:
    iface = gr.Interface(fn=greet, inputs="text", outputs="text").launch()

    chatbot = gr.ChatInterface(alternatingly_agree).launch()
    # chatbot.like
    # chatbot.like(None, None, None)

    chat1 = gr.Chatbot()
    chat1.like(None, None, None)

if __name__ == "__main__":
    demo.launch()