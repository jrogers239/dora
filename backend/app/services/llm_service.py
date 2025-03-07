# backend/app/services/llm_service.py
import httpx

async def get_llm_response(prompt: str):
    async with httpx.AsyncClient() as client:
        response = await client.post(
            "https://api-inference.huggingface.co/models/gpt2",
            json={"inputs": prompt},
            headers={"Authorization": "Bearer hf_KcHtQVkrWwQgzOpnuwmjeknBWpGsTjMQKmN"}
        )
    return response.json()[0]["generated_text"]