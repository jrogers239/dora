from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
import os
from dotenv import load_dotenv
from google import genai
from pathlib import Path
from typing import Optional, List, Dict, Any
import uuid
import logging
from datetime import datetime

# Set up logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# LangChain imports
from langchain_google_genai import ChatGoogleGenerativeAI
from langchain.chains import ConversationChain
from langchain.memory import ConversationBufferMemory
from langchain.prompts import PromptTemplate

# Load environment variables
current_dir = Path(__file__).parent
env_path = current_dir / '.env'
load_dotenv(env_path)

# Initialize environment variables
GOOGLE_API_KEY = os.getenv("GOOGLE_AI_STUDIO_TOKEN")

if not GOOGLE_API_KEY:
    raise ValueError("GOOGLE_API_KEY not found in .env file")

# Initialize Gemini
genai_client = genai.Client(api_key=GOOGLE_API_KEY)

# Define conversation template
template = """The following is a friendly conversation between a human and an AI assistant.

Current conversation:
{history}
Human: {input}"""

PROMPT = PromptTemplate(
    input_variables=["history", "input"],
    template=template
)

app = FastAPI()

# Configure CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

class PromptRequest(BaseModel):
    prompt: str
    max_length: int = 100
    session_id: Optional[str] = None

# Memory store for active sessions
memory_store: Dict[str, ConversationBufferMemory] = {}

def get_or_create_conversation_chain(session_id: str):
    """Get or create a conversation chain for a user"""
    try:
        # Get or create memory
        if session_id not in memory_store:
            memory_store[session_id] = ConversationBufferMemory(
                memory_key="history",
                return_messages=True
            )
        
        memory = memory_store[session_id]
        
        # Create LLM
        llm = ChatGoogleGenerativeAI(
            model="gemini-2.0-flash",
            temperature=0.7,
            google_api_key=GOOGLE_API_KEY
        )
        
        # Create chain
        chain = ConversationChain(
            llm=llm,
            memory=memory,
            prompt=PROMPT,
            verbose=True
        )
        
        return chain
    except Exception as e:
        logger.error(f"Error creating conversation chain: {str(e)}")
        raise

@app.post("/generate")
async def generate_text(request: PromptRequest):
    try:
        # Get or create session ID
        session_id = request.session_id or str(uuid.uuid4())
        logger.info(f"Processing request for session: {session_id}")
        
        # Get conversation chain
        chain = get_or_create_conversation_chain(session_id)
        
        # Generate response
        response = chain.predict(input=request.prompt)
        
        return {
            "generated_text": response,
            "session_id": session_id
        }
    except Exception as e:
        logger.error(f"Error processing request: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000, log_level="info")
