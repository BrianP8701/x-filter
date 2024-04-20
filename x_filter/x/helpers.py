from typing import List, Optional

twitter_url = "https://api.twitter.com/2/"

def build_combined_query(keyword_groups, exclude_replies: bool = True):
    """
    Constructs a Twitter search query string from a list of keyword groups. Each group is combined using 'AND',
    and each resulting group string is then combined with 'OR' between them. Ensures correct formatting to avoid ambiguity.
    
    Args:
        keyword_groups (list of list of str): A list where each element is a list of keywords to be ANDed together.
    
    Returns:
        str: A combined query string integrating both 'AND' and 'OR' conditions, formatted for Twitter API requirements.
    """
    combined_queries = []
    
    for keywords in keyword_groups:
        # Enclose keywords in quotes only if they contain spaces
        quoted_keywords = [f'"{keyword}"' if ' ' in keyword else keyword for keyword in keywords]
        # Join keywords in each group with ' AND ' ensuring correct spacing
        and_query = ' '.join(quoted_keywords)
        # Enclose each and_query in parentheses to ensure proper grouping
        combined_queries.append(f"({and_query})")
    
    # Join all group queries with ' OR ', ensuring correct spacing
    final_query = ' OR '.join(combined_queries)
    
    if exclude_replies:
        final_query += " -is:reply"
    
    return final_query




def concat_fields(fields: List[any]):
    """
    Takes in a list of fields of any type, and concats them with separating commas
    to successfully use the query parameters.
    """

    fields = ",".join(fields)

    return fields

def create_url_tweets(ids: List[int], tweet_fields: Optional[List[str]] = None, user_fields: Optional[List[str]] = None):
    """
    Base call function for the /2/tweets endpoint
    https://developer.twitter.com/en/docs/twitter-api/tweets/lookup/api-reference/get-tweets

    Allows for functionality of different types of query parameters:
        - tweet.fields
        - user.fields
    """
    ids = "ids=" + concat_fields(ids)
    tweet_fields = "&tweet.fields=" + concat_fields(tweet_fields) if tweet_fields else ""
    user_fields = "&user.fields=" + concat_fields(user_fields) if user_fields else ""

    url = f"{twitter_url}tweets?{ids}{tweet_fields}{user_fields}"
    return url

def create_url_users(self, ids: List[int], tweet_fields: Optional[List[str]] = None, user_fields: Optional[List[str]] = None):
    """
    Base call function for the /2/users endpoint
    https://developer.twitter.com/en/docs/twitter-api/users/lookup/api-reference/get-users

    Allows for functionality with these query parameters:
        - tweet.fields
        - user.fields
    """

    ids = "ids=" + concat_fields(ids)
    tweet_fields = "&tweet.fields=" + concat_fields(tweet_fields) if tweet_fields else ""
    user_fields = "&user.fields=" + concat_fields(user_fields) if user_fields else ""

    url = f"{twitter_url}users?{ids}{tweet_fields}{user_fields}"
    return url