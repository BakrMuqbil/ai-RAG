import logging
import sys
  
LOG_FORMAT = "%(asctime)s - %(levelname)s - %(name)s - %(message)s"

def setup_logger():
    """
    إعداد محرك السجلات للنظام بالكامل.
    """
    
    # 2. إنشاء الكائن الرئيسي للسجلات
    logger = logging.getLogger("SENTIMENT-AI")
    
    # 3. تحديد مستوى الحساسية (INFO يعني تسجيل كل شيء من معلومات عادية وأخطاء)
    logger.setLevel(logging.INFO)

    # 4. إعداد "المُعالج" (Handler) الذي يطبع الرسائل على الشاشة (Console)
    console_handler = logging.StreamHandler(sys.stdout)
    console_handler.setFormatter(logging.Formatter(LOG_FORMAT))

    # 5. إضافة المُعالج للكائن الرئيسي
    if not logger.handlers:
        logger.addHandler(console_handler)

    return logger

# إنشاء نسخة جاهزة للاستخدام في كل المشروع
logger = setup_logger()