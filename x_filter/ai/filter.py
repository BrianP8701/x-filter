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

async def run_x_filter(filter_id: str):    
    filter = Filter(**db.query("filters", filter_id))

    min = filter.return_min
    max = filter.return_cap
    gathered_tweets = []    
    previous_keyword_groups = []

    retry = 50
    c_try = 0

    first_keywords = await most_likely_keyword_group(filter, previous_keyword_groups)
    num_of_keywords = len(first_keywords)

    while len(gathered_tweets) < min:
        keywords = await most_likely_keyword_group(filter, previous_keyword_groups, num_of_keywords)
        if c_try > retry:
            break
        filter.messages.append({
            "role": "assistant",
            "content": f"Searching with keywords: {keywords}"
        })
        db.update("filters", filter.model_dump())
        previous_keyword_groups.append(keywords)
        max_results = max - len(gathered_tweets)
        tweets = await xwrapper.search_recent_tweets(keywords, max_results=max_results)
        for tweet in tweets:
            is_valid = await x_filter_validate(tweet["text"], filter)
            if is_valid:
                gathered_tweets.append(tweet)
                filter.messages.append({
                    "role": "assistant",
                    "content": f"Found tweet: {tweet['text']}"
                })
        filter.messages.append({
            "role": "assistant",
            "content": f"Found {len(tweets)} tweets with keywords: {keywords}"
        })
        db.update("filters", filter.model_dump())
        gathered_tweets += tweets
        if c_try % 5 == 0:
            num_of_keywords -= 1
            if num_of_keywords < 2: 
                num_of_keywords = 2
        if len(gathered_tweets) >= max:
            break
        c_try += 1

    tweet_results = sample(gathered_tweets, min)

    for tweet in tweet_results:
        filter.messages.append({
            "role": "assistant",
            "content": f"@{tweet['username']}: {tweet['text']}"
        })
    db.update("filters", filter.model_dump())
    
    if filter.target == "reports":
        for tweet in tweet_results:
            report = await create_tweet_report(tweet["text"], filter)
            filter.messages.append({
                "role": "assistant",
                "content": f"Report for tweet: {report}"
            })
        db.update("filters", filter.model_dump())
    
        

class ValidateTweet(BaseModel):
    valid: bool = Field(..., description="Whether the user would want this tweet. Don't be too strict.")

async def x_filter_validate(tweet_text: str, filter: Filter) -> bool:
    messages = [
        {
            "role": "system",
            "content": "You'll be shown a tweet and also a prompt describing what the user is looking for in tweets. If the tweet is what the user is looking for, set valid to true. If it is not, set valid to false. Respond with 'true' or 'false'."
        },
        {
            "role": "user",
            "content": f"Tweet: {tweet_text}\n\nFilter prompt: {filter.primary_prompt}"
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
            "content": f"The user is looking for stuff that matches this: {filter.primary_prompt}\n\nCurrent keyword groups: {keyword_groups}\n\nPlease provide a new keyword group that is more general than the current one."
        }
    ]

    new_keyword_group: MakeNewKeywordGroup = await instructor.completion(messages, MakeNewKeywordGroup)
    filter.keyword_groups = new_keyword_group.keyword_groups
    filter.messages.append({
        "role": "assistant",
        "content": f"Updated keyword groups to be more general: {filter.keyword_groups}"
    })
    db.update("filters", filter.model_dump())
    return filter

class MakeNewPrimaryPrompt(BaseModel):
    primary_prompt: str = Field(..., description="Enter a new primary prompt.")
async def broaden_primary_prompt(filter: Filter):
    messages = [
        {
            "role": "system",
            "content": "The current primary prompt is not returning enough results. Please provide a new primary prompt that is more general."
        },
        {
            "role": "user",
            "content": f"Current primary prompt: {filter.primary_prompt}"
        }
    ]

    new_primary_prompt: MakeNewPrimaryPrompt = await instructor.completion(messages, MakeNewPrimaryPrompt)
    filter.primary_prompt = new_primary_prompt.primary_prompt
    db.update("filters", filter.model_dump())
    return filter




class MostLikelyKeywordGroup(BaseModel):
    keywords: List[str] = Field(..., description="All the keywords in here are queryed together with the 'AND' operator.")
base_system_prompt = "Reflecting on the user's specific interests, identify the most precise keyword group (comprising single-word keywords) that has not yet been utilized. This process will be repeated iteratively to achieve the optimal number of keywords. It's important to note that the user's primary prompt might not explicitly include the keywords needed for the search. Employ strategic thinking to deduce the most relevant keywords that align with the user's search intent. If pinpointing specific keywords proves challenging, opt for broader, more general keywords to ensure relevancy. Please, use simple words."
async def most_likely_keyword_group(filter: Filter, previous_keyword_groups: List[List[str]], num_of_keywords=None):
    system_prompt = base_system_prompt
    if num_of_keywords is not None:
        system_prompt += f"\n\nYou MUST come up with {num_of_keywords} keywords. This is a MUST."
    messages = [
        {
            "role": "system",
            "content": system_prompt
        },
        {
            "role": "user",
            "content": f"User's search interest: {filter.primary_prompt}\n\nPrevious keyword groups: {previous_keyword_groups}"
        }
    ]

    keyword_group: MostLikelyKeywordGroup = await instructor.completion(messages, MostLikelyKeywordGroup)
    return keyword_group.keywords
