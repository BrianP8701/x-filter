from typing import List, Optional
from datetime import datetime, timedelta

from x_filter.data.models.filter import Filter

twitter_url = "https://api.twitter.com/2/"

def build_combined_query(filter: Filter, exclude_replies: bool = True):
    """
    Constructs a Twitter search query string from a list of keyword groups. Each group is combined using 'AND',
    and each resulting group string is then combined with 'OR' between them. Ensures correct formatting to avoid ambiguity.
    
    Args:
        keyword_groups (list of list of str): A list where each element is a list of keywords to be ANDed together.
    
    Returns:
        str: A combined query string integrating both 'AND' and 'OR' conditions, formatted for Twitter API requirements.
    """
    keyword_groups = filter.keyword_groups
    combined_queries = []

    # Filter out empty or whitespace-only keyword groups before processing
    keyword_groups = [group for group in keyword_groups if group and any(keyword.strip() for keyword in group)]

    for keywords in keyword_groups:
        # Enclose keywords in quotes only if they contain spaces
        quoted_keywords = [f'"{keyword}"' if ' ' in keyword else keyword for keyword in keywords]
        # Join keywords in each group with ' AND ' ensuring correct spacing
        and_query = ' '.join(quoted_keywords)
        # Enclose each and_query in parentheses to ensure proper grouping
        combined_queries.append(f"({and_query})")

    # Initially attempt to include all keyword groups
    final_query = ' OR '.join(combined_queries)

    if exclude_replies:
        final_query += " -is:reply"

    # Check if the final query exceeds the Twitter API limit of 512 characters
    while len(final_query) > 512:
        # If so, remove the last keyword group and reconstruct the query
        if combined_queries:
            combined_queries.pop()  # Remove the last group
            final_query = ' OR '.join(combined_queries)
            if exclude_replies:
                final_query += " -is:reply"
        else:
            # If all groups are removed and it's still too long, break to avoid infinite loop
            break

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