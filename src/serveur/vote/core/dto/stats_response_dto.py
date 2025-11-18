from rest_framework import serializers


class StatsDailyField(serializers.Serializer):
    date = serializers.DateField()
    count = serializers.IntegerField()

class StatsDailySerializer(serializers.Serializer):
    id = serializers.UUIDField()
    voterId = serializers.UUIDField()
    targetUserId = serializers.UUIDField()
    domain = serializers.CharField(max_length=100)
    createdAt = serializers.DateTimeField()

    userId = serializers.UUIDField()
    daily = serializers.ListField(child=StatsDailyField())
    delta = serializers.IntegerField()
