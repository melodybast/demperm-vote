from rest_framework import serializers


class RecipientSerializer(serializers.Serializer):
    userId = serializers.UUIDField()
    total = serializers.IntegerField()
    byDomain = serializers.DictField(child=serializers.IntegerField())
    usersByDomain = serializers.DictField(child=serializers.UUIDField())
