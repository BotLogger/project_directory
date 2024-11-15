# Install required packages
!pip install openai gradio

from openai import OpenAI
import gradio as gr
from datetime import datetime, timedelta
import os

YOUR_API_KEY = "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"
client = OpenAI(api_key=YOUR_API_KEY, base_url="https://api.perplexity.ai")

# Settings for cost management
MAX_TOKENS = 450  # Set maximum tokens per response
DAILY_REQUEST_LIMIT = 10  # Set a daily request limit
request_count = 0
reset_time = datetime.now() + timedelta(days=1)

# Log file path
LOG_DIR = "/home/your_user/data"  # Update this path to your server directory
LOG_FILE = os.path.join(LOG_DIR, "email_log.txt")

# Ensure the directory exists
os.makedirs(LOG_DIR, exist_ok=True)

# Initialize chat history
messages = [
    {
        "role": "system",
        "content": (
            "You are an artificial intelligence assistant and need to engage in a helpful, polite conversation. "
            "All your responses are precise and efficient."
        ),
    },
]

# Function to handle responses
def respond(user_input, chat_history):
    global request_count, reset_time

    # Check if daily request limit has been reached
    if datetime.now() >= reset_time:
        request_count = 0  # Reset count after 24 hours
        reset_time = datetime.now() + timedelta(days=1)

    if request_count >= DAILY_REQUEST_LIMIT:
        assistant_message = "Daily request limit reached. Please try again tomorrow."
        chat_history.append((user_input, assistant_message))
        return "", chat_history, chat_history

    # Append user message
    messages.append({"role": "user", "content": user_input})

    # Make API call with max_tokens limit
    response = client.chat.completions.create(
        model="llama-3.1-sonar-small-128k-online",
        messages=messages,
        max_tokens=MAX_TOKENS  # Limit response length
    )

    # Retrieve and store assistant's response
    assistant_message = response.choices[0].message.content
    messages.append({"role": "assistant", "content": assistant_message})
    chat_history.append((user_input, assistant_message))

    # Increment request count
    request_count += 1

    # Return values for Gradio
    return "", chat_history, chat_history

# Function to verify email input, log email, and grant access
def verify_email(email, verified):
    if "@" in email and "." in email:
        # Log the email to a file
        with open(LOG_FILE, "a") as file:
            file.write(f"{email}, {datetime.now()}\n")

        # Set verified state to True
        return "Access granted! You may now chat with the assistant.", gr.update(visible=False), gr.update(visible=True), True
    else:
        return "Invalid email format. Please enter a valid email to continue.", gr.update(visible=True), gr.update(visible=False), verified

# Gradio interface setup
iface = gr.Blocks()

with iface:
    gr.Markdown("# VirtualDom Chatbot\nPlease enter your email to gain access to the chatbot.")

    # Email input dialog box
    with gr.Column(visible=True, elem_id="email_box") as email_box:
        email_input = gr.Textbox(placeholder="Enter your email...", label="Email")
        verify_button = gr.Button("Verify Email")
        email_status = gr.Markdown()  # Display email verification status

    # Chatbot interface, initially hidden until email verification
    with gr.Column(visible=False, elem_id="chat_box") as chat_box:
        chat_display = gr.Chatbot(label="Conversation")
        user_input = gr.Textbox(lines=2, placeholder="Enter your message here...", label="Your Input")
        submit_button = gr.Button("Send")
        state = gr.State([])  # Initial state to store chat history

    # State to track verification status (True if email is verified in the session)
    verified = gr.State(False)

    # Use Gradio’s load function to check if verification status is True
    iface.load(lambda verified: (gr.update(visible=not verified), gr.update(visible=verified)), inputs=verified, outputs=[email_box, chat_box])

    # Link email verification to update visibility, log email, and set verified state
    verify_button.click(verify_email, inputs=[email_input, verified], outputs=[email_status, email_box, chat_box, verified])

    # Link chatbot response after email verification
    submit_button.click(respond, [user_input, state], [user_input, chat_display, state])

# Launch interface on the server
iface.launch(server_name="0.0.0.0", server_port=8080)
