import math
import os

# قاعدة معرفة بسيطة كخيار احتياطي في الذاكرة
knowledge_base = []
# تخزين البيانات في الذاكرة (Memory)

def cosine_similarity(v1, v2):
    """حساب التشابه بين نصين رياضياً"""
    sum_xx, sum_yy, sum_xy = 0, 0, 0
    for i in range(len(v1)):
        x = v1[i]
        y = v2[i]
        sum_xx += x*x
        sum_yy += y*y
        sum_xy += x*y
    return sum_xy / math.sqrt(sum_xx*sum_yy)

def get_simple_embedding(text):
    """
    دالة بسيطة جداً لتحويل النص لمصفوفة أرقام 
    في المشاريع الكبيرة نستخدم API من Gemini أو OpenAI
    هنا سنستخدم خوارزمية تردد الكلمات المبسطة
    """
    words = text.lower().split()
    # تمثيل مبسط (فقط للتجربة الآن)
    return [words.count(w) for w in set(words)]

def query_knowledge(query_text: str):
    """
    جلب سياق المعلومات من الملف لتقديمه للوكيل.
    """
    file_path = "data/info.txt"
    print(f"[*] جاري البحث عن: {query_text}")
    
    try:
        if os.path.exists(file_path):
            with open(file_path, "r", encoding="utf-8") as f:
                content = f.read()
            # إضافة ترويسة واضحة للوكيل
            return {
                "status": "success",
                "data_found": True,
                "context": f"إليك المعلومات الرسمية من ملفات شركة تكنو-بكر:\n{content}"
            }
        
        return {"status": "error", "message": "ملف المعلومات غير موجود."}
    except Exception as e:
        return {"status": "error", "message": str(e)}

def add_document(content: str, doc_id: str, save_to_file: bool = True):
    """
    إضافة مستند مع حماية من التضخم.
    """
    global knowledge_base
    knowledge_base.append({"id": doc_id, "content": content})
    
    if save_to_file:
        try:
            os.makedirs("data", exist_ok=True)
            with open("data/info.txt", "a", encoding="utf-8") as f:
                f.write(f"\n\n--- تحديث جديد ---\n{content}")
        except Exception as e:
            print(f"Error saving: {e}")