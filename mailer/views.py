from django.core.mail import send_mail
from django.http import HttpResponse
from django.conf import settings

def send_test_email(request):
    send_mail(
        subject='تجربة إرسال إيميل من Django',
        message='تم إرسال هذا البريد بنجاح عبر SendGrid! 🚀',
        recipient_list=['al_nooor20008@hotmail.com'],  # الإيميل الذي تريدين استقباله
        from_email=settings.DEFAULT_FROM_EMAIL,    # تأكدي أنه مطابق للإيميل الموثق
        fail_silently=False,
    )
    return HttpResponse("تم إرسال الإيميل! تحقق من بريدك 🚀")
