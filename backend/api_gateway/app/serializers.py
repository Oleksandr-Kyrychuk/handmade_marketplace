# /mnt/d/handmade_marketplace/backend/api_gateway/app/serializers.py
from rest_framework import serializers

class HealthCheckSerializer(serializers.Serializer):
    status = serializers.CharField(max_length=10)  # 'ok' або 'error'
    services = serializers.DictField(
        child=serializers.DictField(
            child=serializers.CharField(allow_null=True)
        )
    )

class ProxyErrorSerializer(serializers.Serializer):
    error = serializers.CharField(max_length=100)