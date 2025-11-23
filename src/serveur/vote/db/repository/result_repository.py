from app.neo4j_config import get_driver
from datetime import datetime
from typing import Optional, List


class ResultRepository:
    """
    Repository pour récupérer les résultats agrégés des votes.
    
    Récupère le classement des utilisateurs par nombre de votes reçus,
    avec filtrage optionnel par domaine et date.
    """

    @staticmethod
    def get_vote_results(
        domain: Optional[str] = None,
        top: int = 100,
        since: Optional[datetime] = None
    ) -> List[dict]:
        """
        Récupère les résultats des votes agrégés.
        
        Args:
            domain: Domaine optionnel pour filtrer les votes
            top: Nombre maximum de résultats à retourner (défaut: 100)
            since: Date optionnelle - ne retourner que les votes depuis cette date
            
        Returns:
            Liste de dict contenant userId, domain, count, elected, electedAt
        """
        driver = get_driver()
        with driver.session() as session:
            results = session.execute_read(
                ResultRepository._get_vote_results_tx,
                domain,
                top,
                since
            )
            return results

    @staticmethod
    def _get_vote_results_tx(
        tx,
        domain: Optional[str],
        top: int,
        since: Optional[datetime]
    ) -> List[dict]:
        """
        Transaction de lecture pour récupérer les résultats agrégés.
        
        La requête :
        1. Match toutes les relations VOTED vers les utilisateurs cibles
        2. Filtre par domaine si spécifié
        3. Filtre par date si spécifié
        4. Agrège les votes par (targetUserId, domain)
        5. Trie par count décroissant
        6. Limite aux top N résultats
        """
        
        # Construction de la requête Cypher
        query = """
            MATCH (voter:User)-[v:VOTED]->(target:User)
        """
        
        # Ajout des conditions WHERE
        conditions = []
        params = {
            "top": top
        }
        
        if domain:
            conditions.append("v.domain = $domain")
            params["domain"] = domain
        
        if since:
            conditions.append("v.createdAt >= datetime($since)")
            params["since"] = since.isoformat()
        
        if conditions:
            query += " WHERE " + " AND ".join(conditions)
        
        # Agrégation et tri
        query += """
            WITH target.id AS userId,
                 v.domain AS domain,
                 sum(v.count) AS totalCount,
                 min(v.createdAt) AS firstVoteAt
            ORDER BY totalCount DESC
            LIMIT $top
            RETURN userId,
                   domain,
                   totalCount AS count,
                   true AS elected,
                   firstVoteAt AS electedAt
        """
        
        result = tx.run(query, **params)
        
        results = []
        for record in result:
            results.append({
                "userId": record["userId"],
                "domain": record["domain"],
                "count": record["count"],
                "elected": record["elected"],
                "electedAt": record["electedAt"]
            })
        
        return results
