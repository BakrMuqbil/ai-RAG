class ConversationMemory:
    def __init__(self, max_messages=20, max_summary=30):
        self.sessions = {}
        self.summary_sessions = {}
        self.max_messages = max_messages
        self.max_summary = max_summary

    # -------------------------------
    # CHAT HISTORY (للمحادثة فقط)
    # -------------------------------
    def get_history(self, user_id: str):
        if user_id not in self.sessions:
            self.sessions[user_id] = []
        return self.sessions[user_id]

    def add_message(self, user_id: str, role: str, content: str):
        if user_id not in self.sessions:
            self.sessions[user_id] = []

        # ❌ لا تخزن JSON أو نصوص ضخمة
        clean_content = content

        if isinstance(content, str) and len(content) > 500:
            clean_content = content[:500] + "..."

        self.sessions[user_id].append({
            "role": role,
            "content": clean_content
        })

        if len(self.sessions[user_id]) > self.max_messages:
            self.sessions[user_id] = self.sessions[user_id][-self.max_messages:]

    # -------------------------------
    # SUMMARY MEMORY (الأهم 🔥)
    # -------------------------------
    def add_summary_event(self, user_id: str, event: str):
        if user_id not in self.summary_sessions:
            self.summary_sessions[user_id] = []

        self.summary_sessions[user_id].append(event)

        if len(self.summary_sessions[user_id]) > self.max_summary:
            self.summary_sessions[user_id] = self.summary_sessions[user_id][-self.max_summary:]

    def get_summary_context(self, user_id: str):
        if user_id not in self.summary_sessions:
            return ""

        return "\n".join(self.summary_sessions[user_id])

    # -------------------------------
    def clear(self, user_id: str):
        self.sessions[user_id] = []
        self.summary_sessions[user_id] = []


chat_memory = ConversationMemory()