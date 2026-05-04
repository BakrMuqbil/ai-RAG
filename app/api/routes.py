from fastapi import APIRouter, HTTPException
from pydantic import BaseModel
from app.services.agent_service import run_agent  # استدعاء محرك الوكيل الذكي
from app.services.vector_service import add_document
from app.services.memory_service import chat_memory
import uuid

# إنشاء الراوتر الخاص بـ FastAPI
router = APIRouter(tags=["agent"])  # لا بادئة 

# نموذج البيانات المتوقع من المستخدم
class ChatRequest(BaseModel):
    input: str

@router.post("/ask")
async def ask_ai(request: ChatRequest):
    """
    مسار المحادثة الذكي: 
    يقوم باستلام سؤال المستخدم وتمريره للوكيل (Agent) الذي يقرر 
    بنفسه استدعاء أدوات البحث أو الحساب.
    """
    try:
        # التأكد من أن المدخلات ليست فارغة
        if not request.input.strip():
            raise HTTPException(status_code=400, detail="الرجاء إدخال سؤال صالح")

        # ✅ استخدام user_id ثابت لتوحيد الذاكرة
        user_id = "web_user"
        
        # تشغيل محرك الوكيل الذكي مع تمرير user_id
        result = run_agent(request.input, user_id=user_id)
        
        return {
            "user_input": request.input,
            "ai_response": result,
            "status": "success",
            "engine": "AI Agent (Project 3)"
        }
        
    except Exception as e:
        # تسجيل الخطأ في السيرفر وإرجاع رسالة مفهومة للمستخدم
        print(f"[!] API Route Error: {str(e)}")
        raise HTTPException(
            status_code=500, 
            detail=f"حدث خطأ في معالجة طلبك عبر الوكيل: {str(e)}"
        )

@router.post("/train")
async def train_ai(request: ChatRequest):
    """
    مسار التدريب: 
    يسمح بإضافة نصوص جديدة لقاعدة البيانات الاتجاهية (Vector DB).
    """
    try:
        if not request.input.strip():
            raise HTTPException(status_code=400, detail="لا يمكن إضافة نص فارغ")

        # توليد معرف فريد للمستند الجديد
        doc_id = str(uuid.uuid4())
        
        # استدعاء دالة إضافة المستند من الـ Vector Service
        add_document(request.input, doc_id)
        
        return {
            "status": "success", 
            "message": "تمت إضافة المعلومات بنجاح إلى قاعدة المعرفة",
            "doc_id": doc_id
        }
    except Exception as e:
        print(f"[!] Training Error: {str(e)}")
        raise HTTPException(status_code=500, detail=f"فشل إضافة المعلومات: {str(e)}")

@router.get("/status")
async def get_status():
    """
    مسار بسيط للتأكد من أن السيرفر يعمل بشكل صحيح.
    """
    return {"status": "online", "project": "Techno-Bakr AI Agent"}

@router.get("/debug/memory")
async def debug_memory():
    """
    مسار للتصحيح: عرض محتويات الذاكرة
    """
    sessions = list(chat_memory.sessions.keys()) if hasattr(chat_memory, 'sessions') else []
    memory_data = {}
    for session in sessions:
        memory_data[session] = len(chat_memory.get_history(session))
    
    return {
        "available_sessions": sessions,
        "message_counts": memory_data
    }