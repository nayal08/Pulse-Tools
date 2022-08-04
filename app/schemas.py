from typing import Optional
from datetime import datetime
from pydantic import BaseModel, Field, EmailStr

##############################################################################################################

class InfluencerCreate(BaseModel):
    full_name:str
    email:EmailStr
    youtube_link:str
    bio:Optional [str]
    upvotes:int
    downvotes:int
    rating:int

class UpdateInfluencer(BaseModel):
    id=int
    full_name:Optional[str]
    email:Optional[EmailStr]
    youtube_link:Optional[str]
    bio:Optional[str]
    upvotes:Optional[int]
    downvotes:Optional[int]
    rating:Optional[int]


class SocialMediaCreate(BaseModel):
    influencer_id:int
    website:Optional[str]
    telegram:Optional[str]
    twitter:Optional[str]
    github:Optional[str]
    unicrypt:Optional[str]
    discord:Optional[str]

class ReactionCreate(BaseModel):
    influencer_id:int
    super_duper:Optional[int]
    smiley:Optional[int]
    heart:Optional[int]
    dislike:Optional[int]

class AchievementsCreate(BaseModel):
    influencer_id:int
    founder:Optional[str]
    investor:Optional[str]
    whale:Optional[str]
    influencer:Optional[str]


