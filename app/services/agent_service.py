import os
import json
import requests
from app.core.config import settings
from app.services.tools import (
    send_email,
    calculate_discount, 
    get_current_time, 
    calculate_time_remaining,
    fetch_inbox_emails,
    prioritize_tasks,
    create_operational_task,
    generate_session_summary
)
from app.services.vector_service import query_knowledge
from app.services.memory_service import chat_memory
from app.core.logger import logger

API_KEY = settings.OPENROUTER_API_KEY
URL = "https://openrouter.ai/api/v1/chat/completions"
MODEL_NAME = "google/gemini-2.0-flash-001"

AVAILABLE_TOOLS = {
    "send_email": send_email,
    "create_operational_task": create_operational_task,
    "prioritize_tasks": prioritize_tasks,
    "generate_session_summary": generate_session_summary,
    "query_knowledge": query_knowledge,
    "get_current_time": get_current_time,
    "calculate_discount": calculate_discount,
    "calculate_time_remaining": calculate_time_remaining,
    "fetch_inbox_emails": fetch_inbox_emails,
}

# -------------------------------
# Tools Definition (بدون تغيير)
# -------------------------------
TOOLS_DEFINITION = [
    {
        "type": "function",
        "function": {
            "name": "send_email",
            "description": "📧 إرسال بريد إلكتروني حقيقي. استخدم هذه الأداة عندما يطلب المستخدم: 'أرسل ايميل'، 'بريد إلكتروني'، 'email'، 'مراسلة'.",
            "parameters": {
                "type": "object",
                "properties": {
                    "recipient": {"type": "string", "description": "عنوان البريد الإلكتروني للمستلم (مثال: user@gmail.com)"},
                    "subject": {"type": "string", "description": "عنوان البريد (مثال: اختبار، تقرير، استفسار)"},
                    "body": {"type": "string", "description": "محتوى البريد النصي"}
                },
                "required": ["recipient", "subject", "body"]
            }
        }
    },
    {
        "type": "function",
        "function": {
            "name": "create_operational_task",
            "description": "🎫 إنشاء تذكرة/مهمة في Trello. استخدم هذه الأداة عندما يطلب المستخدم: 'تذكرة'، 'مهمة'، 'Trello'، 'Jira'، 'إنشاء تذكرة'، 'مشكلة تقنية'، 'بلغ المهندس'، 'سجل مشكلة'.",
            "parameters": {
                "type": "object",
                "properties": {
                    "title": {"type": "string", "description": "عنوان المهمة أو المشكلة (يجب أن يكون واضحاً ومختصراً)"},
                    "description": {"type": "string", "description": "وصف تفصيلي للمشكلة أو المهمة المطلوبة"},
                    "priority": {"type": "string", "enum": ["High", "Medium", "Low"], "description": "الأولوية: High لعاجل وطارئ، Medium لمهام عادية، Low لاقتراحات أو تذكيرات"}
                },
                "required": ["title", "description"]
            }
        }
    },
    {
        "type": "function",
        "function": {
            "name": "prioritize_tasks",
            "description": "📊 ترتيب المهام حسب الأولوية باستخدام الذكاء الاصطناعي. استخدم هذه الأداة عندما يطلب المستخدم: 'رتب'، 'أولوية'، 'priority'، 'صنف المهام'، 'أهمية'.",
            "parameters": {
                "type": "object",
                "properties": {
                    "tasks_list": {
                        "type": "array",
                        "items": {
                            "type": "object",
                            "properties": {
                                "subject": {"type": "string", "description": "عنوان أو موضوع المهمة"},
                                "body": {"type": "string", "description": "وصف تفصيلي للمهمة"}
                            }
                        },
                        "description": "قائمة المهام المراد ترتيبها حسب الأهمية"
                    }
                },
                "required": ["tasks_list"]
            }
        }
    },
    {
        "type": "function",
        "function": {
            "name": "generate_session_summary",
            "description": "📝 تلخيص المحادثة الحالية. استخدم هذه الأداة عندما يطلب المستخدم: 'ملخص'، 'خلاصة'، 'تلخيص'، 'summary'، 'ماذا حدث'، 'ملخص المحادثة'.",
            "parameters": {
                "type": "object",
                "properties": {}  # ✅ تم إزالة user_id من هنا
            }
        }
    },
    {
        "type": "function",
        "function": {
            "name": "query_knowledge",
            "description": "📚 الاستعلام عن معلومات الشركة. استخدم هذه الأداة عندما يسأل المستخدم عن: 'الشركة'، 'الأسعار'، 'الخدمات'، 'الموظفين'، 'بيانات التواصل'، 'من هو'، 'ما هي'.",
            "parameters": {
                "type": "object",
                "properties": {
                    "query_text": {"type": "string", "description": "السؤال أو النص المراد البحث عنه في قاعدة المعرفة"}
                },
                "required": ["query_text"]
            }
        }
    },
    {
        "type": "function",
        "function": {
            "name": "get_current_time",
            "description": "⏰ معرفة الوقت والتاريخ الحاليين. استخدم هذه الأداة عندما يطلب المستخدم: 'الوقت'، 'التاريخ'، 'الساعة'، 'كم الساعة'، 'أي يوم'، 'اليوم'.",
            "parameters": {"type": "object", "properties": {}}
        }
    },
    {
        "type": "function",
        "function": {
            "name": "calculate_discount",
            "description": "💰 حساب السعر بعد الخصم. استخدم هذه الأداة عندما يطلب المستخدم حساب خصم أو سعر بعد التخفيض.",
            "parameters": {
                "type": "object",
                "properties": {
                    "price": {"type": "number", "description": "السعر الأصلي"},
                    "discount_percent": {"type": "number", "description": "نسبة الخصم (من 0 إلى 100)"}
                },
                "required": ["price", "discount_percent"]
            }
        }
    },
    {
        "type": "function",
        "function": {
            "name": "calculate_time_remaining",
            "description": "⏳ حساب الوقت المتبقي لموعد محدد. استخدم هذه الأداة عندما يسأل المستخدم عن الوقت المتبقي لحدث مستقبلي.",
            "parameters": {
                "type": "object",
                "properties": {
                    "target_date_iso": {"type": "string", "description": "التاريخ المستهدف بصيغة ISO (YYYY-MM-DDTHH:MM:SS)"}
                },
                "required": ["target_date_iso"]
            }
        }
    }
] # احتفظ بنفس التعريف الحالي عندك


def run_agent(user_prompt: str, user_id: str = "default_user"):
    headers = {
        "Authorization": f"Bearer {API_KEY}",
        "Content-Type": "application/json"
    }

    # ✅ System Instruction نظيف (بدون تضارب)
    system_instruction = (
        "أنت وكيل عمليات ذكي.\n"
        "نفّذ طلب المستخدم باستخدام الأدوات فقط عند الحاجة.\n"
        "لا تفترض النتائج.\n"
        "اعرض فقط نتيجة الأداة.\n"
        "لا تنفذ أكثر من أداة إلا إذا طُلب ذلك.\n"
        "لا تستخدم نتائج قديمة.\n"
    )

    history = chat_memory.get_history(user_id)
    summary_context = chat_memory.get_summary_context(user_id)

    messages = (
    [{"role": "system", "content": system_instruction}]
    + [{"role": "system", "content": f"سجل العمليات السابقة:\n{summary_context}"}]
    + history[-6:]
    + [{"role": "user", "content": user_prompt}]
)

    try:
        # -------------------------------
        # STEP 1: Ask LLM
        # -------------------------------
        response = requests.post(
            URL,
            headers=headers,
            json={
                "model": MODEL_NAME,
                "messages": messages,
                "tools": TOOLS_DEFINITION,
                "tool_choice": "auto"
            },
            timeout=60
        )

        assistant_message = response.json()['choices'][0]['message']
        messages.append(assistant_message)

        # -------------------------------
        # STEP 2: If no tool → return مباشرة
        # -------------------------------
        if not assistant_message.get("tool_calls"):
            final_content = assistant_message.get("content", "")

            chat_memory.add_message(user_id, "user", user_prompt)
            chat_memory.add_message(user_id, "assistant", final_content)

            return final_content

        # -------------------------------
        # STEP 3: Execute ONLY ONE tool
        # -------------------------------
        tool_call = assistant_message['tool_calls'][0]

        func_name = tool_call['function']['name']
        args = json.loads(tool_call['function']['arguments'])

        logger.info(f"[TOOL] {func_name} called with {args}")

        try:
            if func_name == "generate_session_summary":
                result = AVAILABLE_TOOLS[func_name](user_id=user_id)
            else:
                result = AVAILABLE_TOOLS[func_name](**args)

        except Exception as e:
            logger.error(f"Tool {func_name} failed: {e}")
            result = {
                "status": "error",
                "message": str(e)
            }

        # -------------------------------
        # STEP 4: Add tool result
        # -------------------------------
        messages.append({
            "role": "tool",
            "tool_call_id": tool_call['id'],
            "name": func_name,
            "content": json.dumps(result, ensure_ascii=False)
        })

        # -------------------------------
        # STEP 5: Final LLM response
        # -------------------------------
        final_response = requests.post(
            URL,
            headers=headers,
            json={
                "model": MODEL_NAME,
                "messages": messages
            },
            timeout=60
        )

        final_message = final_response.json()['choices'][0]['message']
        final_content = final_message.get("content", "")

        # -------------------------------
        # STEP 6: Clean Memory (مهم جداً)
        # -------------------------------
        chat_memory.add_message(user_id, "user", user_prompt)
        chat_memory.add_message(user_id, "assistant", final_content)

        return final_content

    except Exception as e:
        logger.error(f"Agent error: {str(e)}")
        return "حدث خطأ تقني في النظام"