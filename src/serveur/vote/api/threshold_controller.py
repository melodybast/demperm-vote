from drf_spectacular.utils import (
    extend_schema,
    OpenApiResponse,
    OpenApiParameter,
    OpenApiTypes,
)

from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status

from core.dto.threshold_request_dto import ThresholdUpdateRequestSerializer
from core.dto.threshold_response_dto import ThresholdSettingSerializer
from core.services.threshold_service import ThresholdService


class ThresholdSettingView(APIView):
    """
    GET /api/threshold/{userId}
    PUT /api/threshold/{userId}
    """
    
    @extend_schema(
        tags=["Preferences"],
        parameters=[
            OpenApiParameter(
                name="userId",
                description="ID de l'utilisateur dont on souhaite récupérer le seuil",
                required=True,
                type=OpenApiTypes.STR,
                location=OpenApiParameter.PATH,
            )
        ],
        responses={
            200: ThresholdSettingSerializer,
            401: OpenApiResponse(description="Unauthorized"),
        },
        description="Récupère le seuil de publication d'un utilisateur.",
    )
    def get(self, request, userId):
        # Vérification de l'authentification
        user = getattr(request, "user", None)
        current_user_id = getattr(user, "id", None)

        if current_user_id is None:
            return Response(
                {"error": "Unauthorized"},
                status=status.HTTP_401_UNAUTHORIZED,
            )

        setting = ThresholdService.get_threshold_setting(userId)
        response_serializer = ThresholdSettingSerializer(setting)
        
        return Response(response_serializer.data, status=status.HTTP_200_OK)

    @extend_schema(
        tags=["Preferences"],
        parameters=[
            OpenApiParameter(
                name="userId",
                description="ID de l'utilisateur dont on souhaite modifier le seuil",
                required=True,
                type=OpenApiTypes.STR,
                location=OpenApiParameter.PATH,
            )
        ],
        request=ThresholdUpdateRequestSerializer,
        responses={
            200: ThresholdSettingSerializer,
            400: OpenApiResponse(description="Requête invalide"),
            401: OpenApiResponse(description="Unauthorized"),
            403: OpenApiResponse(description="Forbidden: cannot modify another user's settings"),
        },
        description="Met à jour le seuil de publication de l’utilisateur authentifié.",
    )
    def put(self, request, userId):
        # Vérification de l'authentification
        user = getattr(request, "user", None)
        current_user_id = getattr(user, "id", None)

        if current_user_id is None:
            return Response(
                {"error": "Unauthorized"},
                status=status.HTTP_401_UNAUTHORIZED,
            )

        if str(current_user_id) != str(userId):
            return Response(
                {"error": "Forbidden: You can only modify your own threshold settings"},
                status=status.HTTP_403_FORBIDDEN,
            )

        serializer = ThresholdUpdateRequestSerializer(data=request.data)
        if not serializer.is_valid():
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

        threshold = serializer.validated_data["threshold"]
        updated_setting = ThresholdService.update_threshold_setting(
            userId, threshold
        )
        response_serializer = ThresholdSettingSerializer(updated_setting)
        
        return Response(response_serializer.data, status=status.HTTP_200_OK)
