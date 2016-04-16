from __future__ import absolute_import

from celery import shared_task
from django.utils import timezone
from .models import QueuedMail


@shared_task
def send_mails():
    mails = QueuedMail.objects.filter(send_after__lte=timezone.now(), status=QueuedMail.MAIL_STATUS_QUEUED)
    for mail in mails:
        mail.send()
    return len(mails)
