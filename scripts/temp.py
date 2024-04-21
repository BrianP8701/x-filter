import tweepy

from dotenv import load_dotenv
import os

bearer_token = os.getenv('TWITTER_BEARER_TOKEN')

client = tweepy.Client(bearer_token)

# Get User's Followers

# This endpoint/method returns a list of users who are followers of the
# specified user ID

user_id = os.getenv('MY_USER_ID')

# By default, only the ID, name, and username fields of each user will be
# returned
# Additional fields can be retrieved using the user_fields parameter
response = client.get_users_followers(
    user_id, user_fields=["d"]
)

for user in response.data:
    print(user.username, user.id)

# By default, this endpoint/method returns 100 results
# You can retrieve up to 1000 users by specifying max_results
response = client.get_users_followers(user_id, max_results=1000)