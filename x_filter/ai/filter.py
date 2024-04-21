from x_filter import Database
from x_filter.data.models.filter import Filter
from x_filter.x.wrapper import XWrapper

xwrapper = XWrapper()
db = Database()

async def run_x_filter(filter_id: str):
    filter = Filter(**db.query("filters", filter_id))


    tweets = xwrapper.search_tweets_with_filter(filter)
    specific_user_tweets = []
    for username in filter.usernames:
        user_id = xwrapper.get_user_id(username)
        users_tweets = xwrapper.get_users_tweets(user_id, days=filter.filter_period)
        specific_user_tweets += users_tweets
    tweets += specific_user_tweets
    