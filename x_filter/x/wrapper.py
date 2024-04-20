import tweepy
import os
from dotenv import load_dotenv

# singleton
class XWrapper:
    _instance = None
    _client = None

    def __new__(cls):
        if cls._instance is None:
            cls._instance = super().__new__(cls)
            load_dotenv()
            bearer_token = os.getenv("TWITTER_BEARER_TOKEN")
            cls._client = tweepy.Client(bearer_token=bearer_token)
        return cls._instance

    async def get_tweets(self, query: str, max_results: int = 10):
        tweets = self._client.search_recent_tweets(query, max_results=max_results)
        return tweets