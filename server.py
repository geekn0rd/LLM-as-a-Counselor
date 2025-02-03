import logging
import os

from dotenv import load_dotenv
from fastapi import FastAPI, HTTPException, Request
from fastapi.middleware.cors import CORSMiddleware
from starlette.responses import StreamingResponse

from agent.cocoa import CoCoAgent
from prompts.structured_outputs import DialogueRequest, DialogueResponse

# Load environment variables from .env file
load_dotenv()

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

coco_agent = None
app = FastAPI()

# Add CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Allows all origins
    allow_credentials=True,
    allow_methods=["*"],  # Allows all methods
    allow_headers=["*"],  # Allows all headers
)


@app.on_event("startup")
async def startup_event():
    global coco_agent
    coco_agent = CoCoAgent(os.getenv("OPENAI_API_KEY"))
    logger.info("CoCoAgent initialized")


@app.post("/chat")
async def chat(request: Request):
    request_body = await request.json()
    messages = request_body.get("messages", [])
    message = messages[-1]
    content_list = message.get("content", [])

    dialogue = ""
    for content_item in content_list:
        if content_item.get("type") == "text":
            dialogue = content_item.get("text")

    if not coco_agent:
        raise HTTPException(status_code=500, detail="CoCoAgent not initialized")

    try:

        async def stream_response():
            for chunk in coco_agent.process_dialogue(dialogue):
                yield chunk

        return StreamingResponse(stream_response(), media_type="text/event-stream")
    except Exception as e:
        logger.error(f"Error processing dialogue: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))
