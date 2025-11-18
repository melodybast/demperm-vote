from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status

from core.dto.stats_response_dto import StatsDailySerializer
from core.services.stats_service import StatsService


class StatsDailyView(APIView):
    """
    GET /stats/votes/daily/{userId}
    Récupère les paramètres de publication d'un utilisateur.
    200: PublicationSetting avec userId et publishVotes
    404: Not found
    """

    def get(self, request, userId):
        user = getattr(request, "user", None)
        current_user_id = getattr(user, "id", None)

        if current_user_id is None:
            return Response(
                {"error": "Unauthorized"},
                status=status.HTTP_404_NOT_FOUND,
            )

        res = StatsService.get_daily_stats(current_user_id)
        response_serializer = StatsDailySerializer(res)
        
        return Response(response_serializer.data, status=status.HTTP_200_OK)
