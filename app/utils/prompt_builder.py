
def build_rag_prompt(user_input: str, context: list) -> str:
    """
    بناء أمر (Prompt) يحتوي على السياق المستخرج من الملفات الخاصة.
    """
    context_str = "\n".join(context)
    
    return f"""
أنت مساعد ذكي وخبير. استخدم المعلومات التالية (السياق) للإجابة على سؤال المستخدم بدقة.
إذا لم تجد الإجابة في السياق، أخبر المستخدم أنك لا تملك هذه المعلومات الخاصة.

المعلومات الخاصة (Context):
{context_str}

سؤال المستخدم:
{user_input}

يجب أن يكون الرد بصيغة JSON فقط كالتالي:
{{
  "answer": "إجابتك هنا",
  "sources_used": true,
  "confidence_score": 0.9
}}
"""