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
import json
import pickle
from datetime import datetime

# Set up logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# LangChain imports
from langchain_google_genai import ChatGoogleGenerativeAI
from langchain.chains import ConversationChain
from langchain.memory import ConversationBufferMemory, ConversationTokenBufferMemory
from langchain_community.vectorstores.redis import Redis as RedisVectorStore
from langchain.memory import VectorStoreRetrieverMemory, CombinedMemory
from redis.commands.search.field import VectorField, TagField, TextField
from redis import Redis
from sentence_transformers import SentenceTransformer
from langchain.embeddings.base import Embeddings
from langchain.prompts import PromptTemplate

# Load environment variables
current_dir = Path(__file__).parent
env_path = current_dir / '.env'
load_dotenv(env_path)

# Initialize environment variables
GOOGLE_API_KEY = os.getenv("GOOGLE_AI_STUDIO_TOKEN")
REDIS_HOST = os.getenv("REDIS_HOST", "localhost")
REDIS_PORT = int(os.getenv("REDIS_PORT", "6379"))
REDIS_PASSWORD = os.getenv("REDIS_PASSWORD", "")

if not GOOGLE_API_KEY:
    raise ValueError("GOOGLE_API_KEY not found in .env file")

# Initialize Gemini
genai_client = genai.Client(api_key=GOOGLE_API_KEY)

# Initialize Redis
redis_client = Redis(
    host=REDIS_HOST,
    port=REDIS_PORT,
    password=REDIS_PASSWORD,
    decode_responses=False  # Set to False to support binary data
)

# User management functions
def get_user_key(uid: str) -> str:
    return f"user:{uid}"

def store_user(uid: str, email: str):
    """Store user information in Redis"""
    user_key = get_user_key(uid)
    redis_client.hset(user_key, mapping={
        'uid': uid,
        'email': email,
        'created_at': str(datetime.now())
    })

def get_user(uid: str) -> Optional[Dict]:
    """Retrieve user information from Redis"""
    user_key = get_user_key(uid)
    return redis_client.hgetall(user_key)

# Initialize sentence transformer for embeddings
embedder = SentenceTransformer('all-MiniLM-L6-v2')

# Create an embedding wrapper class
class SentenceTransformerEmbeddings(Embeddings):
    def __init__(self, sentence_transformer: SentenceTransformer):
        self.transformer = sentence_transformer

    def embed_documents(self, texts: List[str]) -> List[List[float]]:
        embeddings = self.transformer.encode(texts)
        return embeddings.tolist()

    def embed_query(self, text: str) -> List[float]:
        embedding = self.transformer.encode([text])[0]
        return embedding.tolist()

# Define conversation template
template = """The following is a friendly conversation between a human and an AI assistant. The assistant has access to both recent conversation and relevant past context.

{history}
Human: {input}
Assistant: Let me think about that..."""

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

# Memory management functions
def get_memory_key(session_id: str) -> str:
    return f"memory:{session_id}"

def save_memory(session_id: str, memory: ConversationBufferMemory):
    try:
        key = get_memory_key(session_id)
        # Log current memory state
        logger.info(f"Saving memory for session {session_id}")
        logger.info(f"Memory buffer contents: {memory.buffer}")
        
        # Serialize memory buffer
        serialized_memory = pickle.dumps(memory)
        redis_client.set(key, serialized_memory)
        # Set TTL for 1 hour
        redis_client.expire(key, 3600)
    except Exception as e:
        logger.error(f"Error saving memory: {str(e)}")
        raise

def load_memory(session_id: str) -> Optional[ConversationBufferMemory]:
    try:
        key = get_memory_key(session_id)
        serialized_memory = redis_client.get(key)
        if serialized_memory:
            memory = pickle.loads(serialized_memory)
            logger.info(f"Loaded memory for session {session_id}")
            logger.info(f"Memory buffer contents: {memory.buffer}")
            return memory
        return None
    except Exception as e:
        logger.error(f"Error loading memory: {str(e)}")
        return None

def get_or_create_conversation_chain(session_id: str):
    try:
        # Try to load existing memory
        memory = load_memory(session_id)
        if not memory:
            # Create new memory if none exists
            memory = ConversationBufferMemory(
                human_prefix="Human",
                ai_prefix="Assistant",
                memory_key="history",
                input_key="input",
                return_messages=True
            )
            logger.info(f"Created new memory for session {session_id}")
        else:
            logger.info(f"Loaded existing memory for session {session_id}")

        # Initialize vector store for this session
        index_name = f"user_memory_{session_id}"
        dim = 384  # Dimension for all-MiniLM-L6-v2 embeddings
        embedding_model = SentenceTransformerEmbeddings(embedder)
        
        try:
            # Try to get existing index
            redis_client.ft(index_name).info()
            logger.info(f"Found existing index: {index_name}")
        except:
            # Index doesn't exist, create it
            logger.info(f"Creating new index: {index_name}")
            schema = [
                VectorField("embedding", "HNSW", {"TYPE": "FLOAT32", "DIM": dim, "DISTANCE_METRIC": "COSINE"}),
                TextField("content"),
                TagField("session")
            ]
            redis_client.ft(index_name).create_index(schema)

        # Set up vector store with user-specific prefix
        vector_store = RedisVectorStore(
            redis_url=f"redis://:{REDIS_PASSWORD}@{REDIS_HOST}:{REDIS_PORT}",
            index_name=index_name,
            embedding=embedding_model,
            key_prefix=f"user:{session_id}:"
        )

        # Create LangChain model
        llm = ChatGoogleGenerativeAI(
            model="gemini-2.0-flash",
            temperature=0.7,
            google_api_key=GOOGLE_API_KEY
        )

        # Create conversation chain with memory
        chain = ConversationChain(
            llm=llm,
            memory=memory,
            prompt=PROMPT,
            verbose=True
        )

        return chain, memory
    except Exception as e:
        logger.error(f"Error in get_or_create_conversation_chain: {str(e)}")
        raise

@app.post("/api/storeUser")
async def store_user_endpoint(uid: str, email: str):
    """Store user information in Redis"""
    if not uid or not email:
        raise HTTPException(status_code=400, detail="Missing uid or email")
    
    store_user(uid, email)
    return {"message": "User stored successfully"}

@app.post("/generate")
async def generate_text(request: PromptRequest):
    try:
        # Get or create session ID
        session_id = request.session_id or str(uuid.uuid4())
        logger.info(f"Processing request for session: {session_id}")
        
        # Get conversation chain and memory
        chain, memory = get_or_create_conversation_chain(session_id)
        
        # Generate response using the chain
        logger.info(f"Current memory state: {memory.buffer}")
        response = chain.predict(input=request.prompt)
        logger.info(f"Updated memory state: {memory.buffer}")
        
        # Save updated memory
        save_memory(session_id, memory)
        
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
