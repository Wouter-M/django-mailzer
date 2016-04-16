import json
import sys
from datetime import timedelta

from django.core.mail import EmailMultiAlternatives
from django.core.urlresolvers import reverse_lazy
from django.db import models
from django.template import Template, Context
from django.utils import timezone
from django.utils.translation import ugettext as _


class QueuedMail(models.Model):
    MAIL_STATUS_QUEUED = 'queued'
    MAIL_STATUS_SEND = 'send'
    MAIL_STATUS_ERROR = 'error'
    MAIL_STATUS = (
        (MAIL_STATUS_QUEUED, _("The mail is waiting in the queue")),
        (MAIL_STATUS_SEND, _("The mail has been send successfully")),
        (MAIL_STATUS_ERROR, _("There was an error when sending this email"))
    )
    mail_to = models.EmailField()
    mail_from = models.EmailField(blank=True, null=True)
    template = models.ForeignKey('mailzer.MailTemplate')
    send_after = models.DateTimeField(auto_now=True)
    created = models.DateTimeField(auto_now=True, editable=False)
    context_vars = models.TextField(default='{}')
    status = models.CharField(max_length=10, choices=MAIL_STATUS, default=MAIL_STATUS_QUEUED)

    def send(self):
        if self.mail_from is not None:
            success = self.template.send(self.mail_to, self.mail_from, **unpack_objects(json.loads(self.context_vars)))
        else:
            success = self.template.send(self.mail_to, **unpack_objects(json.loads(self.context_vars)))
        if success:
            self.status = self.MAIL_STATUS_SEND
        else:
            self.status = self.MAIL_STATUS_ERROR
        self.save()

    @staticmethod
    def get_nr_of_send_mails(mail, days=30, template=None):
        """
        :param mail: The mail address of the person
        :type mail: basestring
        :type template: basestring|None
        :param days: The nr of days to search for. Can be larger than now(), to search for queued mails
        :param template: The template to search for
        :rtype: int
        :return: The nr of mails matching the query send to the user
        """
        res = QueuedMail.objects.filter(mail_to__iexact=mail, send_after__gte=timezone.now() - timedelta(days=days))
        if template is not None:
            res = res.filter(template__name=template)
        return res.count()


def pack_objects(objects):
    """Given a dictionary of key values. Where values are primitives (like int and str) or Django objects with a pk
       attribute, pack the objects for storage in database. """
    result = {}
    for key, value in objects.iteritems():
        if value is None:
            continue
        if hasattr(value, '_wrapped'):
            # This is a Django lazy object, get the 'real' object
            value = value._wrapped
        result[key] = {}
        result[key]['class'] = value.__class__.__name__
        if hasattr(value, '__module__'):
            result[key]['module'] = value.__module__
        if hasattr(value, 'pk'):
            result[key]['pk'] = value.pk
        else:
            result[key]['value'] = value
    return result


def unpack_objects(objects):
    result = {}
    for key, value in objects.iteritems():
        if 'pk' in value.keys():
            __import__(value['module'])
            cls = getattr(sys.modules[value['module']], value['class'])
            result[key] = cls.objects.get(pk=value['pk'])
        else:
            result[key] = value['value']
    return result


class MailTemplate(models.Model):
    name = models.CharField(max_length=50, unique=True, db_index=True)
    description = models.CharField(max_length=200, blank=True)
    subject = models.CharField(max_length=150)
    code = models.TextField()
    plain_code = models.TextField()
    reply_address = models.EmailField()

    def render_html(self, *args, **kwargs):
        t = Template(self.code)
        kwargs['reply_address'] = self.reply_address
        context = Context(kwargs)
        return t.render(context)

    def render_plain(self, *args, **kwargs):
        t = Template(self.plain_code)
        kwargs['reply_address'] = self.reply_address
        context = Context(kwargs)
        return t.render(context)

    def admin_preview(self):
        if self.pk is not None:
            return u"<a href='" + str(
                reverse_lazy('mailzer.views.preview_mail', args=[self.pk])) + "'>Preview template</a> | " + \
                   "<a href='" + str(
                reverse_lazy('mailzer.views.preview_mail_plain', args=[self.pk])) + "'>Preview template plaintext</a>"
        else:
            return "N/A"

    admin_preview.short_description = 'Preview'
    admin_preview.allow_tags = True

    def enqueue(self, to_addr, from_addr=None, **kwargs):
        QueuedMail.objects.create(mail_to=to_addr, mail_from=from_addr,
                                  template=self, context_vars=json.dumps(pack_objects(kwargs)))

    def send(self, to_addr, from_addr, **kwargs):
        kwargs['to_mail'] = to_addr
        html_content = self.render_html(**kwargs)
        plain_content = self.render_plain(**kwargs)
        if not isinstance(to_addr, list):
            to_addr = [to_addr]
        msg = EmailMultiAlternatives(self.subject, plain_content, from_addr, to_addr,
                                     headers={'Reply-To': self.reply_address})
        msg.attach_alternative(html_content, "text/html")
        return msg.send()

    def __str__(self):
        return self.name
