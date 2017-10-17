# -*- coding: utf-8 -*-
import logging

from django.db.models import get_model
from rest_framework import serializers

from networkapi.util.geral import get_app
from networkapi.util.serializers import DynamicFieldsModelSerializer

log = logging.getLogger(__name__)


class NeighborV4Serializer(DynamicFieldsModelSerializer):

    soft_reconfiguration = serializers.Field(source='soft_reconfiguration')

    community = serializers.Field(source='community')

    remove_private_as = serializers.Field(source='remove_private_as')

    next_hop_self = serializers.Field(source='next_hop_self')

    created = serializers.Field(source='created')

    class Meta:
        Neighbor = get_model('api_neighbor', 'Neighbor')
        model = Neighbor
        fields = (
            'id',
            'remote_as',
            'remote_ip',
            'password',
            'maximum_hops',
            'timer_keepalive',
            'timer_timeout',
            'description',
            'soft_reconfiguration',
            'community',
            'remove_private_as',
            'next_hop_self',
            'kind',
            'created',
            'virtual_interface'
        )

        default_fields = fields

        basic_fields = fields

        details_fields = fields

