from django.contrib import admin
from .models import MailTemplate, QueuedMail


class MailTemplateAdmin(admin.ModelAdmin):
    list_display = ('id', 'name', 'description')
    list_filter = ('id', 'name')
    search_fields = ('id', 'name', 'description')
    readonly_fields = ('admin_preview',)
    fields = ('name', 'description', 'subject', 'code', 'plain_code', 'admin_preview', 'reply_address')


class QueuedMailAdmin(admin.ModelAdmin):
    list_display = ('id', 'mail_from', 'mail_to', 'template', 'send_after', 'created', 'status')
    list_filter = ('id', 'mail_from', 'mail_to', 'template', 'send_after', 'created', 'status')
    search_fields = ('id', 'mail_from', 'mail_to', 'template', 'send_after', 'created')
    readonly_fields = ('created', 'send_after')
    fields = ('mail_from', 'mail_to', 'template', 'context_vars', 'status')


admin.site.register(MailTemplate, MailTemplateAdmin)
admin.site.register(QueuedMail, QueuedMailAdmin)
