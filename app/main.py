from fastapi import FastAPI
from app.api.routes import router as api_router
from app.services.vector_service import add_document
import os

app = FastAPI(title="AI RAG System")

# وظيفة لقراءة الملفات وتغذية الذاكرة تلقائياً
@app.on_event("startup")
async def load_knowledge_base():
    data_path = "data/"
    if os.path.exists(data_path):
        for filename in os.listdir(data_path):
            if filename.endswith(".txt"):
                with open(os.path.join(data_path, filename), "r", encoding="utf-8") as f:
                    content = f.read()
                    # إضافة محتوى الملف للذاكرة (نستخدم اسم الملف كـ ID)
                    add_document(content, doc_id=filename, metadata={"source": filename})
                    print(f"✅ Loaded: {filename}")

app.include_router(api_router, prefix="/api/v1")

@app.get("/")
async def root():
    return {"status": "online", "message": "Knowledge Base Synced"}