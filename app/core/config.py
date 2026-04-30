from pydantic_settings import BaseSettings, SettingsConfigDict
from typing import Optional

class Settings(BaseSettings):
    """
    هذا الكلاس مسؤول عن قراءة والتحقق من إعدادات النظام من ملف .env
    """
    
    # تعريف المتغيرات وأنواعها (Validation)
    OPENROUTER_API_KEY: str
    OPENAI_API_KEY: Optional[str] = None
    PROJECT_NAME: str = "AI Sentiment Analyzer"
    
    # إعدادات ملف البيئة
    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        extra="ignore" # تجاهل أي متغيرات إضافية غير معرفة هنا
    )

# إنشاء نسخة واحدة (Singleton) ليتم استخدامها في كل مكان
settings = Settings()