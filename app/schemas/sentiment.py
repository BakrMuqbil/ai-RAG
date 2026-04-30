from pydantic import BaseModel
from typing import Optional

# 1. نموذج المدخلات (ما يرسله المستخدم في الـ Body)
class AnalyzeRequest(BaseModel):
    text: str

# 2. نموذج المخرجات (ما نضمن أن السيرفر سيرسله للمستخدم)
class SentimentResponse(BaseModel):
    sentiment: str       # مثال: positive, negative, neutral
    score: int           # تقييم من 1 إلى 5
    product: Optional[str] = None # اسم المنتج إن وُجد، وإلا يكون null
    summary: str         # ملخص بالعربي للتحليل