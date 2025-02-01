import os

from dotenv import load_dotenv

from agent.cocoa import CoCoAgent

# Load environment variables from .env file
load_dotenv()

agent = CoCoAgent(os.getenv("OPENAI_API_KEY"))

agent.run()
