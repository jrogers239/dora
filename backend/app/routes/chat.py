# backend/app/routes/chat.py
from fastapi import APIRouter, HTTPException
from services.llm_service import get_llm_response

router = APIRouter()

@router.post("/chat")
async def chat(prompt: str):
    try:
        response = await get_llm_response(prompt)
        return {"response": response}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))