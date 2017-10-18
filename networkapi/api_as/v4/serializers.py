# -*- coding: utf-8 -*-
from django.db.models import get_model
from rest_framework import serializers

from networkapi.util.geral import get_app
from networkapi.util.serializers import DynamicFieldsModelSerializer


class AsV4Serializer(DynamicFieldsModelSerializer):

    class Meta:
        As_ = get_model('api_as', 'As')
        model = As_

        fields = (
            'id',
            'name',
            'description'
        )

        basic_fields = fields

        default_fields = fields

        details_fields = fields

