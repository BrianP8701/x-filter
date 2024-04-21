import tweepy
from dotenv import load_dotenv
import os

load_dotenv()

consumer_key = os.getenv("X_API_KEY")
consumer_secret = os.getenv("X_API_KEY_SECRET")

# Step 1: Set up your consumer keys and callback URL
callback_uri = 'http://localhost:3000/callback'  # This URL should match the one registered in the Twitter app settings

# Step 2: OAuth Handler and redirect user to Twitter for authorization
auth = tweepy.OAuthHandler(consumer_key, consumer_secret, callback_uri)
redirect_url = auth.get_authorization_url()
print(f"Go to the following URL to authorize your application: {redirect_url}")

# Step 3: User will authorize and receive a verifier code. Enter that here.
verifier = input('Type the verifier code here: ')

# Step 4: Get the access token
auth.get_access_token(verifier)
print(f"Access Token: {auth.access_token}")
print(f"Access Token Secret: {auth.access_token_secret}")

# Step 5: Set up the API client
api = tweepy.API(auth)

# Step 6: Create a tweet
status = "Hello, world! Tweeting from Tweepy and Python."
api.update_status(status=status)
print("Tweeted: {}".format(status))
