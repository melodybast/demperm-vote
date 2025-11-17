from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status

from core.dto.recipient import RecipientSerializer
from core.dto.vote_request_dto import VoteRequestSerializer
from core.dto.vote_response_dto import VoteSerializer
from core.services.vote_service import VoteService


class VoteView(APIView):
    """
    POST /votes
    Body: VoteRequest
    Réponse 201: Vote
    """

    def post(self, request):
        serializer = VoteRequestSerializer(data=request.data)
        if not serializer.is_valid():
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

        user = getattr(request, "user", None)
        voter_id = getattr(user, "id", None)

        if voter_id is None:
            return Response(
                {"error": "Unauthorized"},
                status=status.HTTP_401_UNAUTHORIZED,
            )

        data = serializer.validated_data

        vote_dict = VoteService.create_vote(
            voter_id=str(voter_id),
            target_user_id=str(data["targetUserId"]),
            domain=data["domain"],
        )

        response_serializer = VoteSerializer(vote_dict)

        return Response(response_serializer.data, status=status.HTTP_201_CREATED)


class DeleteVoteView(APIView):
    """
    DELETE /votes/{domain}
    Délétion du vote d'un utilisateur pour le domaine précisé

    Réponse 204: Vote supprimé
    Réponse 401: Erreur d'autorisation (jeton manquant ou invalide)
    Réponse 404: Vote introuvable
    """

    def delete(self, request, domain):
        user = getattr(request, "user", None)

        if (voter_id := getattr(user, "id", None)) is None or domain is None:
            return Response(
                {"error": "Unauthorized"}, status=status.HTTP_401_UNAUTHORIZED
            )

        if VoteService.delete_vote(str(voter_id), domain):
            return Response(status=status.HTTP_204_NO_CONTENT)
        return Response({"error": "Vote introuvable"}, status=status.HTTP_404_NOT_FOUND)


class VoterVoteView(APIView):
    """
    Endpoints:
      GET /votes/by-user/me
      GET /votes/by-user/{voterId}
    Query param: ?domain=<domain>
    Response 200: Elector's votes
    """

    def get(self, request, voter_id=None):
        user = getattr(request, "user", None)

        # /me endpoint or invalid
        if voter_id is None and (voter_id := getattr(user, "id", None)) is None:
            return Response(
                {"error": "Unauthorized"},
                status=status.HTTP_401_UNAUTHORIZED,
            )

        domain = request.query_params.get("domain", None)

        electorVotes = VoteService.get_votes_by_voter(str(voter_id), domain)
        response_serializer = VoteSerializer(electorVotes, many=True)
        return Response(response_serializer, status=status.HTTP_200_OK)


class RecipientVoteView(APIView):
    """
    Endpoints:
      GET /votes/for-user/me
      GET /votes/for-user/{userId}
    Query param: ?domain=<domain>
    Response 200: Votes for Recipient
    """

    def get(self, request, user_id=None):
        user = getattr(request, "user", None)

        # /me endpoint or invalid
        if user_id is None and (user_id := getattr(user, "id", None)) is None:
            return Response(
                {"error": "Unauthorized"},
                status=status.HTTP_401_UNAUTHORIZED,
            )

        domain = request.query_params.get("domain", None)

        recipientVotes = VoteService.get_votes_for_target(
            target_id=str(user_id), domain=domain
        )

        response_serializer = RecipientSerializer(recipientVotes)
        return Response(response_serializer, status=status.HTTP_200_OK)
