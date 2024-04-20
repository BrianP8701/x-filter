from x_filter.ai.stages.stage2 import Stage2, extract_filters_system_prompt
from x_filter.ai.instructor import Instructor
import asyncio

instructor = Instructor()

async def test_stage(stage_model, stage_prompt, message):
    messages = [
        {
            "role": "system",
            "content": stage_prompt
        },
        {
            "role": "user",
            "content": message
        }
    ]
    
    response = await instructor.completion(messages, stage_model)
    print(response.model_dump())

message = """I want this to run every 2 days and only search for tweets from my followers. Maximum of 50 tweets."""
asyncio.run(test_stage(Stage2, extract_filters_system_prompt, message))
