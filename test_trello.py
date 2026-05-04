#!/usr/bin/env python3
import json
from app.services.tools import create_operational_task
from app.core.config import settings

def test_trello():
    print("=" * 50)
    print("📋 التحقق من إعدادات Trello")
    print("=" * 50)
    print(f"API Key: {'✓' if settings.TRELLO_API_KEY else '✗'}")
    print(f"Token: {'✓' if settings.TRELLO_TOKEN else '✗'}")
    print(f"Board ID: {settings.TRELLO_BOARD_ID}")
    print(f"List ID: {settings.TRELLO_LIST_ID}")
    print("=" * 50)

    if not settings.TRELLO_LIST_ID:
        print("❌ TRELLO_LIST_ID مفقود من ملف .env")
        return

    print("\n🚀 جاري إنشاء مهمة في Trello...")
    result = create_operational_task(
        title="اختبار من الوكيل الذكي",
        description="هذه مهمة تم إنشاؤها تلقائياً بواسطة الـ Agent",
        priority="High"
    )

    print("\n🔧 النتيجة:")
    print(json.dumps(result, ensure_ascii=False, indent=2))

    if result.get("status") == "success" and "url" in result:
        print(f"\n✅ تم إنشاء المهمة بنجاح! افتح الرابط: {result['url']}")
    elif result.get("status") == "error":
        print(f"\n❌ فشل إنشاء المهمة: {result.get('message')}")

if __name__ == "__main__":
    test_trello()
