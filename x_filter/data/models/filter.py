from pydantic import BaseModel, ConfigDict
from typing import Optional, List, Dict
from enum import Enum

class FilterTarget(str, Enum):
    USERS = "users"
    TWEETS = "tweets"
    REPORTS = "reports"

class ExtractedFilters(BaseModel): # We build this based off of the filter_prompt
    id: str
    user_id: str
    filter_period: Optional[int] = 7 # In days
    usernames: Optional[List[str]] = [] # Specific usernames to search for
    only_search_specified_usernames: Optional[bool] = False
    only_search_followers: Optional[bool] = False
    
    tweet_cap: Optional[int] = 100
    user_cap: Optional[int] = 20
    
    keyword_groups: Optional[List[List[str]]] = None

    model_config = ConfigDict(use_enum_values=True)

class Filter (BaseModel):
    id: str
    user_id: str
    name: Optional[str] = None
    target: Optional[FilterTarget] = None
    primary_prompt: Optional[str] = None
    report_guide: Optional[str] = None
    filter_prompt: Optional[str] = None

    filter_period: Optional[int] = 7 # In days
    usernames: Optional[List[str]] = [] # Specific usernames to search for
    only_search_specified_usernames: Optional[bool] = False
    # only_search_followers: Optional[bool] = False
    tweet_cap: Optional[int] = 100
    user_cap: Optional[int] = 20
    keyword_groups: Optional[List[List[str]]] = None
    messages: Optional[List[Dict[str, str]]] = []

    model_config = ConfigDict(use_enum_values=True)
