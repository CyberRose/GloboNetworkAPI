# -*- coding: utf-8 -*-
from django.db.models import get_model
from rest_framework import serializers

from networkapi.util.geral import get_app
from networkapi.util.serializers import DynamicFieldsModelSerializer


class AsV4Serializer(DynamicFieldsModelSerializer):

    as_ip_equipment = serializers.SerializerMethodField('get_as_ip_equipment')

    class Meta:
        As_ = get_model('api_as', 'As')
        model = As_

        fields = (
            'id',
            'name',
            'description',
            'as_ip_equipment'
        )

        basic_fields = (
            'id',
            'name',
            'description'
        )

        default_fields = fields

        details_fields = fields

    def get_as_ip_equipment(self, obj):
        return self.extends_serializer(obj, 'as_ip_equipment')

    def get_serializers(self):

        if not self.mapping:
            self.mapping = {
                'as_ip_equipment': {
                    'serializer': AsIpEquipmentV4Serializer,
                    'kwargs': {
                        'many': True,
                    },
                    'obj': 'as_ip_equipment'
                },
                'as_ip_equipment__basic': {
                    'serializer': AsIpEquipmentV4Serializer,
                    'kwargs': {
                        'many': True,
                        'kind': 'basic'
                    },
                    'obj': 'as_ip_equipment'
                },
                'as_ip_equipment__details': {
                    'serializer': AsIpEquipmentV4Serializer,
                    'kwargs': {
                        'many': True,
                        'kind': 'details'
                    },
                    'obj': 'as_ip_equipment'
                }
            }


class AsIpEquipmentV4Serializer(DynamicFieldsModelSerializer):

    asn = serializers.SerializerMethodField('get_asn')
    ipv4_equipment = serializers.SerializerMethodField('get_ipv4_equipment')
    ipv6_equipment = serializers.SerializerMethodField('get_ipv6_equipment')

    class Meta:

        as_ip_equipment = get_model('api_as', 'AsIpEquipment')
        model = as_ip_equipment

        fields = (
            'id',
            'asn',
            'ipv4_equipment',
            'ipv6_equipment'
        )

        basic_fields = fields

        default_fields = fields

        details_fields = fields

    def get_asn(self, obj):
        return self.extends_serializer(obj, 'asn')

    def get_ipv4_equipment(self, obj):
        return self.extends_serializer(obj, 'ipv4_equipment')

    def get_ipv6_equipment(self, obj):
        return self.extends_serializer(obj, 'ipv6_equipment')

    def get_serializers(self):

        ip_slz = get_app('api_ip', module_label='v4.serializers')

        if not self.mapping:
            self.mapping = {
                'asn': {
                    'obj': 'asn_id'
                },
                'asn__basic': {
                    'serializer': AsV4Serializer,
                    'kwargs': {
                        'kind': 'basic',
                        'prohibited': (
                            'as_ip_equipment__basic',
                        )
                    },
                    'obj': 'asn'
                },
                'asn__details': {
                    'serializer': AsV4Serializer,
                    'kwargs': {
                        'kind': 'details',
                        'prohibited': (
                            'as_ip_equipment__details',
                        )
                    },
                    'obj': 'asn'
                },
                'ipv4_equipment': {
                    'obj': 'ipv4_equipment_id'
                },
                'ipv4_equipment__basic': {
                    'serializer': ip_slz.IPv4EquipmentV4Serializer,
                    'kwargs': {
                        'kind': 'basic'
                    },
                    'obj': 'ipv4_equipment'
                },
                'ipv4_equipment__details': {
                    'serializer': ip_slz.IPv4EquipmentV4Serializer,
                    'kwargs': {
                        'kind': 'details'
                    },
                    'obj': 'ipv4_equipment'
                },
                'ipv6_equipment': {
                    'obj': 'ipv6_equipment_id'
                },
                'ipv6_equipment__basic': {
                    'serializer': ip_slz.IPv6EquipmentV4Serializer,
                    'kwargs': {
                        'kind': 'basic'
                    },
                    'obj': 'ipv6_equipment'
                },
                'ipv6_equipment__details': {
                    'serializer': ip_slz.IPv6EquipmentV4Serializer,
                    'kwargs': {
                        'kind': 'details'
                    },
                    'obj': 'ipv6_equipment'
                }
            }

