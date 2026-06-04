# Internal CMS

نظام Django داخلي لإدارة المستخدمين والعملاء والمهام والمستندات.

## التشغيل

- استخدم Python 3.13 وDjango 5.2 LTS.
- انسخ قيم `.env.example` إلى `.env` واضبط الأسرار الحقيقية.
- اجعل Supabase Storage bucket خاصًا؛ التطبيق يصدر روابط تحميل موقعة وقت الطلب.
- في الإنتاج يجب أن تكون `DEBUG=False` وأن يعمل الموقع عبر HTTPS.

```bash
python -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
python manage.py migrate
python manage.py test
python manage.py check --deploy
```

لا ترفع `.env` أو `db.sqlite3` أو `staticfiles/` إلى Git.
