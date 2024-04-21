from x_filter.x.wrapper import XWrapper
from x_filter.x.helpers import create_url_tweets, create_url_users, build_combined_query

your_x_filter_user_id = 1781356046893854720

def test_get_user_id():
    wrapper = XWrapper()
    username = "BrianPrzezdzie2"
    user_id = wrapper.get_user_id(username)
    print(f"User ID for @{username}: {user_id}")

def test_get_user_info():
    wrapper = XWrapper()
    user_id = "1598905171945349124"
    user_info = wrapper.get_user_info(user_id)
    print(user_info)

def test_get_user_tweets():
    wrapper = XWrapper()
    user_id = "1598905171945349124"
    tweets = wrapper.get_user_tweets(user_id, 100, 60)
    print(tweets)

def get_tweet_author_id():
    wrapper = XWrapper()
    tweet_id = "1781327052874174795"
    author_id = wrapper.get_tweet_author_id(tweet_id)
    print(f"Author ID for tweet {tweet_id}: {author_id}")

def test_search_tweets_with_params():
    wrapper = XWrapper()
    keyword_groups = [["RAG", "new methods"], ["RAG", "vector databases"], ["state of the art", "LLM navigation"], ["file structure, RAG"]]
    start_time = "2024-04-13T00:00:00Z"

    tweet_fields = ["text"]
    user_fields = ["id", "username"]

    tweets = wrapper.search_tweets(keyword_groups=keyword_groups, start_time=start_time, tweet_fields=tweet_fields, user_fields=user_fields)
    print(tweets)
    print(len(tweets))

def test_send_tweet():
    user_id = your_x_filter_user_id
    tweet = "Hello from the X Filter bot!"

    wrapper = XWrapper()
    response = wrapper.post_tweet(user_id, tweet)
    print(response)
    
test_get_user_id()


