from typing import List
from fastapi import FastAPI, Request
from fastapi.responses import Response
from pydantic import BaseModel
import requests

from fastapi.middleware.cors import CORSMiddleware
import uvicorn

app = FastAPI()

origins = [
    "https://edubeyondchat.vercel.app"
]

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,  # No trailing slash
    allow_credentials=True,
    allow_methods=["*"],    # Allow all HTTP methods
    allow_headers=["*"],    # Allow all headers
)

# Optional: simple logging middleware to help debug requests
@app.middleware("http")
async def log_requests(request: Request, call_next):
    print(f"Request: {request.method} {request.url}")
    response = await call_next(request)
    return response

class Message(BaseModel):
    role: str
    content: str

class ChatRequest(BaseModel):
    session_id: str
    messages: List[Message]

@app.post("/chat")
async def chat(request: ChatRequest):
    try:
        payload = {
            "model": "meta-llama/Llama-3.3-70B-Instruct-Turbo-Free",
            "messages": [
                {
                    "role": "system",
                    "content": (
                        "you are an academic chatbot that represents edubeyond.ai and you help with ap physics c. keep your messages succinct and if you are asked to solve questions, do it methodically, using formulas and step by step working"
                    )
                },
            ] + [{"role": msg.role, "content": msg.content} for msg in request.messages],
            "temperature": 0.7,
            "max_tokens": 300
        }

        res = requests.post(
            "https://api.together.xyz/v1/chat/completions",
            headers={
                "Authorization": "Bearer 9c7409f52efa969b90731f867d55f9cc93c038e3ff5f9a8318e3cfee219cd058",
                "Content-Type": "application/json"
            },
            json=payload
        )
        response_json = res.json()

        if "choices" in response_json and response_json["choices"]:
            reply = response_json["choices"][0]["message"]["content"]
            return {"response": reply}
        else:
            return {"response": "No response from model."}
    except Exception as e:
        return {"response": f"Error: {str(e)}"}

if __name__ == "__main__":
    uvicorn.run("edubeyondchat:app", host="0.0.0.0", port=8000, reload=True)