from flask import Flask, request, jsonify, render_template
import openai

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

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/validate_email', methods=['POST'])
def validate_email():
    data = request.get_json()
    email = data.get('email')
    if email and '@' in email:
        # Log the email or perform additional validation if necessary
        return jsonify({'valid': True})
    return jsonify({'valid': False})

@app.route('/chatbot')
def chatbot():
    return render_template('chatbot.html')

@app.route('/get_response', methods=['POST'])
def get_response():
    user_input = request.json.get('user_input')
    messages.append({"role": "user", "content": user_input})
    response = openai.ChatCompletion.create(
        model="llama-3.1-sonar-large-128k-online",
        messages=messages,
    )
    assistant_message = response.choices[0].message['content']
    messages.append({"role": "assistant", "content": assistant_message})
    return jsonify({'assistant_message': assistant_message})

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000, debug=True)
