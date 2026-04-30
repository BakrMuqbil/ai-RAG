from fastapi import APIRouter, HTTPException
from pydantic import BaseModel
from app.services.llm_service import call_sentiment_llm
from app.services.vector_service import query_knowledge, add_document
from app.utils.prompt_builder import build_rag_prompt
import os

router = APIRouter()

class ChatRequest(BaseModel):
    input: str

@router.post("/ask")
async def ask_ai(request: ChatRequest):
    try:
        # 1. البحث في الذاكرة الخارجية عن معلومات متعلقة بالسؤال
        context = query_knowledge(request.input)
        
        # 2. بناء الأمر (Prompt) مع السياق المكتشف
        enriched_prompt = build_rag_prompt(request.input, context)
        
        # 3. إرسال الأمر المدمج للموديل (Gemini/OpenRouter)
        result = call_sentiment_llm(enriched_prompt)
        
        return {
            "user_input": request.input,
            "ai_response": result,
            "context_found": len(context) > 0
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.post("/train")
async def train_ai(request: ChatRequest):
    """
    إضافة معلومات جديدة للذاكرة يدوياً عبر API
    """
    import uuid
    doc_id = str(uuid.uuid4())
    add_document(request.input, doc_id)
    return {"status": "success", "message": "Information added to knowledge base"}