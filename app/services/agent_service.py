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

# ربط جميع الأدوات (القديمة + الجديدة)
AVAILABLE_TOOLS = {
    "send_email": send_email,
    "create_operational_task": create_operational_task,
    "prioritize_tasks": prioritize_tasks,
    "generate_session_summary": generate_session_summary,
    "query_knowledge": query_knowledge,
    "get_current_time": get_current_time,
    "calculate_discount": calculate_discount,
    "calculate_time_remaining": calculate_time_remaining,
    "fetch_inbox_emails": fetch_inbox_emails,  # اختياري
}

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
]

def run_agent(user_prompt: str, user_id: str = "default_user"):
    headers = {"Authorization": f"Bearer {API_KEY}", "Content-Type": "application/json"}

    #Context Injection
    system_instruction = (
    "أنت 'وكيل عمليات ذكي' متخصص في تنفيذ المهام باستخدام الأدوات بدقة وموثوقية.\n\n"
    
    "⚡ **قواعد أساسية يجب اتباعها** ⚡\n"
    "1. التزم بدورك كوكيل عمليات، ولا تقدم آراء أو نصائح شخصية.\n"
    "2. لا تخترع معلومات أو نتائج غير موجودة.\n"
    "3. إذا لم تكن متأكداً، قل 'لا أعرف'.\n"
    "4. لا تعتبر أي مهمة مكتملة إلا بعد استلام نتيجة من الأداة.\n"
    "5. يمكنك استخدام أكثر من أداة إذا تطلبت المهمة ذلك.\n\n"
    
    "🧠 **منهجية العمل (Execution Logic)**\n"
    "1. حلل طلب المستخدم.\n"
    "2. إذا كان يتطلب تنفيذ → استخدم الأداة المناسبة.\n"
    "3. لا تكتب نتيجة التنفيذ بنفسك.\n"
    "4. انتظر نتيجة الأداة ثم اعرضها فقط.\n\n"
    
    "🛠️ **الأدوات المتاحة (لا تستخدم أدوات خارج هذه القائمة)**\n"
    "- send_email → لإرسال الإيميلات\n"
    "- create_operational_task → لإنشاء تذاكر Trello\n"
    "- prioritize_tasks → لترتيب الأولويات\n"
    "- generate_session_summary → لتلخيص المحادثة\n"
    "- query_knowledge → للاستعلام عن معلومات الشركة\n"
    "- get_current_time → لمعرفة الوقت\n\n"
    
    "📋 **تنسيق الردود**\n"
    "- اعرض نتيجة الأداة كما هي بدون اختصار مخل.\n"
    "- عند استخدام prioritize_tasks → اعرض المهام مرتبة مع الأولويات.\n"
    "- عند استخدام generate_session_summary → اعرض الملخص كاملاً.\n"
    "- لا تقل 'تم التنفيذ' أو 'تم الإرسال' بدون وجود نتيجة فعلية.\n"
    "- لا تعيد صياغة نتائج الأدوات الحساسة (مثل الإيميل أو التذاكر).\n"
    "- لا تكرر نفس المعلومات.\n\n"
    
    "🔴 **ممنوعات** 🔴\n"
    "- لا تفترض نجاح أي أداة.\n"
    "- لا تقل 'تم إرسال الإيميل' أو 'تم إنشاء التذكرة' بدون دليل من الأداة.\n"
    "- لا تشرح ما ستفعله قبل التنفيذ.\n"
    "- لا تسأل أسئلة غير ضرورية.\n"
    "- لا تدّعي تنفيذ لم يحدث.\n\n"
    
    "⚠️ **في حال الفشل أو عدم التوفر**\n"
    "- إذا فشلت الأداة → اعرض رسالة الخطأ كما هي.\n"
    "- إذا لم توجد أداة مناسبة → قل 'لا أستطيع تنفيذ هذا الطلب'.\n\n"
    
    "✅ **سلوك صحيح متوقع**\n"
    "- تنفيذ الأداة → انتظار النتيجة → عرض النتيجة.\n"
    
    "❌ **سلوك خاطئ**\n"
    "- كتابة 'تم الإرسال' بدون تنفيذ فعلي.\n"
    "- تلخيص بدون استخدام الأداة.\n"
    "- ترتيب مهام بدون الأداة.\n\n"
    
    "🧩 **ملاحظة مهمة**\n"
    "أنت لا تنفذ المهام بنفسك، بل تستخدم الأدوات.\n"
    "النظام الخارجي هو المسؤول عن التنفيذ الفعلي.\n"
    "مهمتك هي اتخاذ القرار الصحيح وعرض النتيجة الحقيقية فقط."
)
    history = chat_memory.get_history(user_id)
    messages = [{"role": "system", "content": system_instruction}] + history[-4:] + [{"role": "user", "content": user_prompt}]
    
    try:
        # حلقة تنفيذ الوكيل
        iteration = 0
        max_iterations = 5  # لمنع الحلقات اللانهائية
        
        while iteration < max_iterations:
            response = requests.post(URL, headers=headers, json={
                "model": MODEL_NAME,
                "messages": messages,
                "tools": TOOLS_DEFINITION,
                "tool_choice": "auto"
            }, timeout=60)
            
            assistant_message = response.json()['choices'][0]['message']
            messages.append(assistant_message)  # أضف رد المساعد أولاً
            
            # إذا لم توجد أدوات مطلوبة، ننهي الحلقة
            if not assistant_message.get("tool_calls"):
                break
            
            # تنفيذ الأدوات المطلوبة
            for tool_call in assistant_message['tool_calls']:
                func_name = tool_call['function']['name']
                args = json.loads(tool_call['function']['arguments'])
                logger.info(f"Executing tool: {func_name} with args: {args}")
                
                try:
                    # ✅ التعديل الأساسي: تمرير user_id تلقائياً لأداة الملخص
                    if func_name == "generate_session_summary":
                        # الأداة لا تطلب user_id من الـ LLM، نمرره من run_agent
                        result = AVAILABLE_TOOLS[func_name](user_id=user_id)
                        logger.info(f"Auto-passed user_id={user_id} to generate_session_summary")
                    else:
                        result = AVAILABLE_TOOLS[func_name](**args)
                except Exception as e:
                    logger.error(f"Tool {func_name} failed: {e}")
                    result = {"error": str(e)}
                
                messages.append({
                    "role": "tool",
                    "tool_call_id": tool_call['id'],
                    "name": func_name,
                    "content": json.dumps(result, ensure_ascii=False)
                })
            
            iteration += 1
        
        # بعد الخروج من الحلقة، نحصل على الرد النهائي (المحتوى آخر رسالة من assistant)
        final_message = messages[-1]  # آخر رسالة أضيفت
        if final_message["role"] == "assistant":
            final_content = final_message.get("content", "")
        elif final_message["role"] == "tool" and len(messages) > 1:
            # إذا انتهت الحلقة بعد أدوات ولم يكن هناك رد مساعد نضيف طلب أخير
            final_response = requests.post(URL, headers=headers, json={"model": MODEL_NAME, "messages": messages}, timeout=60)
            final_content = final_response.json()['choices'][0]['message']['content']
        else:
            final_content = "لم يتم الحصول على رد واضح."
        
        # حفظ الذاكرة
        chat_memory.add_message(user_id, "user", user_prompt)
        chat_memory.add_message(user_id, "assistant", final_content)
        return final_content
    
    except Exception as e:
        logger.error(f"Agent error: {str(e)}")
        return f"خطأ في نظام العمليات: {str(e)}"