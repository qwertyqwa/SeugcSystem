from rest_framework import serializers

from .models import Ticket, TicketAnalysis, TicketStatus


class TicketAnalysisSerializer(serializers.ModelSerializer):
    class Meta:
        model = TicketAnalysis
        fields = (
            "priority_label",
            "priority_score",
            "priority_prob_low",
            "priority_prob_medium",
            "priority_prob_high",
            "sentiment_label",
            "sentiment_score",
        )


class TicketAuthorSerializer(serializers.Serializer):
    id = serializers.IntegerField()
    username = serializers.CharField()
    email = serializers.EmailField()


class TicketSerializer(serializers.ModelSerializer):
    analysis = TicketAnalysisSerializer(read_only=True)
    author = serializers.SerializerMethodField()

    class Meta:
        model = Ticket
        fields = (
            "id",
            "text",
            "status",
            "created_at",
            "updated_at",
            "author",
            "analysis",
        )

    def get_author(self, obj):
        return TicketAuthorSerializer(
            {
                "id": obj.user_id,
                "username": obj.user.username,
                "email": obj.user.email,
            }
        ).data


class TicketCreateSerializer(serializers.Serializer):
    text = serializers.CharField(max_length=10000)


class TicketStatusUpdateSerializer(serializers.Serializer):
    status = serializers.ChoiceField(choices=TicketStatus.choices)


class AnalyzeTextSerializer(serializers.Serializer):
    text = serializers.CharField(max_length=10000)
