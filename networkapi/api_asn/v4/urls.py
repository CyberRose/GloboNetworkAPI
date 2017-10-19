# -*- coding: utf-8 -*-
from django.conf.urls import patterns
from django.conf.urls import url

from networkapi.api_asn.v4 import views

urlpatterns = patterns(
    '',
    url(r'^asn/((?P<obj_ids>[;\w]+)/)?$',
        views.AsnDBView.as_view()),
)
