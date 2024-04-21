# x_filter/api/filter_settings.py
from fastapi import APIRouter, Depends
from pydantic import BaseModel
from typing import List, Dict, Optional

from x_filter import Database
from x_filter.data.models.filter import FilterTarget
from x_filter.utils.security import authenticate, generate_uuid
from x_filter.ai.filter import run_x_filter
from x_filter.ai.chosen import generate_keyword_groups

db = Database()
router = APIRouter()

class CreateEmptyFilterParams(BaseModel):
    filter_name: str
    
@router.post("/api/create_empty_filter/")
async def create_empty_filter(data: CreateEmptyFilterParams, user_id: str = Depends(authenticate)):
    user = db.query("users", user_id)
    filter_id = generate_uuid()
    user["filters"][filter_id] = data.filter_name
    db.update("users", user)
    empty_filter = {"id": filter_id, "user_id": user_id, "target": "tweets", "primary_prompt": "", "report_guide": "", "filter_prompt": "", "filter_period": 7, "only_search_specified_usernames": False,  "tweet_cap": 50, "user_cap": 20, "keyword_groups": [], "usernames": [], "name": data.filter_name}
    db.insert("filters", empty_filter)

    user.pop("password")
    user["id"] = user_id
    return {"user": user, "filter": empty_filter}

@router.get("/api/get_filter/{filter_id}")
async def get_filter(filter_id: str):
    filter = db.query("filters", filter_id)
    return {"filter": filter}

class UpdateFilterParams(BaseModel):
    filter: Dict
@router.post("/api/update_filter/")
async def update_filter(data: UpdateFilterParams):
    db.update("filters", data.filter)
    await generate_keyword_groups(data.filter)
