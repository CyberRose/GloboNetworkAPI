# -*- coding:utf-8 -*-
from django.conf.urls import patterns
from django.conf.urls import url

from networkapi.api_environment import views

urlpatterns = patterns(
    '',
    url(r'^v3/environment/((?P<environment_ids>[;\w]+)/)?$', views.EnvironmentDBView.as_view()),  # TODO doc
    url(r'^v3/environment/environment-vip/((?P<environment_vip_id>\d+)/)?$', views.EnvEnvVipRelatedView.as_view()),
)
