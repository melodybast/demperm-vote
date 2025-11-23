from typing import Optional, List
from datetime import datetime

from db.repository.result_repository import ResultRepository


class ResultService:
    """
    Service pour la gestion des résultats de votes.
    """

    @staticmethod
    def get_vote_results(
        domain: Optional[str] = None,
        top: int = 100,
        since: Optional[datetime] = None
    ) -> List[dict]:
        """
        Récupère les résultats agrégés des votes.
        
        Args:
            domain: Domaine optionnel pour filtrer les votes
            top: Nombre maximum de résultats (défaut: 100)
            since: Date optionnelle - votes depuis cette date
            
        Returns:
            Liste de résultats avec userId, domain, count, elected, electedAt
        """
        return ResultRepository.get_vote_results(domain, top, since)
