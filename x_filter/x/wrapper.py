# Feel free to change the functions as needed i just made a rough outline of what i think the wrapper should look like
# singleton

import requests
import os
from typing import List, Optional
from dotenv import load_dotenv
import tweepy

from x_filter.data.models.filter import Filter
from x_filter.x.helpers import create_url_tweets, create_url_users, build_combined_query

load_dotenv()

TWITTER_BEARER_TOKEN = os.getenv("TWITTER_BEARER_TOKEN")
twitter_url = "https://api.twitter.com/2/"
def bearer_oauth(r):
    """
    Method required by bearer token authentication.
    """

    r.headers["Authorization"] = f"Bearer {TWITTER_BEARER_TOKEN}"

    return r

class XWrapper:
    _instance = None

    def __new__(cls):
        if cls._instance is None:
            cls._instance = super(XWrapper, cls).__new__(cls)
        return cls._instance

    def connect_to_endpoint(self, url, params):
        response = requests.request("GET", url, auth=bearer_oauth, params=params)
        print(response.status_code)
        if response.status_code != 200:
            raise Exception(
                "Request returned an error: {} {}".format(
                    response.status_code, response.text
                )
            )
        return response.json()

    def search_tweets(self, keyword_groups: List[List[str]], tweet_cap: int = 100, expansions: Optional[List[str]] = None, sort_order: Optional[str] = None, start_time: Optional[str] = None, tweet_fields: Optional[List[str]] = None, user_fields: Optional[List[str]] = None) -> List[dict]:
        """
        Search for tweets based on various parameters similar to Twitter's advanced search functionality.

        :param keywords_groups: List of lists of keywords to be ANDed together.
        :param tweet_cap: The maximum number of tweets to be returned by a request.
        :param expansions: Expansions enable you to request additional data objects that relate to the originally returned Tweets.
        :param sort_order: This parameter is used to specify the order in which you want the Tweets returned.
        :param start_time: The oldest UTC timestamp from which the Tweets will be provided.
        :param tweet_fields: This fields parameter enables you to select which specific Tweet fields will deliver in each returned Tweet object.
        :param user_fields: This fields parameter enables you to select which specific user fields will deliver in each returned Tweet.
        """
        data = []
        url = f"{twitter_url}tweets/search/recent"
        params = {
            "query": build_combined_query(keyword_groups)
        }

        if expansions:
            params["expansions"] = ",".join(expansions)
        if sort_order:
            params["sort_order"] = sort_order
        if start_time:
            params["start_time"] = start_time
        if tweet_fields:
            params["tweet.fields"] = ",".join(tweet_fields)
        if user_fields:
            params["user.fields"] = ",".join(user_fields)

        while len(data) < tweet_cap:
            response = self.connect_to_endpoint(url, params)
            data.extend(response["data"])
            if "next_token" in response["meta"]:
                params["next_token"] = response["meta"]["next_token"]
            else:
                break
        
        return data

    def search_tweets_with_filter(self, filter: Filter) -> List[dict]:
        """
        Search for tweets based on various parameters similar to Twitter's advanced search functionality.

        :param filter: Filter object containing all parameters needed for searching tweets.
        """
        data = []
        url = f"{twitter_url}tweets/search/recent"
        params = {
            "query": self.build_combined_query(filter.keyword_groups)
        }

        if filter.start_time:
            params["start_time"] = filter.start_time
        if filter.tweet_fields:
            params["tweet.fields"] = ",".join(filter.tweet_fields)
        if filter.user_fields:
            params["user.fields"] = ",".join(filter.user_fields)

        # Handle user specific search if required
        if filter.only_search_specified_usernames and filter.usernames:
            params["query"] += " (" + " OR ".join(f"from:{username}" for username in filter.usernames) + ")"

        tweet_cap = filter.tweet_cap if filter.tweet_cap is not None else 100  # Use a default value if not specified

        while len(data) < tweet_cap:
            response = self.connect_to_endpoint(url, params)
            data.extend(response.get("data", []))
            if "next_token" in response.get("meta", {}):
                params["next_token"] = response["meta"]["next_token"]
            else:
                break
        
        return data


    def get_tweet_text(self, tweet_id: str):   
        """
        Gets text from a tweet.

        tweet_fields - query parameter to get text data of the tweet
        ids - id of the specific tweet to access
        url - complete URL to get a response from
        """

        tweet_fields = ["text"]
        ids = [tweet_id]
        url = create_url_tweets(ids=ids, tweet_fields=tweet_fields)

        response = requests.request("GET", url, auth=bearer_oauth)
        return response.json()["data"][0]["text"]

    def get_tweet_author_id(self, tweet_id: str) -> str:
        """
        Gets author's account id from their tweet.

        tweet_fields - query parameter to get author_id data of the tweet
        ids - id of the specific tweet to access
        url - complete URL to get a response from
        """
        tweet_fields = ["author_id"]
        ids = [tweet_id]
        url = create_url_tweets(ids=ids, tweet_fields=tweet_fields)
        
        response = requests.request("GET", url, auth=bearer_oauth)
        return response.json()["data"][0]["author_id"]

    def get_user_id(self, username: str) -> str:
        """
        Gets user's account id from their username.

        user_fields - query parameter to get id data of the user
        ids - id of the specific user to access
        url - complete URL to get a response from
        """
        user_fields = ["id"]
        ids = [username]
        url = f"{twitter_url}users/by?usernames={username}&user.fields=id"

        response = requests.request("GET", url, auth=bearer_oauth)
        print(response.json())
        return response.json()["data"][0]["id"]

    def get_user_info(self, user_id: str):
        user_fields = ["name", "username", "created_at", "description", "location", "public_metrics", "verified"]
        ids = [user_id]
        url = create_url_users(ids=ids, user_fields=user_fields)

        response = requests.request("GET", url, auth=bearer_oauth)
        # TODO: Go through the response.json and put it into an easy to read and accessed json/dictionary
        return response.json()

    def get_user_followers(self, user_id: str):
        url = f"{twitter_url}users/{id}/followers"

        response = requests.request("GET", url, auth=bearer_oauth)
        return response.json()

    def get_user_tweets(self, user_id: str, count: int = 100, days: int = None):
        """
        Get users {count} recent tweets or tweets from the past {days} days.
        """
        url = f"https://api.twitter.com/2/users/{user_id}/tweets"
        params = {
            "tweet.fields": "created_at",
            "max_results": min(count, 100)  # Twitter API v2 allows a maximum of 100 tweets per request
        }

        # If days parameter is provided, calculate the start time for tweets
        if days is not None:
            from datetime import datetime, timedelta
            start_time = datetime.utcnow() - timedelta(days=days)
            params["start_time"] = start_time.strftime("%Y-%m-%dT%H:%M:%SZ")

        response = self.connect_to_endpoint(url, params)
        return response

    def post_tweet(self, user_id: str, tweet: str):
        url = f"{twitter_url}tweets"
        params = {
            "text": tweet,
            "author_id": user_id
        }

        response = requests.request("POST", url, auth=bearer_oauth, params=params)
        return response.json()
    # Learn more abt x's api and implement more methods as needed
    
