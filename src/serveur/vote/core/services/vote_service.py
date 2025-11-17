from typing import Optional

import uuid
from django.utils import timezone

from db.repository.vote_repository import VoteRepository


class VoteService:
    @staticmethod
    def create_vote(voter_id: str, target_user_id: str, domain: str) -> dict:
        """
        Crée un vote + le persiste dans Neo4j, puis renvoie un dict
        """
        vote = {
            "id": uuid.uuid4(),
            "voterId": voter_id,
            "targetUserId": target_user_id,
            "domain": domain,
            "createdAt": timezone.now(),
        }

        VoteRepository.save_vote(vote)

        return vote

    @staticmethod
    def delete_vote(voter_id: str, domain: str) -> bool:
        """
        Délétion du vote d'un utilisateur pour le domaine précisé.
        """
        return VoteRepository.delete_vote(voter_id, domain)

    @staticmethod
    def get_votes_by_voter(user_id: str, domain: Optional[str] = None) -> list[dict]:
        """
        Récupère la liste de votes effectués par un utilisateur.
        """
        return VoteRepository.get_votes_by_voter(user_id, domain)

    @staticmethod
    def get_votes_for_target(target_id: str, domain: Optional[str] = None) -> dict:
        """
        Récupère le nombre de votes qu'a reçu un utilisateur.
        """
        votes = VoteRepository.get_votes_for_target(target_id, domain)
        domain_distr = {}

        for vote in votes:
            d = vote["domain"]
            domain_distr[d] = domain_distr.get(d, 0) + 1

        return {
            "userId": target_id,
            "total": len(votes),
            "byDomain": domain_distr,
        }
