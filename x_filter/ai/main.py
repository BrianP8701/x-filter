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
    Stage1_1, stage1_1_system_prompt, stage1_2_system_prompt,
    ask_for_report_guide, Stage1_2, ask_for_filter_prompt, 
    stage1_3_system_prompt, Stage1_3, end_of_stage1_message,
    ExtractedFilters, extract_filters_system_prompt, 
    GenerateKeywordGroups, generate_keyword_groups_system_prompt
)
from x_filter.data.models.filter import Filter
from x_filter.data.models.conversation import Conversation
from x_filter.ai.instructor import Instructor
from x_filter.utils.conversational import add_message_to_conversation, send_message_to_user, initialize_filter_chat
from x_filter.utils.extraction import extract_filters, combine_keyword_groups
from x_filter.x.wrapper import XWrapper
from x_filter.data.models.events import MessageEvent

db = Database()
instructor = Instructor()
xwrapper = XWrapper()

async def handle_user_message(conversation: Conversation, event: MessageEvent, filter: Filter):
    """
    This function is called when a user sends a message to the bot.
    """
    logging.info(f"Received event in handler")
    logging.info(f"Conversation: {conversation}")
    if len(conversation.messages) == 0:
        logging.info(f"First message sent to user: {first_message}")
        send_message_to_user(conversation, first_message)
        return {"message": "First message sent."}
    
    logging.info(f"Adding message to conversation: {event.message}")

    add_message_to_conversation(conversation, "user", event.message)

    logging.info(f"Conversation after adding message: {conversation.stage}")

    match int(conversation.stage):
        case 1:
            await handle_stage_1(conversation, event, filter)
        case 2:
            await handle_stage_2(conversation, event, filter)
        case _:
            raise ValueError(f"Invalid stage: {conversation.stage}")


async def handle_stage_1(conversation: Conversation, event: MessageEvent, filter: Filter):
    """
    Determine the filter target, primary prompt and report guide if the filter target is 'reports'.
    """
    user_message = event.message

    if conversation.stage == 1.0: # Determine the filter target
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
            conversation.stage = 1.1
            conversation.cached_messages = []
            db.update("conversations", conversation.model_dump())
            if filter.target == "users":
                send_message_to_user(conversation, ask_for_primary_prompt_for_users)
            else:
                send_message_to_user(conversation, ask_for_primary_prompt_for_tweets)
        else:
            send_message_to_user(conversation, model.message)

    elif conversation.stage == 1.1: # Determine the primary prompt
        if user_message.lower().replace(" ", "") == "yes": # User is satisfied with the primary prompt
            conversation.stage = 1.2
            conversation.cached_messages = []
            db.update("conversations", conversation.model_dump())
            send_message_to_user(conversation, ask_for_filter_prompt)
            return

        messages = conversation.cached_messages + [
            {
                "role": "system",
                "content": stage1_1_system_prompt
            },
            {
                "role": "user",
                "content": user_message
            }
        ]

        model: Stage1_1 = await instructor.completion(messages, Stage1_1)
        if model.questions:
            send_message_to_user(conversation, model.questions)
        elif model.rewritten_primary_prompt:
            filter.primary_prompt = model.rewritten_primary_prompt
            db.update("filters", filter.model_dump())
            send_message_to_user(conversation, "If you like this prompt and are ready to move on, say 'yes'. Otherwise tell me what to change or improve:\n" + model.rewritten_primary_prompt)
        else:
            send_message_to_user(conversation, "I'm sorry, I didn't understand that. Please try again.")
            logging.error("Instructor call with Stage1_1 didn't return a valid model. User id: " + str(event.user_id) + "\n" + str(model))
    elif conversation.stage == 1.2: # Build the filter prompt
        if user_message.lower().replace(" ", "") == "yes": # User is satisfied with the primary prompt
            if filter.target is 'reports':
                conversation.stage = 1.3
                conversation.cached_messages = []
                db.update("conversations", conversation.model_dump())
                send_message_to_user(conversation, ask_for_report_guide)
                return
            else:
                conversation.stage = 2
                conversation.cached_messages = []
                db.update("conversations", conversation.model_dump())
                await handle_stage_2(conversation, event, filter)
        
        messages = conversation.cached_messages + [
            {
                "role": "system",
                "content": stage1_2_system_prompt
            },
            {
                "role": "user",
                "content": user_message
            }
        ]
        
        model: Stage1_2 = await instructor.completion(messages, Stage1_2)
        if model.questions:
            send_message_to_user(conversation, model.questions)
        elif model.filter_prompt:
            filter.filter_prompt = model.filter_prompt
            db.update("filters", filter.model_dump())
            send_message_to_user(conversation, "If you are satisfied with these filters, say 'yes'. Otherwise tell me what to change or improve:\n" + model.filter_prompt)
        else:
            send_message_to_user(conversation, "I'm sorry, I didn't understand that. Please try again.")
            logging.error("Instructor call with Stage1_2 didn't return a valid model. User id: " + str(event.user_id) + "\n" + str(model))
    elif conversation.stage == 1.3: # If filter target is 'reports', determine the report guide
        if user_message.lower().replace(" ", "") == "yes": # User is satisfied with the report guide
            conversation.stage = 2
            conversation.cached_messages = []
            db.update("conversations", conversation.model_dump())
            send_message_to_user(conversation, end_of_stage1_message)
            new_filter_id = generate_uuid()
            conversation.id = new_filter_id
            filter.id = new_filter_id
            db.insert("conversations", conversation.model_dump())
            db.insert("filters", filter.model_dump())

            initialize_filter_chat(event.user_id)

            event.filter_id = new_filter_id
            await handle_stage_2(conversation, event, filter)

        messages = conversation.cached_messages + [
            {
                "role": "system",
                "content": stage1_3_system_prompt
            },
            {
                "role": "user",
                "content": user_message
            }
        ]
        
        model: Stage1_3 = await instructor.completion(messages, Stage1_3)
        if model.questions:
            send_message_to_user(conversation, model.questions)
        elif model.report_guide:
            filter.report_guide = model.report_guide
            db.update("filters", filter.model_dump())
            send_message_to_user(conversation, "If you like this report guide and are ready to move on, say 'yes'. Otherwise tell me what to change or improve:\n" + model.report_guide)
        else:
            send_message_to_user(conversation, "I'm sorry, I didn't understand that. Please try again.")
            logging.error("Instructor call with Stage1_3 didn't return a valid model. User id: " + str(event.user_id) + "\n" + str(model))
    else:
        raise ValueError(f"Invalid stage: {conversation.stage}")

async def handle_stage_2(conversation: Conversation, event: MessageEvent, filter: Filter):
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
    extracted_filters: Filter = extract_filters(model, filter)
    db.update("filters", extracted_filters.model_dump())

    messages = [
        {
            "role": "system",
            "content": generate_keyword_groups_system_prompt
        },
        {
            "role": "user",
            "content": filter.primary_prompt
        }
    ]

    model: GenerateKeywordGroups = await instructor.completion(messages, GenerateKeywordGroups)
    filter.keyword_groups = combine_keyword_groups(filter.keyword_groups, model.keyword_groups)
    db.update("filters", filter.model_dump())

    # Execute search
    tweets = xwrapper.search_tweets(filter)
    specific_user_tweets = []
    for username in filter.usernames:
        user_id = xwrapper.get_user_id(username)
        users_tweets = xwrapper.get_users_tweets(user_id, days=filter.filter_period)
        specific_user_tweets += users_tweets
    tweets += specific_user_tweets
    
    return await handle_stage_3(conversation, event, filter)

async def handle_stage_3(conversation: Conversation, event: MessageEvent, filter: Filter):
    pass

