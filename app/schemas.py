from typing import Optional
from datetime import datetime
from app.models import Influencers
from pydantic import BaseModel, Field, EmailStr

##############################################################################################################

class InfluencerCreate(BaseModel):
    full_name:str
    email:Optional[EmailStr]
    youtube_link:Optional[str]
    bio:Optional[str]
    rating:Optional[int]

class UpdateInfluencer(BaseModel):
    influencer_id:int
    email:Optional[EmailStr]
    youtube_link:Optional[str]
    bio:Optional[str]
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

class VotesCreate(BaseModel):
    influencer_id:int
    upvotes:Optional[bool]
    downvotes:Optional[bool]
    
