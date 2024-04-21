import asyncio
from x_filter import Database
from x_filter.data.models.filter import Filter
from x_filter.x.tweepy_client import TwitterClient
from x_filter.ai.instructor import Instructor
from random import sample
from pydantic import BaseModel, Field
from typing import List

instructor = Instructor()
xwrapper = TwitterClient()
db = Database()

async def run_x_filter(filter_id: str, first_cap: int = 100):
    results_to_return = []
    
    filter = Filter(**db.query("filters", filter_id))
    
    while True:
        tweets = xwrapper.search_tweets(filter, return_cap=100)
        filter = Filter(**db.query("filters", filter_id))
        if len(tweets) < 30:
            filter = await broaden_query(filter)
        else:
            break

    # if filter.usernames and len(filter.usernames) > 0:
    #     specific_user_tweets = xwrapper.get_user_tweets(filter.usernames, days=7)
    #     tweets += specific_user_tweets
    
    if len(tweets) > first_cap:
        tweets = sample(tweets, first_cap)
    
    # Concurrently validate tweets
    valid_tweets = await asyncio.gather(*(x_filter_validate(tweet["text"], filter) for tweet in tweets))

    # Filter out only the valid tweets
    valid_tweets = [tweet for tweet, valid in zip(tweets, valid_tweets) if valid]
    
    if filter.target == "reports":
        # Concurrently create reports for valid tweets
        reports = await asyncio.gather(*(create_tweet_report(tweet["text"], filter) for tweet in valid_tweets))
        results_to_return.extend(reports)
    else:
        results_to_return.extend([f"{tweet['username']}: {tweet['text']}\n\n" for tweet in valid_tweets])
    
    return_cap = filter.return_cap
    if return_cap and len(results_to_return) > return_cap:
        results_to_return = sample(results_to_return, return_cap)
    
    results_to_return_as_string = "\n\n\n".join(results_to_return)
    
    filter.messages.append({
        "role": "assistant",
        "content": f"Here are the results for your filter '{filter.name}':\n\n{results_to_return_as_string}"
    })
    with open("results.md", "w") as results_file:
        results_file.write(results_to_return_as_string)
    db.update("filters", filter.model_dump())

class ValidateTweet(BaseModel):
    valid: bool = Field(..., description="Whether the tweet would want this tweet.")

async def x_filter_validate(tweet_text: str, filter: Filter) -> bool:
    messages = [
        {
            "role": "system",
            "content": "You'll be shown a tweet and also a prompt describing what the user is looking for in tweets. If the tweet is what the user is looking for, set valid to true. If it is not, set valid to false. Respond with 'true' or 'false'."
        },
        {
            "role": "user",
            "content": f"Tweet: {tweet_text}\n\nFilter: {filter.primary_prompt}"
        }
    ]

    decision: ValidateTweet = await instructor.completion(messages, ValidateTweet)
    return decision.valid

class CreateTweetReport(BaseModel):
    report: str = Field(..., description="Write this tweet's report here.")

async def create_tweet_report(tweet_text: str, filter: Filter):
    messages = [
        {
            "role": "system",
            "content": f"Write a report for this tweet following this report guide:\n{filter.report_guide}\n\nThe user's search interest is: {filter.primary_prompt}."
        },
        {
            "role": "user",
            "content": f"Tweet: {tweet_text}"
        }
    ]

    report: CreateTweetReport = await instructor.completion(messages, CreateTweetReport)
    return report.report

class MakeNewKeywordGroup(BaseModel):
    keyword_groups: List[List[str]] = Field(..., description="Enter a new keyword group.")
broaden_query_prompt = "The current query is not returning enough results. Please provide a new more general keyword group to broaden the search. By the way, to clarify, you are REWRITING the keyword groups, not adding to them. Keyword groups work by treating each sublist as a set of 'AND' conditions, and the lists themselves are 'ORed' together. The best way to broaden a search is to create fewer 'ANDs' (sublists with fewer items) and more 'ORs' (more sublists). So, consider splitting up the inner sublists to increase 'ORs'."
async def broaden_query(filter: Filter):
    keyword_groups = filter.keyword_groups
    messages = [
        {
            "role": "system",
            "content": broaden_query_prompt
        },
        {
            "role": "user",
            "content": f"The user is looking for stuff that matches this: {filter.primary_prompt}\n\nCurrent keyword groups: {keyword_groups}\n\nPlease provide a new keyword group."
        }
    ]
    
    new_keyword_group: MakeNewKeywordGroup = await instructor.completion(messages, MakeNewKeywordGroup)
    filter.keyword_groups = new_keyword_group.keyword_groups
    db.update("filters", filter.model_dump())
    return filter
