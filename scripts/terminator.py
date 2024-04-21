from x_filter.x.tweepy_client import TwitterClient
from pydantic import BaseModel, Field
from x_filter.ai.instructor import Instructor
import asyncio
from typing import List, Dict

instructor = Instructor()
twitter_client = TwitterClient()


async def terminate_bots(username: str):
    user_id = twitter_client.get_user_id(username)
    
    user_followers = twitter_client.get_followers(user_id)
    
    bot_list = []
    
    # First check for usernames with more than 6 digits in their username
    for follower in user_followers:
        suspect_username = twitter_client.get_username(follower)
        if sum(c.isdigit() for c in suspect_username) > 6:
            bot_list.append(follower)
            user_followers.remove(follower)
    
    # Then check their follower:following ratio
    for follower in user_followers:
        following_count = twitter_client.get_user_following_count(follower)
        followers_count = twitter_client.get_user_followers_count(follower)
        # Check if followers_count is not None before proceeding
        if followers_count is not None and following_count > 0 and (followers_count / following_count) < 0.01:
            bot_list.append(follower)
            user_followers.remove(follower)
        elif followers_count is None:
            # Handle the case where followers_count is None, e.g., log an error or skip the user
            print(f"Error retrieving followers count for user ID: {follower}")
    
    # Fetch tweets for all followers in a batch
    followers_tweets = twitter_client.batch_get_users_tweets(user_followers, days=30)

    # Prepare tasks for parallel execution
    tasks = [ai_terminate_bot(follower, followers_tweets.get(follower, [])) for follower in user_followers]
    results = await asyncio.gather(*tasks)
    
    for result in results:
        user_id, is_bot = next(iter(result.items()))
        if is_bot:
            bot_list.append(user_id)
            user_followers.remove(user_id)
    
    print(f"Bot list: {bot_list}")
    print(f"User list: {user_followers}")
    print(len(bot_list), len(user_followers))

class IsThisUserABot(BaseModel):
    is_bot: bool = Field(..., description="Whether the user is a bot.")

system_prompt = """Hi, I'm going to share a twitter user's tweets and bio with you. I need you to decide whether or not this user is a bot. Here are some examples of bot-like behavior. If the user's bio or posts makes any mention of cam shows, slutty stuff, crypto, or any other bot-like behavior, please respond with 'True'. Otherwise, please respond with 'False'.

These are all examples of bots:
1. 
bio: 💛21 / Lets Cam👇🖤
tweets: ["He bent his head and reflected like a bloodhound who puts his nose to the ground to make sure that he is on the right scent"]]
2. 
bio: 🔗25 ~ EARN daily USDT👇💎
3.
bio: 🌐Earn your own Crypto casino👇🔶

"""
async def ai_terminate_bot(user_id: str, tweets_data: List[Dict]) -> Dict[str, bool]:
    bio = twitter_client.get_user_bio(user_id)
    tweets = [tweet["text"] for tweet in tweets_data]

    messages = [
        {
            "role": "system",
            "content": system_prompt
        },
        {
            "role": "user",
            "content": f"bio: {bio}\n\ntweets: {tweets}"
        }
    ]
    
    model: IsThisUserABot = await instructor.completion(messages, IsThisUserABot)
    
    return {user_id: model.is_bot}
    
    

# At the end of your script, replace the direct call with:
if __name__ == "__main__":
    asyncio.run(terminate_bots("PhuongRust"))
