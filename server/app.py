from fastapi import FastAPI, HTTPException, Header
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
import firebase_admin
from firebase_admin import credentials, auth
from sentence_transformers import SentenceTransformer
from qdrant_client import QdrantClient
from qdrant_client.http.models import Distance, VectorParams, PointStruct
from langchain_core.memory import BaseMemory
from langchain.schema import BaseMessage, HumanMessage, AIMessage
from langchain.prompts import PromptTemplate
from langchain_google_genai import ChatGoogleGenerativeAI
from langchain.chains import ConversationChain

# Set up logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Load environment variables
current_dir = Path(__file__).parent
env_path = current_dir / '.env'
load_dotenv(env_path)

# Initialize environment variables
GOOGLE_API_KEY = os.getenv("GOOGLE_AI_STUDIO_TOKEN")
QDRANT_URL = os.getenv("QDRANT_URL", "http://localhost:6333")
FIREBASE_CREDENTIALS = os.getenv("FIREBASE_CREDENTIALS_PATH")

if not all([GOOGLE_API_KEY, FIREBASE_CREDENTIALS]):
    raise ValueError("Missing required environment variables")

# Initialize Firebase Admin
firebase_cred_path = current_dir / FIREBASE_CREDENTIALS.replace('./', '')
cred = credentials.Certificate(str(firebase_cred_path))
firebase_admin.initialize_app(cred)

# Initialize Qdrant
qdrant_client = QdrantClient(url=QDRANT_URL)
COLLECTION_NAME = "user_messages"
VECTOR_SIZE = 768

# Initialize sentence transformer for embeddings
encoder = SentenceTransformer('all-MiniLM-L6-v2')

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

class QdrantMemory(BaseMemory):
    user_id: str
    k: int = 5
    return_messages: bool = True
    
    def __init__(self, user_id: str, k: int = 5):
        super().__init__()
        self.user_id = user_id
        self.k = k
        self.return_messages = True
        self.memory_key = "history"

    @property
    def memory_variables(self) -> List[str]:
        return ["history"]

    def get_relevant_messages(self, query: str) -> List[BaseMessage]:
        vector = encoder.encode(query)
        results = qdrant_client.search(
            collection_name=COLLECTION_NAME,
            query_vector=vector.tolist(),
            query_filter={"must": [{"key": "user_id", "match": {"value": self.user_id}}]},
            limit=self.k
        )
        messages = []
        for result in results:
            role = result.payload["role"]
            content = result.payload["content"]
            messages.append(
                HumanMessage(content=content) if role == "human"
                else AIMessage(content=content)
            )
        return messages

    def load_memory_variables(self, inputs: Dict[str, Any]) -> Dict[str, Any]:
        query = inputs.get("input", "")
        relevant_messages = self.get_relevant_messages(query)
        messages_str = "\n".join(f"{'Human' if isinstance(m, HumanMessage) else 'Assistant'}: {m.content}" 
                               for m in relevant_messages)
        return {"history": messages_str}

    def save_context(self, inputs: Dict[str, Any], outputs: Dict[str, str]) -> None:
        input_str = inputs.get("input", "")
        output_str = outputs.get("response", "") or outputs.get("output", "")
        
        # Save messages to vector store
        for msg, role in [(input_str, "human"), (output_str, "assistant")]:
            if msg.strip():  # Only store non-empty messages
                vector = encoder.encode(msg)
                point = PointStruct(
                    id=str(uuid.uuid4()),
                    vector=vector.tolist(),
                    payload={
                        "user_id": self.user_id,
                        "content": msg,
                        "role": role,
                        "timestamp": datetime.utcnow().isoformat()
                    }
                )
                qdrant_client.upsert(collection_name=COLLECTION_NAME, points=[point])

    def clear(self) -> None:
        try:
            qdrant_client.delete(
                collection_name=COLLECTION_NAME,
                points_selector={"must": [{"key": "user_id", "match": {"value": self.user_id}}]}
            )
        except Exception as e:
            logger.error(f"Error clearing memory: {str(e)}")

def ensure_collection_exists():
    try:
        collections = qdrant_client.get_collections().collections
        exists = any(c.name == COLLECTION_NAME for c in collections)
        
        if not exists:
            qdrant_client.create_collection(
                collection_name=COLLECTION_NAME,
                vectors_config=VectorParams(
                    size=VECTOR_SIZE,
                    distance=Distance.COSINE
                )
            )
            logger.info(f"Created collection: {COLLECTION_NAME}")
    except Exception as e:
        logger.error(f"Error ensuring collection exists: {str(e)}")
        raise
git
def verify_firebase_token(token: str) -> str:
    try:
        if not token:
            raise HTTPException(status_code=401, detail="No token provided")
        decoded_token = auth.verify_id_token(token)
        return decoded_token['uid']
    except Exception as e:
        raise HTTPException(status_code=401, detail=f"Invalid token: {str(e)}")

def get_conversation_chain(user_id: str):
    try:
        # Create LLM
        llm = ChatGoogleGenerativeAI(
            model="gemini-pro",
            temperature=0.7,
            google_api_key=GOOGLE_API_KEY
        )
        
        # Create memory
        memory = QdrantMemory(user_id=user_id)
        
        # Create chain
        chain = ConversationChain(
            llm=llm,
            memory=memory,
            prompt=PromptTemplate(
                input_variables=["history", "input"],
    """Ensure Qdrant collection exists with proper schema"""
    try:
        collections = qdrant_client.get_collections().collections
        exists = any(c.name == COLLECTION_NAME for c in collections)
        
        if not exists:
            qdrant_client.create_collection(
                collection_name=COLLECTION_NAME,
                vectors_config=VectorParams(
                    size=VECTOR_SIZE,
                    distance=Distance.COSINE
                )
            )
            logger.info(f"Created collection: {COLLECTION_NAME}")
    except Exception as e:
        logger.error(f"Error ensuring collection exists: {str(e)}")
        raise

def get_conversation_chain(user_id: str):
    """Get conversation chain for a user"""
    try:
        # Create LLM
        llm = ChatGoogleGenerativeAI(
            model="gemini-pro",
            temperature=0.7,
            google_api_key=GOOGLE_API_KEY
        )
        
        # Create memory
        memory = QdrantMemory(user_id=user_id)
        
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
async def generate_text(request: PromptRequest, authorization: str = Header(None)):
    try:
        # Verify token and get user ID
        user_id = verify_firebase_token(authorization.replace("Bearer ", ""))
        logger.info(f"Processing request for user: {user_id}")
        
        # Ensure collection exists
        ensure_collection_exists()
        
        # Get conversation chain
        chain = get_conversation_chain(user_id)
        
        # Generate response
        response = chain.predict(input=request.prompt)
        
        return {
            "generated_text": response
        }
    except Exception as e:
        logger.error(f"Error processing request: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))

@app.delete("/clear-collection")
async def clear_collection(authorization: str = Header(None)):
    try:
        # Verify token and get user ID
        user_id = verify_firebase_token(authorization.replace("Bearer ", ""))
        logger.info(f"Clearing collection for user: {user_id}")
        
        # Create memory instance and clear it
        memory = QdrantMemory(user_id=user_id)
        memory.clear()
        
        return {"message": "Collection cleared successfully for user"}
    except Exception as e:
        logger.error(f"Error clearing collection: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000, log_level="info")