from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
import os
from dotenv import load_dotenv
from google import genai
from pathlib import Path

# Load environment variables
current_dir = Path(__file__).parent
env_path = current_dir / '.env'
load_dotenv(env_path)

# Initialize Gemini
GOOGLE_API_KEY = os.getenv("GOOGLE_AI_STUDIO_TOKEN")
if not GOOGLE_API_KEY:
    raise ValueError("GOOGLE_API_KEY not found in .env file")

client = genai.Client(api_key=GOOGLE_API_KEY)
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

@app.post("/generate")
async def generate_text(request: PromptRequest):
    try:
        response = client.models.generate_content(
            model="gemini-2.0-flash",
            contents=request.prompt
        )
        return {"generated_text": response.text}
    except Exception as e:
        return {"error": str(e)}

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)