# -*- coding: utf-8 -*-
from django.conf.urls import patterns
from django.conf.urls import include
from django.conf.urls import url

urlpatterns = patterns(
    '',
    url(r'^v4/', include('networkapi.api_virtual_interface.v4.urls')),

)
