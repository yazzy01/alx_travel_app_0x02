from celery import shared_task
from django.core.mail import send_mail

@shared_task
def send_email_task(subject, message, from_email, recipient_list):
    """
    Task to send an email asynchronously
    """
    send_mail(
        subject,
        message,
        from_email,
        recipient_list,
        fail_silently=False
    )
    return f"Email sent to {', '.join(recipient_list)}" 