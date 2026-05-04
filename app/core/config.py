from pydantic_settings import BaseSettings, SettingsConfigDict
from typing import Optional

class Settings(BaseSettings):
    """
    تحديث الإعدادات لدعم مهام مساعد العمليات (Project 3)
    """
    OPENROUTER_API_KEY: str
    OPENAI_API_KEY: Optional[str] = None
    PROJECT_NAME: str = "Techno-Bakr AI Agent"
    
    # إعدادات البريد لمهام (Reads emails)
    SMTP_SERVER: str = "smtp.gmail.com"
    SMTP_PORT: int = 587
    COMPANY_EMAIL: str = "bakr@tecno-bakr.com"
    EMAIL_PASSWORD: Optional[str] = None # سيتم قراءته من ملف .env
    
    # إعدادات نظام المهام (Operational Tasks)
    JIRA_API_TOKEN: Optional[str] = None
    JIRA_SERVER_URL: Optional[str] = "https://tecno-bakr.atlassian.net"
    # Trello settings
    TRELLO_API_KEY: Optional[str] = None
    TRELLO_TOKEN: Optional[str] = None
    TRELLO_BOARD_ID: Optional[str] = None
    TRELLO_LIST_ID: Optional[str] = None
    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        extra="ignore"
    )

settings = Settings()