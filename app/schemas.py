from typing import Optional
from pydantic import BaseModel, Field, EmailStr

##############################################################################################################

class InfluencerCreate(BaseModel):
    full_name:str
    email:Optional[EmailStr]
    youtube_link:Optional[str]
    bio:Optional[str]
    rating:Optional[int]

class UpdateInfluencer(BaseModel):
    slug:str
    email:Optional[EmailStr]
    youtube_link:Optional[str]
    bio:Optional[str]
    rating:Optional[int]


class SocialMediaCreate(BaseModel):
    slug:str
    website:Optional[str]
    telegram:Optional[str]
    twitter:Optional[str]
    github:Optional[str]
    unicrypt:Optional[str]
    discord:Optional[str]

class ReactionCreate(BaseModel):
    slug:str
    device_id: str
    super_duper:bool
    smiley:bool
    heart:bool
    dislike:bool

class AchievementsCreate(BaseModel):
    slug: str
    founder: bool
    investor: bool
    whale:bool
    influencer:bool

class VotesCreate(BaseModel):
    slug: str
    device_id:str
    up:bool
    down:bool

