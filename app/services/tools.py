from datetime import datetime, timedelta
import requests
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from app.core.config import settings
from app.core.logger import logger
from app.services.memory_service import chat_memory
import smtplib
from app.services.llm_service import call_sentiment_llm as call_llm
# ==================== الأدوات الأساسية ====================

def calculate_discount(price: float, discount_percent: float):
    """حساب السعر النهائي بعد الخصم."""
    final_price = price - (price * (discount_percent / 100))
    return {"final_price": final_price}

def get_current_time():
    """جلب الوقت والتاريخ الحالي بتوقيت اليمن (GMT+3)."""
    now = datetime.utcnow() + timedelta(hours=3)
    days_ar = {
        "Monday": "الاثنين", "Tuesday": "الثلاثاء", "Wednesday": "الأربعاء", 
        "Thursday": "الخميس", "Friday": "الجمعة", "Saturday": "السبت", "Sunday": "الأحد"
    }
    day_name = days_ar[now.strftime("%A")]
    return {
        "formatted": f"اليوم هو {day_name}، التاريخ: {now.strftime('%Y-%m-%d')}، الوقت: {now.strftime('%I:%M %p')}",
        "raw_iso": now.isoformat(),
        "day": day_name
    }

def calculate_time_remaining(target_date_iso: str):
    """حساب الوقت المتبقي لموعد معين."""
    try:
        now = datetime.utcnow() + timedelta(hours=3)
        target = datetime.fromisoformat(target_date_iso)
        diff = target - now
        if diff.total_seconds() < 0: 
            return {"status": "past"}
        days = diff.days
        hours, remainder = divmod(diff.seconds, 3600)
        minutes, _ = divmod(remainder, 60)
        return {"total_string": f"المتبقي {days} يوم و {hours} ساعة و {minutes} دقيقة."}
    except Exception as e: 
        return {"error": str(e)}

# ==================== أداة الإيميل ====================

def send_email(recipient: str, subject: str, body: str):
    """إرسال بريد إلكتروني حقيقي باستخدام SMTP."""
    try:
        smtp_server = settings.SMTP_SERVER
        smtp_port = settings.SMTP_PORT
        sender_email = settings.COMPANY_EMAIL
        password = settings.EMAIL_PASSWORD
        
        if not all([smtp_server, smtp_port, sender_email, password]):
            return {"status": "failed", "error": "SMTP settings are missing. Please check your .env file."}
        
        msg = MIMEMultipart()
        msg['From'] = sender_email
        msg['To'] = recipient
        msg['Subject'] = subject
        msg.attach(MIMEText(body, 'plain', 'utf-8'))
        
        server = smtplib.SMTP(smtp_server, smtp_port)
        server.starttls()
        server.login(sender_email, password)
        server.send_message(msg)
        server.quit()
        
        return {"status": "success", "to": recipient, "subject": subject, "message": f"تم إرسال البريد بنجاح إلى {recipient}"}
    except Exception as e:
        return {"status": "failed", "error": str(e), "message": "فشل إرسال البريد."}

# ==================== أداة Trello ====================

def create_operational_task(title: str, description: str, priority: str = "Medium"):
    """إنشاء مهمة حقيقية في Trello."""
    api_key = settings.TRELLO_API_KEY
    token = settings.TRELLO_TOKEN
    list_id = settings.TRELLO_LIST_ID
    
    if not api_key or not token:
        return {"status": "error", "message": "Trello API credentials missing."}
    
    url = "https://api.trello.com/1/cards"
    params = {
        "key": api_key,
        "token": token,
        "idList": list_id,
        "name": title,
        "desc": description + f"\nPriority: {priority}",
    }
    try:
        response = requests.post(url, params=params)
        response.raise_for_status()
        card = response.json()
        return {"status": "success", "task_id": card["id"], "url": card["url"], "title": title, "priority": priority}
    except Exception as e:
        return {"status": "error", "message": str(e)}

# ==================== أداة ترتيب الأولويات ====================

def prioritize_tasks(tasks_list: list):
    """ترتيب المهام حسب الأولوية باستخدام LLM."""
    try:
        if not tasks_list:
            return {"prioritized_list": [], "message": "لا توجد مهام للترتيب"}
        
        tasks_text = []
        for i, task in enumerate(tasks_list, 1):
            subject = task.get('subject', '')
            body = task.get('body', '')
            tasks_text.append(f"المهمة {i}:\n- الموضوع: {subject}\n- المحتوى: {body[:200]}...\n")
        
        prompt = f"""قم بترتيب هذه المهام حسب الأولوية (High/Medium/Low) بناءً على الكلمات المفتاحية مثل "عاجل", "طارئ", "مشكلة", "تعطل".

المهام:
{''.join(tasks_text)}

أعد JSON فقط بهذا التنسيق:
{{"prioritized_list": [{{"original_index": 1, "priority": "High", "reason": "السبب"}}]}}"""
        
        result = call_llm(prompt)
        
        if isinstance(result, dict) and "prioritized_list" in result:
            final_list = []
            for item in result["prioritized_list"]:
                original_index = item.get("original_index", 0) - 1
                if 0 <= original_index < len(tasks_list):
                    task = tasks_list[original_index].copy()
                    task["priority"] = item.get("priority", "Medium")
                    task["priority_reason"] = item.get("reason", "")
                    final_list.append(task)
            return {"prioritized_list": final_list, "method": "llm_based"}
        else:
            return _prioritize_tasks_fallback(tasks_list)
    except Exception as e:
        return _prioritize_tasks_fallback(tasks_list, str(e))

def _prioritize_tasks_fallback(tasks_list: list, error_msg: str = None):
    """طريقة مبسطة للترتيب في حالة فشل LLM"""
    def get_priority_score(task):
        text = f"{task.get('subject', '')} {task.get('body', '')}".lower()
        score = 0
        high_keywords = ['عاجل', 'طارئ', 'مشكلة', 'تعطل', 'دفع', 'urgent', 'error']
        for word in high_keywords:
            if word in text:
                score += 10
        return -score
    sorted_tasks = sorted(tasks_list, key=get_priority_score)
    return {"prioritized_list": sorted_tasks, "method": "keyword_based_fallback"}

def fetch_inbox_emails(email_address: str):
    """قراءة الرسائل الواردة (محاكاة)"""
    simulated_emails = [
        {"from": "ali@gmail.com", "subject": "استفسار عن باقة المؤسسات", "body": "أريد حجز باقة المؤسسات لشركتي."},
        {"from": "sara@outlook.com", "subject": "مشكلة في الدخول", "body": "لا أستطيع الوصول للوحة التحكم."}
    ]
    return {"status": "success", "emails": simulated_emails, "count": len(simulated_emails)}

# ==================== أداة الملخص (المُصلحة) ====================

def generate_session_summary(user_id: str):
    """تلخيص المحادثة باستخدام LLM"""
    try:
        # ✅ توحيد user_id مع routes.py
        if not user_id or user_id in ["None", "null", "current_user", "", "بكر"]:
            user_id = "web_user"
            logger.info(f"Normalized user_id to: {user_id}")
        
        history = chat_memory.get_history(user_id)
        
        # ✅ للتصحيح: طباعة عدد الرسائل
        logger.info(f"Retrieved {len(history)} messages for user: {user_id}")
        
        if not history:
            # عرض جميع الجلسات المتاحة للتصحيح
            all_sessions = list(chat_memory.sessions.keys()) if hasattr(chat_memory, 'sessions') else []
            return {
                "summary": f"لا توجد محادثات سابقة للمستخدم '{user_id}'.",
                "status": "empty",
                "message_count": 0,
                "user_id": user_id,
                "available_sessions": all_sessions
            }
        
        # تحويل التاريخ إلى نص
        conversation_text = []
        for msg in history:
            role = "المستخدم" if msg['role'] == 'user' else "المساعد"
            conversation_text.append(f"{role}: {msg['content']}")
        
        full_conversation = "\n".join(conversation_text)
        
        prompt = f"""قم بتلخيص المحادثة التالية:

{full_conversation}

أخرج JSON فقط بهذا التنسيق:
{{"summary_text": "الملخص هنا", "key_points": ["نقطة1"], "completed_actions": ["إجراء1"], "conversation_length": {len(history)}}}"""
        
        logger.info(f"Generating summary for user: {user_id}")
        result = call_llm(prompt)
        
        if isinstance(result, dict) and "summary_text" in result:
            return {"status": "success", "method": "llm_based", **result}
        else:
            return _generate_summary_fallback(history)
            
    except Exception as e:
        logger.error(f"Error in generate_session_summary: {str(e)}")
        return _generate_summary_fallback(history) if 'history' in locals() else {"error": str(e), "summary": f"خطأ: {str(e)}"}

def _generate_summary_fallback(history):
    """طريقة مبسطة للتلخيص"""
    try:
        user_messages = [msg['content'] for msg in history if msg['role'] == 'user']
        assistant_messages = [msg['content'] for msg in history if msg['role'] == 'assistant']
        
        has_email = any("إيميل" in msg or "بريد" in msg for msg in user_messages)
        has_task = any("تذكرة" in msg or "Trello" in msg for msg in assistant_messages)
        has_priority = any("أولوية" in msg or "ترتيب" in msg for msg in user_messages)
        
        completed = []
        if has_email: 
          completed.append("📧 تم إرسال إيميلات")
        if has_task:
         completed.append("🎫 تم إنشاء تذاكر عمل")
        if has_priority:
         completed.append("📊 تم ترتيب المهام حسب الأولوية")
        if not completed: 
         completed.append("💬 محادثة عامة")
        
        summary = f"""📝 **ملخص المحادثة**

عدد الرسائل: {len(history)} رسالة

**الإجراءات التي تمت:**
{chr(10).join(f'- {action}' for action in completed)}

**آخر سؤال:**
{user_messages[-1][:150] if user_messages else 'لا يوجد'}"""
        
        return {"status": "success", "method": "fallback_simple", "summary_text": summary, "completed_actions": completed, "conversation_length": len(history)}
    except Exception as e:
        return {"status": "error", "error": str(e), "summary_text": "حدث خطأ في تلخيص المحادثة"}