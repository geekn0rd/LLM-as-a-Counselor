from dotenv import load_dotenv
from fastapi import FastAPI, HTTPException
from agent.cocoa import CoCoAgent
import logging
import os
from prompts.structured_outputs import DialogueRequest, DialogueResponse

# Load environment variables from .env file
load_dotenv()

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

coco_agent = None
app = FastAPI()


@app.on_event("startup")
async def startup_event():
    global coco_agent
    coco_agent = CoCoAgent(os.getenv("OPENAI_API_KEY"))
    logger.info("CoCoAgent initialized")


@app.post("/chat", response_model=DialogueResponse)
async def chat(dialogue: DialogueRequest) -> DialogueResponse:
    """
    Process a chat message and return the assistant's response with metadata.

    Args:
        dialogue (DialogueRequest): The request containing the latest dialogue

    Returns:
        DialogueResponse: The structured response containing the assistant's reply and metadata
    """
    if not coco_agent:
        raise HTTPException(
            status_code=500,
            detail="CoCoAgent not initialized"
        )

    try:
        response = await coco_agent.process_dialogue(dialogue.latest_dialogue)
        return response
    except Exception as e:
        logger.error(f"Error processing dialogue: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))
