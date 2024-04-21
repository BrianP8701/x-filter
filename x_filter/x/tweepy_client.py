import os
import tweepy

from dotenv import load_dotenv

load_dotenv()

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

    # def get_user_id(self, username):
    #     """ Returns the user ID for the specified username. """
    #     return self.client.get_users(ids=user_id, user_fields=["profile_image_url"])

    def get_following_ids(self, user_id):
        """ Returns a list of user IDs for users that the specified user is following. """
        return self.client.get_users_followers(id=user_id, max_results=1000)

    def block_users(self, user_id, user_ids_to_block):
        """ Blocks the specified user_ids for the given user. """
        for uid in user_ids_to_block:
            self.client.create_block(user_id=uid)
        return f"Blocked {len(user_ids_to_block)} users for user ID {user_id}"

# Usage
twitter_client = TwitterClient()
following_ids = twitter_client.get_following_ids(user_id='1598905171945349124')
print(following_ids)
# twitter_client.block_users(user_id='12345', user_ids_to_block=['67890', '98765'])
