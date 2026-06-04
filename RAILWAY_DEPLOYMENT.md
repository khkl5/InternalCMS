# دليل النشر على Railway

## الخطوات الأساسية لنشر المشروع على Railway

### 1. إنشاء حساب على Railway
1. اذهب إلى [railway.app](https://railway.app)
2. قم بإنشاء حساب جديد أو تسجيل الدخول
3. ربط حسابك بـ GitHub

### 2. إنشاء مشروع جديد على Railway
1. انقر على "New Project"
2. اختر "Deploy from GitHub repo"
3. اختر هذا المستودع (InternalCMS)

### 3. إضافة قاعدة البيانات
1. في لوحة التحكم، انقر على "+" لإضافة خدمة جديدة
2. اختر "PostgreSQL"
3. سيتم إنشاء متغيرات البيئة تلقائياً

### 4. تعيين متغيرات البيئة
في قسم Variables في Railway، أضف المتغيرات التالية:

**المتغيرات المطلوبة:**
```
DEBUG=False
DJANGO_SECRET_KEY=<قيمة عشوائية طويلة - يمكن توليدها>
ALLOWED_HOSTS=<yourdomain.railway.app>,www.<yourdomain>.railway.app
CSRF_TRUSTED_ORIGINS=https://<yourdomain>.railway.app,https://www.<yourdomain>.railway.app

USE_POSTGRES=True

SUPABASE_URL=<your-supabase-url>
SUPABASE_ANON_KEY=<your-supabase-anon-key>
SUPABASE_SERVICE_KEY=<your-supabase-service-key>
SUPABASE_STORAGE_BUCKET=media

EMAIL_HOST=smtp.sendgrid.net
EMAIL_PORT=587
EMAIL_HOST_USER=apikey
SENDGRID_API_KEY=<your-sendgrid-api-key>
EMAIL_USE_TLS=True
DEFAULT_FROM_EMAIL=<your-email@domain.com>
```

**ملاحظة:** Railway سيوفر متغير `DATABASE_URL` تلقائياً عند إضافة PostgreSQL.

### 5. توليد DJANGO_SECRET_KEY
يمكنك استخدام الأمر التالي لتوليد مفتاح سري آمن:
```bash
python -c "from django.core.management.utils import get_random_secret_key; print(get_random_secret_key())"
```

أو في Python:
```python
import secrets
print(secrets.token_urlsafe(50))
```

### 6. التحقق من التكوين
قبل الدفع، تأكد من:
- ✅ ملف `Procfile` موجود
- ✅ ملف `runtime.txt` موجود
- ✅ جميع متغيرات البيئة المطلوبة مضبوطة
- ✅ ملف `.env` مستبعد من Git (موجود في .gitignore)

### 7. نشر المشروع
1. قم بدفع التغييرات إلى GitHub:
```bash
git add .
git commit -m "Add Railway deployment configuration"
git push origin main
```

2. Railway سيبدأ النشر تلقائياً
3. انتظر انتهاء النشر (ستظهر حالة البناء في لوحة التحكم)

### 8. تشغيل المهام الأولى
بعد النشر الناجح، قد تحتاج إلى تشغيل الأوامر التالية:
- إنشاء مسؤول (superuser):
```bash
python manage.py createsuperuser
```
- جمع الملفات الثابتة:
```bash
python manage.py collectstatic --noinput
```

Railway سيقوم بهذا تلقائياً من خلال أوامر `release` في الملف `Procfile`.

### 9. التحقق من الموقع
- انتقل إلى اسم النطاق الخاص بك على Railway
- تحقق من أن الموقع يعمل بشكل صحيح
- سجل الدخول إلى لوحة الإدارة في `/admin`

### 10. المراقبة والسجلات
في لوحة تحكم Railway، يمكنك:
- عرض السجلات (Logs) في الوقت الفعلي
- مراقبة استهلاك الموارد
- إعادة تشغيل التطبيق إذا لزم الأمر

## استكشاف الأخطاء

### خطأ: DJANGO_SECRET_KEY غير مُعرَّف
- تأكد من إضافة `DJANGO_SECRET_KEY` في متغيرات البيئة

### خطأ: قاعدة البيانات غير موصولة
- تحقق من أن PostgreSQL تعمل في Railway
- تحقق من متغير `DATABASE_URL`
- شغّل `python manage.py migrate` يدويًا إذا لزم الأمر

### خطأ: الملفات الثابتة غير موجودة
- تأكد من تشغيل `python manage.py collectstatic`
- تحقق من أن `STATIC_ROOT` و `STATIC_URL` مضبوطة بشكل صحيح

## تحديثات مستقبلية
- لتحديث الموقع، ما عليك سوى دفع التغييرات إلى GitHub
- Railway سيقوم بالنشر تلقائياً

## موارد مفيدة
- [وثائق Railway](https://docs.railway.app)
- [وثائق Django للإنتاج](https://docs.djangoproject.com/en/5.2/howto/deployment/)
- [دليل Gunicorn](https://docs.gunicorn.org)
