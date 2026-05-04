
class ConversationMemory:
    def __init__(self, max_messages=20):
        self.sessions = {}
        self.max_messages = max_messages

    def get_history(self, user_id: str):
        """جلب تاريخ المحادثة للمستخدم الحالي"""
        if user_id not in self.sessions:
            self.sessions[user_id] = []
        return self.sessions[user_id]

    def add_message(self, user_id: str, role: str, content: str):
        """إضافة رسالة جديدة للسجل (سواء من المستخدم أو المساعد)"""
        if user_id not in self.sessions:
            self.sessions[user_id] = []
        
        self.sessions[user_id].append({"role": role, "content": content})
        
        # الحفاظ على حجم الذاكرة (قص أقدم الرسائل إذا تجاوزت الحد)
        if len(self.sessions[user_id]) > self.max_messages:
            self.sessions[user_id] = self.sessions[user_id][-self.max_messages:]

    def clear(self, user_id: str):
        """تصفير الذاكرة للمستخدم"""
        self.sessions[user_id] = []

# تصدير نسخة واحدة ثابتة لاستخدامها عبر التطبيق
chat_memory = ConversationMemory()