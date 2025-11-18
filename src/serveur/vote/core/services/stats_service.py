from db.repository.vote_repository import VoteRepository

from typing import List

class StatsService:
    @staticmethod
    def get_daily_stats(user_id: str) -> List:
        """
        """
        per_day = {}
        votes = VoteRepository.get_votes_to_user(user_id)
        for v in votes:
            dt = str(v.createdAt)
            if dt not in per_day:
                per_day[dt] = 1
            else:
                per_day[dt] += 1
        return per_day

    @staticmethod
    def get_monthly_stats(user_id: str) -> dict:
        """
        """
        pass
