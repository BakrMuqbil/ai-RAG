import requests
import json
from app.core.config import settings
from app.core.logger import logger

def call_sentiment_llm(prompt: str) -> dict:
    """
    يتواصل مع OpenRouter لجلب تحليل المشاعر.
    """
    try:
        # استخدام المفتاح من الإعدادات المركزية (Config)
        api_key = settings.OPENROUTER_API_KEY
        #api_key = settings.OPENAI_API_KEY
        # قائمة الموديلات التي سنجربها (Fallback logic)
        models = [
             "deepseek/deepseek-v3.1-base",
             
             "gpt-4o-mini",
             
            "google/gemini-2.0-flash-001",
            "google/gemini-flash-1.5",
            "mistralai/mistral-7b-instruct:free"
        ]

        response_text = None
        for model in models:
            try:
                logger.info(f"Trying model: {model}")
                response_text = _send_request(model, api_key, prompt)
                if response_text:
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

def _send_request(model, api_key, prompt):
    response = requests.post(
        "https://openrouter.ai/api/v1/chat/completions",
        headers={
            "Authorization": f"Bearer {api_key}",
            "Content-Type": "application/json"
        },
        json={
            "model": model,
            "messages": [{"role": "user", "content": prompt}]
        },
        timeout=20
    )
    res_json = response.json()
    if "error" in res_json:
        raise ValueError(res_json["error"])
    return res_json["choices"][0]["message"]["content"]

def _safe_parse(output: str) -> dict:
    try:
        # تنظيف النص من أي Markdown tags
        clean_text = output.strip()
        if "```json" in clean_text:
            clean_text = clean_text.split("```json")[1].split("```")[0]
        elif "```" in clean_text:
            clean_text = clean_text.split("```")[1].split("```")[0]
        
        return json.loads(clean_text.strip())
    except Exception as e:
        logger.warning(f"JSON parsing failed, returning raw text. Error: {e}")
        return {"raw_text": output}