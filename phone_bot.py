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
        url = "http://your-server-url.com/voice"  # Replace with your server URL
        record = True)
    
    return f"Call initiated with SID: {call.sid}"

@app.route("/voice", methods = ["POST"])
def voice():
    """Handle incoming call and respond with a message."""
    response = VoiceResponse()
    response.say("Hello! This is your phone bot. How can I assist you today?", voice = 'alice')
    
    # In a full implementation, you would use Twilio Media Streams (WebSockets) here
    # to stream the audio to your LangChain/Groq agent for real-time processing.
    # response.connect().stream(url=os.getenv("NGROK_WSS_URL") + "/stream")
    
    return str(response)

def generate_agent_response(user_input, scenario):
    """Generate a response from the agent based on user input and scenario."""
    prompt = ChatPromptTemplate.from_messages([
        ("system", f"You are a patient calling a doctor's office to {scenario}. Respond appropriately and concisely."),
        ("user", user_input)
    ])
    
    chain = prompt | llm
    return chain.invoke({"scenario": scenario, "user_input": user_input}).content

if __name__ == "__main__":
    # Run the flask app on port 5000
    app.run(port = 5000, debug = True)