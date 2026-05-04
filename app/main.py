from fastapi import FastAPI
from app.api.routes import router as api_router
from app.services.vector_service import add_document
import os
from fastapi.staticfiles import StaticFiles
from fastapi.responses import FileResponse

app = FastAPI(title="Techno-Bakr AI Agent System")

if not os.path.exists("static"):
    os.makedirs("static")
app.mount("/static", StaticFiles(directory="static"), name="static")

@app.on_event("startup")
async def load_knowledge_base():
    data_path = "data/"
    if os.path.exists(data_path):
        for filename in os.listdir(data_path):
            if filename.endswith(".txt"):
                file_full_path = os.path.join(data_path, filename)
                try:
                    with open(file_full_path, "r", encoding="utf-8") as f:
                        content = f.read()
                        # التعديل الهام: save_to_file=False
                        # لأننا نقرأ من الملف أصلاً فلا نريد إعادة الكتابة فيه!
                        add_document(content, doc_id=filename, save_to_file=False)
                        print(f"✅ Indexed in RAM: {filename}")
                except Exception as e:
                    print(f"❌ Error loading {filename}: {e}")
    else:
        os.makedirs(data_path, exist_ok=True)

app.include_router(api_router, prefix="/api/v1")

@app.get("/")
async def read_index():
    return FileResponse('static/index.html')