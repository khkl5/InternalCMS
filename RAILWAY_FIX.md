# خطوات حل مشكلة Railway Deployment

## المشاكل التي تم حلها:

### ✅ 1. تحديث متغيرات البيئة (.env)
- تم تغيير `DEBUG=True` إلى `DEBUG=False` ✓
- تم إضافة `ALLOWED_HOSTS` لقبول طلبات Railway ✓
- تم تفعيل إعدادات الأمان (`SECURE_SSL_REDIRECT`, `SESSION_COOKIE_SECURE`, etc.) ✓

### ✅ 2. تحديث settings.py
- إضافة دعم `DATABASE_URL` (الذي توفره Railway تلقائياً) ✓
- إضافة دعم الوكيل العكسي (`SECURE_PROXY_SSL_HEADER`) ✓

### ✅ 3. ملفات النشر
- `Procfile` - يشغل Gunicorn ويدير المهاجرات ✓
- `runtime.txt` - حدد إصدار Python 3.13 ✓
- `requirements.txt` - يحتوي على جميع الحزم المطلوبة ✓

### ✅ 4. اختبار البيئة
- تم اختبار تشغيل `python manage.py check --deploy` ✓
- جميع التحذيرات الحرجة تم حلها ✓

---

## الخطوات التالية للنشر على Railway:

### 1️⃣ دفع الكود إلى GitHub:
```bash
cd /Users/khawlh/Desktop/dev/InternalCMS/InternalCMS
git add .
git commit -m "Fix Railway deployment configuration"
git push origin main
```

### 2️⃣ إنشاء مشروع على Railway:

1. اذهب إلى https://railway.app
2. اضغط على **"New Project"**
3. اختر **"Deploy from GitHub repo"**
4. ابحث عن **"InternalCMS"** واختره
5. اضغط **"Deploy"**

### 3️⃣ إضافة قاعدة البيانات PostgreSQL:

1. بعد أن يتم إنشاء المشروع، اذهب إلى dashboard
2. اضغط على أيقونة **"+"** لإضافة خدمة
3. اختر **"PostgreSQL"**
4. سيتم إنشاء متغير `DATABASE_URL` تلقائياً ✓

### 4️⃣ تعيين متغيرات البيئة في Railway Dashboard:

في علامة تبويب **"Variables"**، أضف **أو تحديث** المتغيرات التالية:

**مطلوب:**
```
DEBUG=False
DJANGO_SECRET_KEY=<استخدم أداة توليد أدناه>
ALLOWED_HOSTS=<app-name>.railway.app,www.<app-name>.railway.app
CSRF_TRUSTED_ORIGINS=https://<app-name>.railway.app,https://www.<app-name>.railway.app

SUPABASE_URL=<your-supabase-url>
SUPABASE_ANON_KEY=<your-supabase-anon-key>
SUPABASE_SERVICE_KEY=<your-supabase-service-key>
SUPABASE_STORAGE_BUCKET=media

SENDGRID_API_KEY=<your-sendgrid-api-key>
DEFAULT_FROM_EMAIL=<your-email@domain.com>
```

**ملاحظة:** `DATABASE_URL` سيكون موجوداً تلقائياً من PostgreSQL!

### 5️⃣ توليد DJANGO_SECRET_KEY:

استخدم أحد الأوامر التالية:

```bash
# الطريقة 1:
python -c "from django.core.management.utils import get_random_secret_key; print(get_random_secret_key())"

# الطريقة 2:
python -c "import secrets; print(secrets.token_urlsafe(50))"
```

### 6️⃣ تحديث ALLOWED_HOSTS مع اسم تطبيقك:

في Dashboard، اختر اسم فريد لتطبيقك، مثل "internalcms-prod"

ثم حدّث:
```
ALLOWED_HOSTS=internalcms-prod.railway.app
CSRF_TRUSTED_ORIGINS=https://internalcms-prod.railway.app
```

### 7️⃣ بدء النشر:

بعد تعيين جميع المتغيرات:
1. اضغط **"Deploy"** (قد يكون تلقائياً)
2. انتظر انتهاء البناء والنشر
3. ستظهر رسالة النجاح عند الانتهاء

### 8️⃣ التحقق من التطبيق:

1. انتظر تغيير حالة التطبيق إلى "Running" ✓
2. انقر على عنوان URL المُعطى
3. تحقق من أن الموقع يعمل بشكل صحيح

### 9️⃣ إنشاء حساب Admin (اختياري):

إذا لم تكن قد أنشأت مسؤول قاعدة بيانات:

من لوحة تحكم Railway:
1. اذهب إلى علامة تبويب "Logs"
2. بحث عن أمر لإنشاء مسؤول، أو استخدم:

```bash
railway run python manage.py createsuperuser
```

---

## استكشاف الأخطاء الشائعة:

### ❌ خطأ: "ModuleNotFoundError: No module named 'dj_database_url'"
- **الحل:** تأكد من أن `dj-database-url` موجود في `requirements.txt`
- ✓ تم التحقق: موجود بالفعل

### ❌ خطأ: "DJANGO_SECRET_KEY is not configured"
- **الحل:** أضف `DJANGO_SECRET_KEY` في Railway Dashboard Variables
- تأكد من استخدام قيمة طويلة وعشوائية

### ❌ خطأ: "DisallowedHost at /"
- **الحل:** تحديث `ALLOWED_HOSTS` و `CSRF_TRUSTED_ORIGINS` بشكل صحيح
- تأكد من أن اسم النطاق يطابق عنوان URL في Railway

### ❌ خطأ: "Connection refused" للبيانات
- **الحل:** تحقق من أن PostgreSQL add-on موجود في المشروع
- تأكد من أن `DATABASE_URL` موجود في المتغيرات

### ❌ خطأ: "Static files not found (404)"
- **الحل:** تشغيل جمع الملفات الثابتة
- Railway سيفعل هذا تلقائياً من خلال أمر `release` في Procfile

---

## معلومات مفيدة:

- **عنوان لوحة التحكم:** https://railway.app/dashboard
- **وثائق Railway:** https://docs.railway.app
- **وثائق Django للإنتاج:** https://docs.djangoproject.com/en/5.2/howto/deployment/
- **عنوان الموقع:** سيكون شيء من قبيل: `https://internalcms-prod.railway.app`

---

## التحديثات المستقبلية:

بعد النشر الناجح:
- فقط ادفع التغييرات إلى GitHub
- Railway سيقوم بالنشر تلقائياً!

```bash
git add .
git commit -m "Your changes"
git push origin main
# Railway سيبدأ النشر تلقائياً
```
