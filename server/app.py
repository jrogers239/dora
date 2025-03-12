from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
import os
from dotenv import load_dotenv
from google import genai
from pathlib import Path
from typing import Optional
import uuid

# LangChain imports
from langchain_google_genai import ChatGoogleGenerativeAI
from langchain.chains import ConversationChain
from langchain.memory import ConversationBufferMemory
from langchain_community.vectorstores.redis import Redis as RedisVectorStore
from langchain.memory import VectorStoreRetrieverMemory
from redis.commands.search.field import VectorField, TagField, TextField
from redis import Redis
from sentence_transformers import SentenceTransformer

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
genai.configure(api_key=GOOGLE_API_KEY)

# Initialize Redis
redis_client = Redis(
    host=REDIS_HOST,
    port=REDIS_PORT,
    password=REDIS_PASSWORD,
    decode_responses=True
)

# Initialize sentence transformer for embeddings
embedder = SentenceTransformer('all-MiniLM-L6-v2')

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

def get_or_create_conversation_chain(session_id: str):
    # Initialize vector store for this session
    index_name = f"chat_history_{session_id}"
    dim = 384  # Dimension for all-MiniLM-L6-v2 embeddings
    
    try:
        # Try to create the index
        redis_client.ft(index_name).info()
    except:
        # Index doesn't exist, create it
        schema = [
            VectorField("embedding", "HNSW", {"TYPE": "FLOAT32", "DIM": dim, "DISTANCE_METRIC": "COSINE"}),
            TextField("content"),
            TagField("session")
        ]
        redis_client.ft(index_name).create_index(schema)

    # Set up vector store
    vector_store = RedisVectorStore(
        redis_url=f"redis://:{REDIS_PASSWORD}@{REDIS_HOST}:{REDIS_PORT}",
        index_name=index_name,
        embedding_function=embedder.encode
    )

    # Create memory with vector store
    memory = VectorStoreRetrieverMemory(
        retriever=vector_store.as_retriever(),
        memory_key="chat_history"
    )

    # Create LangChain model
    llm = ChatGoogleGenerativeAI(
        model="gemini-pro",  # Changed from gemini-2.0-flash to gemini-pro
        temperature=0.7
    )

    # Create conversation chain
    chain = ConversationChain(
        llm=llm,
        memory=memory,
        verbose=True
    )

    return chain

@app.post("/generate")
async def generate_text(request: PromptRequest):
    try:
        # Get or create session ID
        session_id = request.session_id or str(uuid.uuid4())
        
        # Get conversation chain for this session
        chain = get_or_create_conversation_chain(session_id)
        
        # Generate response using the chain
        response = chain.run(request.prompt)
        
        return {
            "generated_text": response,
            "session_id": session_id
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

if __name__ == "__main__":
    import uvicorn
