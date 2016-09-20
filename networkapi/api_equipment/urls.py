# -*- coding: utf-8 -*-
from __future__ import absolute_import

from django.conf.urls import patterns
from django.conf.urls import url

from networkapi.api_equipment import views


urlpatterns = patterns(
    '',
    url(r'^equipment/get_routers_by_environment/(?P<env_id>\d+)/$', views.EquipmentRoutersView.as_view()),  # TODO doc

    url(r'^v3/equipment/environment/(?P<env_id>\d+)/$', views.EquipmentEnvView.as_view()),  # TODO doc GET
)
