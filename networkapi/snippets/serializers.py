from rest_framework import serializers
from pools.models import ServerPool


class ServerPoolSerializer(serializers.ModelSerializer):
    class Meta:
        model = ServerPool
        fields = ('id', 'identifier', 'default_port',)
