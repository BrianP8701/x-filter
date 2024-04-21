from x_filter.ai.instructor import Instructor
from x_filter.data.models.filter import Filter
from x_filter.utils.extraction import extract_filters, combine_keyword_groups
from x_filter.ai.workflows.guided_convo import extract_filters_system_prompt, generate_keyword_groups_system_prompt, GenerateKeywordGroups
from x_filter.ai.filter import run_x_filter
from x_filter import Database
import logging

instructor = Instructor()
db = Database()

async def generate_keyword_groups(filter: Filter): # Extract filters from the prompts
    logging.info(f"filter: {filter}")
    filter = Filter(**filter)
    
    user_message = filter.primary_prompt
    if filter.keyword_groups:
        user_message += f"\n\nThe user shared these example keywords with us: {filter.keyword_groups}"

    messages = [
        {
            "role": "system",
            "content": generate_keyword_groups_system_prompt
        },
        {
            "role": "user",
            "content": user_message
        }
    ]

    model: GenerateKeywordGroups = await instructor.completion(messages, GenerateKeywordGroups)
    filter.keyword_groups = combine_keyword_groups(filter.keyword_groups, model.keyword_groups)
    db.update("filters", filter.model_dump())

    await run_x_filter(filter.id)
