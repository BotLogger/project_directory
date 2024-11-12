from flask import Flask, request, jsonify, render_template
import openai
import gradio as gr

app = Flask(__name__)

# Replace with your Perplexity API key
YOUR_API_KEY = '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'

# Initialize the OpenAI client with Perplexity's API key and base URL
openai.api_key = YOUR_API_KEY
openai.api_base = 'https://api.perplexity.ai'

# Initialize conversation history
messages = [
    {
        "role": "system",
        "content": (
            "You are an artificial intelligence assistant and you need to "
            "engage in a helpful, detailed, polite conversation with a user."
        ),
    },
]

def respond(user_input, chat_history):
    messages.append({"role": "user", "content": user_input})
    response = openai.ChatCompletion.create(
        model="llama-3.1-sonar-large-128k-online",
        messages=messages,
    )
    assistant_message = response.choices[0].message['content']
    messages.append({"role": "assistant", "content": assistant_message})
    chat_history.append((user_input, assistant_message))
    return "", chat_history

# Define the Gradio interface
with gr.Blocks() as demo:
    gr.Markdown("# AI Assistant Chatbot")
    chatbot = gr.Chatbot()
    with gr.Row():
        with gr.Column(scale=0.85):
            txt = gr.Textbox(
                show_label=False,
                placeholder="Enter your message...",
            ).style(container=False)
        with gr.Column(scale=0.15, min_width=0):
            btn = gr.Button("Send")
    btn.click(respond, [txt, chatbot], [txt, chatbot])

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/chatbot')
def chatbot_page():
    return demo.launch(share=False, inline=True)

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000, debug=True)
