from drf_spectacular.utils import (
    extend_schema,
    OpenApiResponse,
    OpenApiParameter,
    OpenApiTypes,
)

from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status

from core.dto.publication_request_dto import PublicationUpdateRequestSerializer
from core.dto.publication_response_dto import PublicationSettingSerializer
from core.services.publication_service import PublicationService


class PublicationSettingView(APIView):
    """
    GET /api/publication/{userId}
    PUT /api/publication/{userId}
    """

    @extend_schema(
        tags=["Preferences"],
        parameters=[
            OpenApiParameter(
                name="userId",
                description="ID de l'utilisateur dont on souhaite récupérer le paramètre de publication",
                required=True,
                type=OpenApiTypes.STR,
                location=OpenApiParameter.PATH,
            )
        ],
        responses={
            200: PublicationSettingSerializer,
            401: OpenApiResponse(description="Unauthorized"),
        },
        description="Récupère les paramètres de publication d’un utilisateur.",
    )
    def get(self, request, userId):
        user = getattr(request, "user", None)
        current_user_id = getattr(user, "id", None)

        if current_user_id is None:
            return Response(
                {"error": "Unauthorized"},
                status=status.HTTP_401_UNAUTHORIZED,
            )

        setting = PublicationService.get_publication_setting(userId)
        response_serializer = PublicationSettingSerializer(setting)
        
        return Response(response_serializer.data, status=status.HTTP_200_OK)

    @extend_schema(
        tags=["Preferences"],
        parameters=[
            OpenApiParameter(
                name="userId",
                description="ID de l'utilisateur dont on souhaite modifier le paramètre de publication",
                required=True,
                type=OpenApiTypes.STR,
                location=OpenApiParameter.PATH,
            )
        ],
        request=PublicationUpdateRequestSerializer,
        responses={
            200: PublicationSettingSerializer,
            400: OpenApiResponse(description="Requête invalide"),
            401: OpenApiResponse(description="Unauthorized"),
            403: OpenApiResponse(description="Forbidden: cannot modify another user's settings"),
        },
        description=(
            "Met à jour les paramètres de publication de l’utilisateur authentifié. "
            "publishVotes: bool — publish automatique si True. threshold géré séparément."
        ),
    )
    def put(self, request, userId):
        user = getattr(request, "user", None)
        current_user_id = getattr(user, "id", None)

        if current_user_id is None:
            return Response(
                {"error": "Unauthorized"},
                status=status.HTTP_401_UNAUTHORIZED,
            )

        if str(current_user_id) != str(userId):
            return Response(
                {"error": "Forbidden: You can only modify your own publication settings"},
                status=status.HTTP_403_FORBIDDEN,
            )

        serializer = PublicationUpdateRequestSerializer(data=request.data)
        if not serializer.is_valid():
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

        publish_votes = serializer.validated_data["publishVotes"]
        updated_setting = PublicationService.update_publication_setting(
            userId, publish_votes
        )

        response_serializer = PublicationSettingSerializer(updated_setting)
        
        return Response(response_serializer.data, status=status.HTTP_200_OK)
