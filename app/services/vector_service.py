import math

# تخزين البيانات في الذاكرة (Memory)
knowledge_base = []

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

def add_document(text: str, doc_id: str = None, metadata: dict = None):
    # نقوم بتخزين النص كما هو حالياً
    # في الأنظمة البسيطة، البحث النصي يكفي جداً
    knowledge_base.append({"content": text, "id": doc_id})
    return True

def query_knowledge(query_text: str, n_results: int = 1):
    """
    البحث عن أفضل نص مطابق للسؤال باستخدام البحث النصي الذكي
    """
    if not knowledge_base:
        return []
    
    # سنستخدم حالياً البحث بوجود الكلمات المفتاحية (Keyword Matching)
    # وهو فعال جداً وسريع في Termux للملفات الصغيرة
    query_words = set(query_text.lower().split())
    
    scored_results = []
    for doc in knowledge_base:
        doc_words = set(doc['content'].lower().split())
        # حساب كم كلمة من السؤال موجودة في النص
        score = len(query_words.intersection(doc_words))
        scored_results.append((score, doc['content']))
    
    # ترتيب النتائج حسب الأعلى درجة
    scored_results.sort(key=lambda x: x[0], reverse=True)
    
    # إرجاع أفضل نتيجة إذا كان هناك تطابق
    return [scored_results[0][1]] if scored_results[0][0] > 0 else []