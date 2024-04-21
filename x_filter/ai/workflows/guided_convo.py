# x_filter/ai/workflows/guided_convo.py
"""
This file contains a handcrafted guided conversation workflow.

1: Determine filter target
2: Determine primary prompt
3: Determine report guide if filter target is 'reports'

At the end of the conversation we will have a filter object built.
"""
from pydantic import BaseModel, ConfigDict, Field
from typing import Optional, List

from x_filter.data.models.filter import FilterTarget

# First we ask the user to choose the filter target
first_message = """Hello! I am X-Filter, a bot designed to assist users in finding specific content on X (Twitter). Can you tell me what you are looking for? Are you looking for users, tweets or reports (a summary of a collection of tweets)?"""

# We go back and forth with the user until they choose a filter target
class Stage1(BaseModel):
    """
    Determine what the FilterTarget.
    """
    filter_target: Optional[FilterTarget] = None
    message: str
    model_config = ConfigDict(use_enum_values=True)
    
    def __str__(self):
        return f"filter_target: {self.filter_target}\nmessage: {self.message}"

stage1_system_prompt = """We've inquired whether the user's interest lies in users, tweets, or reports. Please indicate their preference by updating the target field. Should their response deviate or lack clarity, prompting further inquiry, kindly reiterate the question to maintain focus. Below are insights into each option to assist in addressing their queries effectively:
- **Tweets**: Should the user express a desire to sift through an overwhelming volume of tweets or seek out tweets pertaining to a particular idea, topic, or event, this option aligns with their needs.
- **Users**: This option is apt for users on the lookout for specific individuals, be it for recruitment purposes or to connect with those sharing similar beliefs or skills.
- **Reports**: Opt for this if the user expects not just a curated selection of tweets but also desires analytical reports based on them.
So fill out the 'filter_target' field if the user made a choice. If they haven't fill out the 'message' field."""

# Then we ask the user to clarify what they are looking for
ask_for_primary_prompt_for_users = """Great! Now that we've established the target, could you explain to me what type of people your looking for? Be as specific as possible. Are there any specific skills, beliefs, or interests you're looking for?"""
ask_for_primary_prompt_for_tweets = """Great! Now that we've established the target, could you explain to me what type of tweets you're looking for? Be as specific as possible. Are there any specific topics, events, or ideas you're looking for?"""

# We go back and forth with the user to build the primary prompt
class Stage2(BaseModel):
    rewritten_primary_prompt: Optional[str]
    questions: Optional[str]
    
    def __str__(self):
        return f"rewritten_primary_prompt: {self.rewritten_primary_prompt}\nquestions: {self.questions}"

stage2_system_prompt = """At this stage we want to build a comprehensive "primary prompt" describing what the user wants. Choose one of the following options:

1. **Clarify the Search**: If the user's request is unclear, ask questions in the 'questions' field to better understand what they want. If there's acronyms or things that you don't aren't familiar about ask them detailed questions about it. Record these questions in the 'questions' field. Skip this step if the user's intent is already clear. If the user wants reports, clarify that at this stage we're only talking about what types of tweets you want to search for.

2. **Write the Primary Prompt**: If you don't have any further questions to ask, write the primary prompt in the 'rewritten_primary_prompt' field. Try to include everything the user talked about and wanted in this prompt. It's crucial that this is as comprehensive as humanlly possible."""

class Stage3(BaseModel):
    additional_filters: Optional[str]
    questions: Optional[str]

    def __str__(self):
        return f"additional_filters: {self.additional_filters}\nquestions: {self.questions}"

ask_for_filter_prompt = """Now that we've pinpointed the main focus of your search, it's time to fine-tune it with some additional filters. You're not required to specify everything—just share what matters most to you:

- How often would you like this filter to run? The default setting is weekly, but we can adjust this based on your preference.
- How many tweets/users would you like to see in each report? We can set a maximum number of tweets/users to display.
- Are there specific usernames (@username) you're interested in? Do you want to limit your search to these users, or do you want us to find other users as well? You may also choose to limit the search to people you follow.
- Are there any keywords or specific combinations of keywords you think will be useful to search by? We will generate a combinations of keywords to search, but if you have any specific ones you want to mention, please do so."""

class Stage3(BaseModel):
    filter_prompt: Optional[str]
    questions: Optional[str]

    def __str__(self):
        return f"filter_prompt: {self.filter_prompt}\nquestions: {self.questions}"

stage3_system_prompt = """At this stage we are building a filter prompt. The user can tell us how often they want the filter to run, the maximum number of tweets/users they want to see in each report, specific usernames they are interested in and if they want to limit the search to those they specified, or if they want to limit the search to people they follow, or if they are okay with us finding new users.  Also did they mention any specific keywords they want us to search for? If so, write them that in the 'filter_prompt' field as well. Try to include everything the user talked about and wanted in this prompt. The user might ask you to change it, so be ready to make adjustments. If the user doesn't want any filters, just fill out the 'filter_prompt' field with 'No specific filters in mind'. The user doesen't have to fill out any of these, but if they make something very unclear choose to ask questions."""

ask_for_report_guide = """Fantastic! We're now transitioning to the report creation phase. Based on the primary prompt we've crafted together, we'll prepare individual reports for each tweet that aligns with your specified criteria. Please specify the format you prefer for these reports (e.g., text, PDF, spreadsheet). For example, you can tell us what level of detail you expect in each report - do you prefer a concise summary, a detailed analysis, or something in-between? Are there any specific insights or types of analysis you're particularly interested in for each tweet? What tone do you prefer for the reports - formal, informal, technical, or something else? Lastly, are you interested in an analytical perspective of the tweets, or would a straightforward listing of facts, insights, and ideas suffice? Feel free to provide any additional information or preferences you have regarding the report guide."""

class Stage4(BaseModel):
    report_guide: Optional[str]
    questions: Optional[str]
    
    def __str__(self):
        return f"report_guide: {self.report_guide}\nquestions: {self.questions}"

stage4_system_prompt = """At this stage we want to build a comprehensive "report guide" describing how we will write the report. To give some context, we'll have a collection of tweets and we want to know how the user wants the report to be written. If you need to further clarify details about the report guide, ask questions in the 'questions' field. Otherwise, write the report guide in the 'report_guide' field. Try to include everything the user talked about and wanted in this guide. The user might ask you to change it, so be ready to make adjustments."""

ask_for_user_report_guide = """Fantastic! Now do you want us to generate reports on each user we find? If so, please specify the format you prefer for these reports (e.g., text, PDF, spreadsheet). What level of detail do you expect in each report - do you prefer a concise summary, a detailed analysis, or something in-between? Are there any specific insights or types of analysis you're particularly interested in for each user? What tone do you prefer for the reports - formal, informal, technical, or something else? Lastly, are you interested in an analytical perspective of the users, or would a straightforward listing of facts, insights, and ideas suffice? Feel free to provide any additional information or preferences you have regarding the report guide."""

class Stage1_4(BaseModel):
    no_user_reports: Optional[bool]
    user_report_guide: Optional[str]
    questions: Optional[str]
    
    def __str__(self):
        return f"user_report_guide: {self.user_report_guide}\nmessage: {self.message}"

stage1_4_system_prompt = """At this stage we want to build a comprehensive "user report guide" describing how we will write the report. To give some context, we'll have a collection of users and we want to know how the user wants the report to be written. If you need to further clarify details about the report guide, ask questions in the 'questions' field. Otherwise, write the report guide in the 'user_report_guide' field. Try to include everything the user talked about and wanted in this guide. The user might ask you to change it, so be ready to make adjustments. Also, if the user doesn't want user reports, just fill out the 'no_user_reports' field."""

end_of_stage1_message = """Great! We've successfully gathered all the information we need to move on to the next stage. I'll now generate a search strategy based on the information you've provided. When finished I'll run the filter and schedile it to run as you specified. You can see details in the filter setting object. If you need to make any changes, please let me know there!"""

class ExtractedFilters(BaseModel):
    """
    Extract filters from the filter_prompt into the filter object
    """
    filter_period: Optional[int] = Field(None, description="Did the user specify how often they want the filter to runs? Fil in this field in days.")
    usernames: Optional[List[str]] = Field(None, description="Did the user mention any specific usernames to search for?")
    only_search_specified_usernames: Optional[bool] = Field(None, description="Did the user ask to only search for the specific usernames they mentioned?")
    only_search_followers: Optional[bool] = Field(None, description="Did the user ask to only search for the people they follow?")
    keyword_groups: Optional[List[List[str]]] = Field(None, description="Did the user provide any keyword groups to search for?")
    
    return_cap: Optional[int] = Field(None, description="Did the user ask to limit the number of tweets/users they want to see in each report?")
    
    def __str__(self):
        return f"filter_period: {self.filter_period}, usernames: {self.usernames}, only_search_specified_usernames: {self.only_search_specified_usernames}, only_search_followers: {self.only_search_followers}, return_cap: {self.return_cap}"
    
    model_config = ConfigDict(use_enum_values=True)

extract_filters_system_prompt = """Given the prompt from the user, extract as many fields as possible accurately into the provided object. Leave anything not mentioned as None."""

class GenerateKeywordGroups(BaseModel):
    """
    Extract combinations of keyword groups to search
    """
    keyword_groups: List[List[str]] = Field(..., description="List of keyword groups to search for. Each sublist is a group of keywords to be ANDed together. The outer list is a list of groups to be ORed together.")
    
    def __str__(self):
        return f"keyword_groups: {self.keyword_groups}"
    
    model_config = ConfigDict(use_enum_values=True)

generate_keyword_groups_system_prompt = """Your task is to distill keyword groups from the user's prompt with precision, populating the provided object effectively. This step is crucial for honing in on the most relevant search results. Here's how to structure the data:
- Use the outer list to compile groups of keywords that, when searched together, should be considered as separate search queries (OR logic).
- Within each group, list keywords that must all be present in a search result (AND logic).
Consider this user prompt as an example:
"I'm specifically looking for tweets that deliver insights into new methods in RAG, addressing new challenges. I'm interested in new chunking methods in RAG, top vector databases, and models fine-tuned for RAG. Additionally, I'm keen on methods that go beyond vector similarity, utilizing metadata, descriptions, or an LLM to navigate through a structured data system. A system that autonomously organizes arbitrary data into a structured file system, with descriptive labeling and LLM-based search capabilities, would be of particular interest."
A simplistic keyword grouping like [['RAG'], ['solve', 'new problems'], ['file structure']] is inadequate. Such broad terms will yield an overwhelming number of irrelevant tweets. The goal is to craft keyword groups that are both comprehensive and precise, ensuring relevance without overlooking potential insights. Aim for specificity and thoughtful combinations that capture the essence of the user's request.
A more effective approach might include:
[["chunking", "RAG"], ["models", "finetuned", "RAG"], ["file structure", "LLM", "RAG"], ["vector databases", "state of the art", "RAG"], ["metadata", "data organization", "LLM"]].
In addition, you can see this example is quite a specific field, so you should go on to create many more combinations of keywords. In the other hand, if the user's request is by default more broad, you can create less combinations of keywords."""

