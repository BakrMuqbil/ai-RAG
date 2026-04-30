# استخدام نسخة بايثون خفيفة جداً
FROM python:3.11-slim

# منع بايثون من إنشاء ملفات .pyc وتفعيل مخرجات الـ log فوراً
ENV PYTHONDONTWRITEBYTECODE 1
ENV PYTHONUNBUFFERED 1

# تحديد مجلد العمل داخل الحاوية
WORKDIR /app

# تثبيت الأدوات الأساسية للنظام
RUN apt-get update && apt-get install -y \
    build-essential \
    && rm -rf /var/lib/apt/lists/*

# نسخ ملف المتطلبات وتثبيتها
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# نسخ ملفات المشروع بالكامل
COPY . .

# إنشاء مجلد البيانات وقاعدة البيانات إذا لم يوجدوا
RUN mkdir -p data db

# تحديد المنفذ (Port)
EXPOSE 8000

# أمر تشغيل السيرفر
CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8000"]