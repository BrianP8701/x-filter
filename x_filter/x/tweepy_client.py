import os
import tweepy
from dotenv import load_dotenv
from datetime import datetime, timedelta
from x_filter.data.models.filter import Filter
from x_filter.x.helpers import build_combined_query
from typing import List
from x_filter import Database
import logging

load_dotenv()
db = Database()

class TwitterClient:
    _instance = None

    def __new__(cls):
        if cls._instance is None:
            cls._instance = super(TwitterClient, cls).__new__(cls)
            bearer_token = os.getenv('TWITTER_BEARER_TOKEN')
            api_key = os.getenv('X_API_KEY')
            api_secret_key = os.getenv('X_API_KEY_SECRET')
            access_token = os.getenv('X_ACCESS_TOKEN')
            access_token_secret = os.getenv('X_ACCESS_TOKEN_SECRET')

            # # Authentication with Tweepy
            cls._instance.client = tweepy.Client(
                bearer_token=bearer_token,
                consumer_key=api_key,
                consumer_secret=api_secret_key,
                access_token=access_token,
                access_token_secret=access_token_secret
            )
        return cls._instance

    def get_user_id(self, username: str):
        """ Returns the user ID for the specified username. """
        data = self.client.get_users(usernames=[username], user_fields=["id"])
        return data.data[0].id

    def get_username(self, user_id: str):
        """ Returns the username for the specified user ID. """
        data = self.client.get_users(ids=[user_id], user_fields=["username"])
        return data.data[0].username

    def get_followers(self, user_id):
        """ Returns a list of user IDs for users that the specified user is following. """
        data = self.client.get_users_followers(id=user_id, max_results=1000, user_fields=["id"])
        follower_ids = [user.id for user in data.data]
        return follower_ids

    def search_tweets(self, filter: Filter, return_cap=None, keyword_groups=None, filter_period=None):
        """ Returns a list of tweets (id, text, username) that match the specified query. """
        query = build_combined_query(filter)
        if return_cap is None:
            return_cap = filter.return_cap
        if filter_period is None:
            filter_period = filter.filter_period  # Use filter's period if not specified
        start_time = datetime.now() - timedelta(days=6)
        all_data = []
        next_token = None

        while len(all_data) < return_cap:
            logging.info(f"Searching for tweets with query: {query}")
            response = self.client.search_recent_tweets(query=query, max_results=return_cap, start_time=start_time, next_token=next_token, tweet_fields=["author_id"], expansions="author_id")
            print("\n\n\n")
            print(response)
            print("\n\n\n")
            try:
                next_token = response.meta["next_token"]
            except KeyError:
                next_token = None
            if response.data is not None:  # Check if response.data is not None
                all_data.extend(response.data)
            if next_token is None:
                break
        
        if len(all_data) == 0:
            return []

        # Map user IDs to usernames
        user_ids = [tweet.author_id for tweet in all_data]
        users = {user.id: user.username for user in self.client.get_users(ids=user_ids).data}

        output = []
        for tweet in all_data:
            output.append({"id": tweet.id, "text": tweet.text, "username": users.get(tweet.author_id)})
        
        new_message = f"When searching with query {query}, found {len(output)} tweets."
        filter.messages.append({"role": "assistant", "content": new_message})
        db.update("filters", filter.model_dump())
        print(output)
        return output
    
    def block_users(self, user_id, user_ids_to_block):
        """ Blocks the specified user_ids for the given user. """
        for uid in user_ids_to_block:
            self.client.create_block(user_id=uid)
        return f"Blocked {len(user_ids_to_block)} users for user ID {user_id}"

    def get_user_following_count(self, user_id: str):
        """ Returns the number of users that the specified user is following. """
        try:
            data = self.client.get_users_following(id=user_id, max_results=1000)
            return len(data.data)
        except Exception as e:
            return 0
    
    def get_user_followers_count(self, user_id: str):
        """ Returns the number of followers for the specified user. """
        try:
            data = self.client.get_users_followers(id=user_id, max_results=1000)
            return len(data.data)
        except Exception as e:
            return 0

    def get_user_bio(self, user_id: str):
        """ Returns the bio for the specified user. """
        data = self.client.get_users(ids=[user_id], user_fields=["description"])
        return data.data[0].description

    def get_user_tweets(self, usernames: List[str], days: int = 30) -> List[dict]:
        """ Returns a list of tweets (id, text) for the specified usernames within the given number of days. """
        if len(usernames) == 0:
            return []
        all_tweets = []
        for username in usernames:
            user_id = self.get_user_id(username)
            start_time = datetime.now() - timedelta(days=days)
            tweets = self.client.get_users_tweets(id=user_id, start_time=start_time, max_results=100)
            for tweet in tweets.data:
                all_tweets.append({"id": tweet.id, "text": tweet.text})
        return all_tweets
    
    def batch_get_users_tweets(self, user_ids: List[str], days: int = 30) -> List[dict]:
        """ Returns a dict {user_id: [tweet_text, tweet_text...]} for each user """
        all_tweets = {}
        for user_id in user_ids:
            start_time = datetime.now() - timedelta(days=days)
            tweets = self.client.get_users_tweets(id=user_id, start_time=start_time, max_results=100)
            all_tweets[user_id] = [{"id": tweet.id, "text": tweet.text} for tweet in tweets.data]
        return all_tweets

    def get_user_tweets_by_id(self, user_id: str, days: int = 30) -> List[dict]:
        """ Returns a list of tweets (id, text) for the specified user ID within the given number of days. """
        start_time = datetime.now() - timedelta(days=days)
        tweets = self.client.get_users_tweets(id=user_id, start_time=start_time, max_results=100)
        return [{"id": tweet.id, "text": tweet.text} for tweet in tweets.data]
# Usage
if __name__ == "__main__":
    twitter_client = TwitterClient()

    my_id = twitter_client.get_user_id('BrianPrzezdzie2')
    follower_count = twitter_client.get_user_followers_count(my_id)
    following_count = twitter_client.get_user_following_count(my_id)

    print(f"User ID: {my_id}")
    print(f"Followers: {follower_count}")
    print(f"Following: {following_count}")


# data = twitter_client.get_user_tweets(usernames=['BrianPrzezdzie2'])

# print(data)

# following_ids = twitter_client.get_following_ids(user_id='1598905171945349124')
# print(following_ids)

# user_id = twitter_client.get_user_id(username='BrianPrzezdzie2')
# print(user_id)


# filter = Filter(
#     id='12345',
#     user_id='1598905171945349124',
#     name='Test Filter',
#     target='tweets',
#     primary_prompt='Test Prompt',
#     filter_prompt='(test OR testing) (python OR java)',
#     return_cap=100,
#     keyword_groups=[['RAG', 'metadata'], ['RAG', 'new methods'], ['RAG', 'vector databases'], ['state of the art', 'LLM navigation'], ['file structure', 'RAG']],
#     filter_period=14
# )

# tweet_ids = twitter_client.search_tweets(filter, filter_period=6, return_cap=10)
# print(tweet_ids)

# twitter_client.block_users(user_id='12345', user_ids_to_block=['67890', '98765'])
