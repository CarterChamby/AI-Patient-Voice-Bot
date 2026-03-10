import base64
import json
import os
from flask import Flask, request
from twilio.rest import Client
from twilio.twiml.voice_response import VoiceResponse
from langchain_groq import ChatGroq
from langchain_core.prompts import ChatPromptTemplate
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()

app = Flask(__name__) # Initialize Flask app
sock = Sock(app) # Initialize Flask-Sock for WebSocket support

# Initialize API clients
twilio_client = Client(os.getenv("TWILIO_ACCOUNT_SID"), os.getenv("TWILIO_AUTH_TOKEN"))
groq_client = ChatGroq(model="mixtral-8x7b-32768", temperature=0)

# Test number for the bot to call
TEST_NUMBER = "+18054398008"

@app.route("/call", methods = ["GET"])
def make_call():
    """Initiate a call to the test number."""
    call = twilio_client.calls.create(
        to = TEST_NUMBER,
        from_ = os.getenv("TWILIO_PHONE_NUMBER"),
        url = "http://your-server-url.com/voice",  # Replace with your server URL
        record = True)
    
    return f"Call initiated with SID: {call.sid}"

@app.route("/voice", methods = ["POST"])
def voice():
    """Handle incoming call and respond with a message."""
    response = VoiceResponse()
    response.say("Hello, I am calling to schedule an appointment.", voice = 'alice')
    
    # Connect Twilio's audio to the WebSocket stream
    connect = Connect()
    connect.stream(url=os.getenv("NGROK_WSS_URL") + "/stream")
    response.append(connect)

    return str(response)
@sock.route("/stream")
def stream(ws):
    """Handle the audio stream with Twilio."""
    print("WebSocket connection open!")
    stream_sid = None

    while True:
        # Listen for messages
        message = ws.receive()
        if message is None:
            print("WebSocket connection closed!")
            break

        data = json.loads(message)

        # Handle the different types of stream events
        if data["event"] == "start":
            stream_sid = data["start"]["streamSid"]
            print(f"Stream started with SID: {stream_sid}")

        elif data["event"] == "media":
            # capture the raw audio bytes from the AI agent
            audio_chunk = data["media"]["payload"]
            # we have to decode the audio chunk from base64 to raw bytes before sending it to the agent
            audio_bytes = base64.b64decode(audio_chunk)

            # ------ THIS IS THE AI's BRAIN ------
            # TODO: send audio_bytes to a speech-to-text model to get the transcribed text
            # TODO: pass the trascription to Groq
            # TODO: send Groq's response to a text-to-speech model to get the audio response bytes
            # TODO: encode the TTS audio back to base64 and send it to Twilio
            
        elif data["event"] == "stop":
            print(f"Stream stopped with SID: {stream_sid}")
            break


def generate_agent_response(user_input, scenario):
    """Generate a response from the agent based on user input and scenario."""
    prompt = ChatPromptTemplate.from_messages([
        ("system", f"You are a patient calling a doctor's office to {scenario}. Respond appropriately and concisely."),
        ("user", user_input)
    ])
    
    chain = prompt | groq_client
    return chain.invoke({"scenario": scenario, "user_input": user_input}).content

if __name__ == "__main__":
    # Run the flask app on port 5000
    app.run(port = 5000, debug = True)