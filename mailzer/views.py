import sys
from django.http import HttpResponse
from django.shortcuts import get_object_or_404
from .models import MailTemplate
from django.conf import settings


def preview_mail(request, pk):
    context = {}
    for key, module, clsname in settings.EXTRA_MAIL_CONTEXT_CLASSES:
        __import__(module)
        cls = getattr(sys.modules[module], clsname)
        context[key] = cls.objects.order_by('?').first()
    return HttpResponse(get_object_or_404(MailTemplate, pk=pk).render_html(to_mail='example@example.com', **context))


def preview_mail_plain(request, pk):
    context = {}
    for key, module, clsname in settings.EXTRA_MAIL_CONTEXT_CLASSES:
        __import__(module)
        cls = getattr(sys.modules[module], clsname)
        context[key] = cls.objects.order_by('?').first()
    return HttpResponse(get_object_or_404(MailTemplate, pk=pk).render_plain(to_mail='example@example.com', **context),
                        content_type='text/plain')
