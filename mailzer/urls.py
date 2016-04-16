from django.conf.urls import patterns, url

urlpatterns = patterns(
        '',
        url(r'^preview/(?P<pk>\d+)/$', 'mailzer.views.preview_mail'),
        url(r'^previewplain/(?P<pk>\d+)/$', 'mailzer.views.preview_mail_plain'),
)
