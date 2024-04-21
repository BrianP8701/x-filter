# x_filter/ai/main.py
"""
This is where we build the main logic for the bot.
"""
# import swarmstar
import logging

from x_filter.utils.security import generate_uuid
from x_filter import Database
from x_filter.ai.workflows.guided_convo import (
    first_message, Stage1, ask_for_primary_prompt_for_users, 
    ask_for_primary_prompt_for_tweets, stage1_system_prompt, 
    Stage2, stage2_system_prompt, stage3_system_prompt,
    ask_for_report_guide, Stage3, ask_for_filter_prompt, 
    stage4_system_prompt, Stage4, end_of_stage1_message,
    ExtractedFilters, extract_filters_system_prompt, 
    GenerateKeywordGroups, generate_keyword_groups_system_prompt
)
from x_filter.data.models.filter import Filter
from x_filter.data.models.conversation import Conversation
from x_filter.ai.instructor import Instructor
from x_filter.utils.conversational import add_message_to_conversation, initialize_filter_chat
from x_filter.utils.extraction import extract_filters, combine_keyword_groups
from x_filter.x.wrapper import XWrapper
from x_filter.data.models.events import MessageEvent
from x_filter.ai.filter import run_x_filter

db = Database()
instructor = Instructor()
xwrapper = XWrapper()

async def handle_chat_message(user_id: str, message: str):
    """
    This function is called when a user sends a message to the bot.
    """
    conversation = Conversation(**db.query("conversations", user_id))
    filter = Filter(**db.query("filters", user_id))
    event = MessageEvent(user_id=user_id, filter_id=user_id, message=message)
    logging.info(f"Received event in the handler")
    conversation.cached_messages.append({"role": "user", "content": message})
    db.update("conversations", conversation.model_dump())

    match int(conversation.stage):
        case 1:
            await determine_filter_target(conversation, event, filter)
        case 2:
            await build_primary_prompt(conversation, event, filter)
        case 3:
            await build_filter_prompt(conversation, event, filter)
        case 4:
            await build_report_guide(conversation, event, filter)
        case 5:
            await build_filter(filter)
        case _:
            raise ValueError(f"Invalid stage: {conversation.stage}")


async def determine_filter_target(conversation: Conversation, event: MessageEvent, filter: Filter):
    """
    Determine the filter target, primary prompt and report guide if the filter target is 'reports'.
    """
    logging.info(f"Received event in the determine_filter_target function")
    user_message = event.message

    messages = [
        {
            "role": "system",
            "content": stage1_system_prompt
        },
        {
            "role": "user",
            "content": user_message
        }
    ]

    model: Stage1 = await instructor.completion(messages, Stage1)
    if model.filter_target:
        filter.target = model.filter_target
        db.update("filters", filter.model_dump())
        conversation.stage = 2
        conversation.cached_messages = []
        db.update("conversations", conversation.model_dump())
        if filter.target == "users":
            add_message_to_conversation(conversation, "assistant", ask_for_primary_prompt_for_users)
        else:
            add_message_to_conversation(conversation, "assistant", ask_for_primary_prompt_for_tweets)
    else:
        add_message_to_conversation(conversation, "assistant", model.message)

async def build_primary_prompt(conversation: Conversation, event: MessageEvent, filter: Filter): # Build the primary prompt
    logging.info(f"Received event in the build_primary_prompt function")
    user_message = event.message
    if user_message.lower().replace(" ", "") == "yes": # User is satisfied with the primary prompt
        conversation.stage = 3
        conversation.cached_messages = []
        db.update("conversations", conversation.model_dump())
        add_message_to_conversation(conversation, "assistant", ask_for_filter_prompt)
        return

    messages = conversation.cached_messages + [
        {
            "role": "system",
            "content": stage2_system_prompt
        },
        {
            "role": "user",
            "content": user_message
        }
    ]

    model: Stage2 = await instructor.completion(messages, Stage2)
    if model.questions:
        add_message_to_conversation(conversation, "assistant", model.questions)
    elif model.rewritten_primary_prompt:
        filter.primary_prompt = model.rewritten_primary_prompt
        filter.name = model.name
        db.update("filters", filter.model_dump())
        add_message_to_conversation(conversation, "assistant", "If you like this prompt and are ready to move on, say 'yes'. Otherwise tell me what to change or improve:\n" + model.rewritten_primary_prompt)
    else:
        add_message_to_conversation(conversation, "assistant", "I'm sorry, I didn't understand that. Please try again.")
        logging.error("Instructor call with Stage1_1 didn't return a valid model. User id: " + str(event.user_id) + "\n" + str(model))

async def build_filter_prompt(conversation: Conversation, event: MessageEvent, filter: Filter):  # Build the filter prompt
    logging.info(f"Received event in the build_filter_prompt function")
    user_message = event.message
    if user_message.lower().replace(" ", "") == "yes": # User is satisfied with the filter prompt
        if filter.target == 'reports':
            conversation.stage = 4
            conversation.cached_messages = []
            db.update("conversations", conversation.model_dump())
            add_message_to_conversation(conversation, "assistant", ask_for_report_guide)
            return
        else:
            conversation.cached_messages = []
            db.update("conversations", conversation.model_dump())
            await build_report_guide(conversation, event, filter)
            add_message_to_conversation(conversation, "assistant", end_of_stage1_message)
            await build_filter(filter)
    
    messages = conversation.cached_messages + [
        {
            "role": "system",
            "content": stage3_system_prompt
        },
        {
            "role": "user",
            "content": user_message
        }
    ]
    
    model: Stage3 = await instructor.completion(messages, Stage3)
    if model.questions:
        add_message_to_conversation(conversation, "assistant", model.questions)
    elif model.filter_prompt:
        filter.filter_prompt = model.filter_prompt
        db.update("filters", filter.model_dump())
        add_message_to_conversation(conversation, "assistant", "If you like this prompt and are ready to move on, say 'yes'. Otherwise tell me what to change or improve:\n" + model.filter_prompt)
    else:
        add_message_to_conversation(conversation, "assistant", "I'm sorry, I didn't understand that. Please try again.")
        logging.error("Instructor call with Stage1_2 didn't return a valid model. User id: " + str(event.user_id) + "\n" + str(model))

async def build_report_guide(conversation: Conversation, event: MessageEvent, filter: Filter): # Build the report guide
    logging.info(f"Received event in the build_report_guide function")
    user_message = event.message
    if user_message.lower().replace(" ", "") == "yes": # User is satisfied with the report guide
        conversation.stage = 5
        conversation.cached_messages = []
        db.update("conversations", conversation.model_dump())
        add_message_to_conversation(conversation, "assistant", end_of_stage1_message)
        new_filter_id = generate_uuid()
        conversation.id = new_filter_id
        filter.id = new_filter_id
        filter.messages = conversation.messages
        user = db.query("users", event.user_id)
        user["filters"][new_filter_id] = filter.name 
        db.update("users", user)
        db.insert("conversations", conversation.model_dump())
        db.insert("filters", filter.model_dump())
        initialize_filter_chat(event.user_id)

        event.filter_id = new_filter_id
        await build_filter(filter)

    messages = conversation.cached_messages + [
        {
            "role": "system",
            "content": stage4_system_prompt
        },
        {
            "role": "user",
            "content": user_message
        }
    ]
    
    model: Stage4 = await instructor.completion(messages, Stage4)
    if model.questions:
        add_message_to_conversation(conversation, "assistant", model.questions)
    elif model.report_guide:
        filter.report_guide = model.report_guide
        db.update("filters", filter.model_dump())
        add_message_to_conversation(conversation, "assistant", "If you like this report guide and are ready to move on, say 'yes'. Otherwise tell me what to change or improve:\n" + model.report_guide)
    else:
        add_message_to_conversation(conversation, "assistant", "I'm sorry, I didn't understand that. Please try again.")
        logging.error("Instructor call with Stage1_3 didn't return a valid model. User id: " + str(event.user_id) + "\n" + str(model))

async def build_filter(filter: Filter): # Extract filters from the prompts
    logging.info(f"Building filter")
    filter_prompt = filter.filter_prompt
    messages = [
        {
            "role": "system",
            "content": extract_filters_system_prompt
        },
        {
            "role": "user",
            "content": filter_prompt
        }
    ]
    
    model: ExtractedFilters = await instructor.completion(messages, ExtractedFilters)
    if model.return_cap:
        filter.return_cap = model.return_cap
    if model.filter_period:
        filter.filter_period = model.filter_period
    if model.usernames:
        filter.usernames = model.usernames
    if model.only_search_specified_usernames:
        filter.only_search_specified_usernames = model.only_search_specified_usernames
    
    db.update("filters", filter.model_dump())

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
