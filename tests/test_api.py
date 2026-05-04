def test_smtp_direct():
    """
    اختبار مباشر لـ SMTP (بدون الـ Agent)
    """
    import smtplib
    from email.mime.text import MIMEText
    from app.core.config import settings
    
    print("=" * 50)
    print("📧 اختبار SMTP المباشر")
    print("=" * 50)
    
    print(f"SMTP Server: {settings.SMTP_SERVER}")
    print(f"SMTP Port: {settings.SMTP_PORT}")
    print(f"Sender: {settings.COMPANY_EMAIL}")
    print(f"Password: {'✓ موجود' if settings.EMAIL_PASSWORD else '✗ مفقود'}")
    print("=" * 50)
    
    if not settings.EMAIL_PASSWORD:
        print("❌ EMAIL_PASSWORD غير موجود في .env")
        return
    
    try:
        # إنشاء الرسالة
        msg = MIMEText("هذا اختبار مباشر لـ SMTP من مشروع الوكيل الذكي", "plain", "utf-8")
        msg['From'] = settings.COMPANY_EMAIL
        msg['To'] = "bakr.muqbil@gmail.com"
        msg['Subject'] = "🧪 اختبار SMTP مباشر"
        
        # الاتصال والإرسال
        print("🔄 جاري الاتصال بخادم SMTP...")
        server = smtplib.SMTP(settings.SMTP_SERVER, settings.SMTP_PORT)
        server.starttls()
        print("✅ تم إنشاء الاتصال المشفر")
        
        print("🔄 جاري تسجيل الدخول...")
        server.login(settings.COMPANY_EMAIL, settings.EMAIL_PASSWORD)
        print("✅ تم تسجيل الدخول بنجاح")
        
        print("🔄 جاري إرسال الرسالة...")
        server.send_message(msg)
        server.quit()
        
        print("\n✅ ✅ ✅ تم إرسال الإيميل بنجاح عبر الاختبار المباشر!")
        print("📬 تفقد صندوق الوارد: bakr.muqbil@gmail.com")
        
    except Exception as e:
        print(f"\n❌ فشل الإرسال: {e}")
