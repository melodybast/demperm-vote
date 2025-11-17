from typing import Optional

from app.neo4j_config import get_driver


class VoteRepository:
    """
    Persistance des votes dans Neo4j.

    Modèle :
      (voter:User {id})
          -[:VOTED {id, createdAt, domain, count}]->
      (target:User {id})
    """

    @staticmethod
    def save_vote(vote: dict) -> None:
        """
        vote = {
          "id": uuid,
          "voterId": str,
          "targetUserId": str,
          "domain": str,
          "createdAt": datetime
        }
        """
        driver = get_driver()
        with driver.session() as session:
            session.execute_write(VoteRepository._save_vote_tx, vote)

    @staticmethod
    def _save_vote_tx(tx, vote: dict):
        tx.run(
            """
            MERGE (voter:User {id: $voterId})
            MERGE (target:User {id: $targetUserId})

            WITH voter, target

            OPTIONAL MATCH (voter)<-[incoming:VOTED]-()
            WITH voter, target,
                 CASE
                    WHEN coalesce(sum(incoming.count), 0) = 0
                    THEN 1
                    ELSE coalesce(sum(incoming.count), 0)
                 END AS voteWeight

            MERGE (voter)-[rel:VOTED {domain: $domain}]->(target)
            ON CREATE SET
                rel.id        = $id,
                rel.createdAt = datetime($createdAt),
                rel.count     = voteWeight
            ON MATCH SET
                rel.count     = rel.count + voteWeight
            """,
            id=str(vote["id"]),
            voterId=str(vote["voterId"]),
            targetUserId=str(vote["targetUserId"]),
            domain=vote["domain"],
            createdAt=vote["createdAt"].isoformat(),
        )

    @staticmethod
    def delete_vote(voter_id: str, domain: str) -> bool:
        """
        Délétion du vote d'un utilisateur dans le domaine précisé.
        """
        driver = get_driver()
        with driver.session() as session:
            return session.execute_write(
                VoteRepository._delete_vote_tx, voter_id, domain
            )

    @staticmethod
    def _delete_vote_tx(tx, voter_id: str, domain: str):
        result = tx.run(
            """
            MATCH (voter:User {id: $voterId})-[v:VOTED {domain: $domain}]->(target:User)
            DELETE v
            RETURN count(v) as deleted
            """,
            voterId=voter_id,
            domain=domain,
        )

        record = result.single()
        return record["deleted"] > 0

    @staticmethod
    def get_votes_by_voter(voter_id: str, domain: Optional[str] = None) -> list[dict]:
        """
        Récupère les votes émis par un utilisateur
        """
        driver = get_driver()
        with driver.session() as session:
            return session.execute_read(
                VoteRepository._get_votes_by_voter_tx, voter_id, domain
            )

    @staticmethod
    def _get_votes_by_voter_tx(
        tx, voter_id: str, domain: Optional[str] = None
    ) -> list[dict]:
        query_start = """
        MATCH (voter:User {id: $voterId})-[v:VOTED]->(target:User)
        """
        query_ret = """
        RETURN v.id as id, 
            voter.id as voterId, 
            target.id as targetUserId, 
            v.domain as domain, 
            v.createdAt as createdAt
        """

        params = {"voterId": voter_id}

        domain_clause = ""
        if domain is not None:
            domain_clause = "WHERE v.domain = $domain"
            params["domain"] = domain

        records = tx.run(query_start + domain_clause + query_ret, **params)

        votes = []
        for record in records:
            votes.append(
                {
                    "id": record["id"],
                    "voterId": record["voterId"],
                    "targetUserId": record["targetUserId"],
                    "domain": record["domain"],
                    "createdAt": record["createdAt"],
                }
            )

        return votes

    @staticmethod
    def get_votes_for_target(target_user_id: str, domain: Optional[str] = None) -> list:
        """
        Recuperation des votes percus par un individu.
        """

        driver = get_driver()
        with driver.session() as session:
            return session.execute_read(
                VoteRepository._get_votes_for_target_tx, target_user_id, domain
            )

    @staticmethod
    def _get_votes_for_target_tx(tx, target_user_id: str, domain: Optional[str]):
        query_start = (
            """MATCH (voter:User)-[v:VOTED]->(target:User {id: $targetUserId})"""
        )
        query_ret = """
        RETURN  v.id as id,
                voter.id as voterId,
                target.id as targetId,
                v.domain as domain,
                v.createdAt as createdAt
        """

        params = {"targetUserID": target_user_id}
        domain_clause = ""
        if domain is not None:
            domain_clause += "WHERE v.domain = $domain"
            params["domain"] = domain

        # TODO: Verify if formatting is correct, else iter over each elem and put in new correct dict
        return tx.run(query_start + domain_clause + query_ret, params)
