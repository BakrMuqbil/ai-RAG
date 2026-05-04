import requests
import json
import time
from app.core.config import settings
from app.core.logger import logger

def call_sentiment_llm(prompt: str) -> dict:
    """
    يتواصل مع OpenRouter لجلب تحليل المشاعر مع إعادة المحاولة التلقائية.
    """
    try:
        api_key = settings.OPENROUTER_API_KEY
        
        # ✅ النماذج المجانية المتاحة والمؤكدة (تم إزالة deepseek و gpt-4o-mini)
        models = [
            "google/gemini-2.0-flash-001",
            "google/gemini-flash-1.5",
            "mistralai/mistral-7b-instruct:free"
        ]

        response_text = None
        for model in models:
            try:
                logger.info(f"Trying model: {model}")
                response_text = _send_request_with_retry(model, api_key, prompt)
                if response_text:
                    logger.info(f"✅ Success with model: {model}")
                    break
            except Exception as e:
                logger.error(f"Model {model} failed: {str(e)}")
                continue

        if not response_text:
            return {"error": "Failed to get response from all models"}
        
        return _safe_parse(response_text)

    except Exception as e:
        logger.error(f"Critical error in LLM service: {str(e)}")
        return {"error": str(e)}
def _send_request_with_retry(model, api_key, prompt, max_retries=2):
    """
    إرسال الطلب مع إعادة المحاولة في حالة فشل الاتصال
    """
    for attempt in range(max_retries + 1):
        try:
            return _send_request(model, api_key, prompt)
        except (requests.exceptions.ConnectionError, ConnectionResetError, requests.exceptions.Timeout) as e:
            if attempt < max_retries:
                logger.warning(f"Connection error for {model}, retrying ({attempt+1}/{max_retries})...")
                time.sleep(2)  # انتظر ثانيتين قبل إعادة المحاولة
            else:
                logger.error(f"All retries failed for {model}: {str(e)}")
                raise e

def _send_request(model, api_key, prompt):
    """
    إرسال الطلب الفعلي إلى OpenRouter
    """
    response = requests.post(
        "https://openrouter.ai/api/v1/chat/completions",
        headers={
            "Authorization": f"Bearer {api_key}",
            "Content-Type": "application/json"
        },
        json={
    "model": model,
    "messages": [{"role": "user", "content": prompt}],
    "max_tokens": 600,        # ← قلل من 500 إلى 300 (ردود أقصر وأكثر دقة)
    "temperature": 0.5,       # ← قلل من 0.7 إلى 0.2 (أقل إبداع = أقل هلوسة)
    "top_p": 0.9,             # ← أضف هذا (تركيز على الكلمات الأكثر احتمالاً)
    "frequency_penalty": 0.5, # ← أضف هذا (يمنع تكرار نفس العبارات)
},
        timeout=30  # ✅ زيادة الوقت من 20 إلى 30 ثانية
    )
    
    # التحقق من حالة الاستجابة
    if response.status_code != 200:
        raise ValueError(f"HTTP {response.status_code}: {response.text[:200]}")
    
    res_json = response.json()
    if "error" in res_json:
        raise ValueError(res_json["error"]["message"] if isinstance(res_json["error"], dict) else str(res_json["error"]))
    
    return res_json["choices"][0]["message"]["content"]

def _safe_parse(output: str) -> dict:
    """
    تنظيف وتحويل استجابة LLM إلى JSON
    """
    try:
        # تنظيف النص من أي Markdown tags
        clean_text = output.strip()
        if "```json" in clean_text:
            clean_text = clean_text.split("```json")[1].split("```")[0]
        elif "```" in clean_text:
            clean_text = clean_text.split("```")[1].split("```")[0]
        
        # إزالة أي مسافات بيضاء إضافية
        clean_text = clean_text.strip()
        
        # محاولة تحليل JSON
        return json.loads(clean_text)
    except json.JSONDecodeError as e:
        logger.warning(f"JSON parsing failed: {e}. Raw output: {output[:200]}")
        return {"raw_text": output, "parse_error": str(e)}
    except Exception as e:
        logger.warning(f"Unexpected error in safe_parse: {e}")
        return {"raw_text": output, "parse_error": str(e)}