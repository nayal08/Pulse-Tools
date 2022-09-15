from lib2to3.pgen2.token import OP
from turtle import st
from typing import List, Optional,Dict,Union
from pydantic import BaseModel, Field, EmailStr

##############################################################################################################

class InfluencerCreate(BaseModel):
    full_name:str
    image: Optional[str]
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
    youtube:Optional[str]
    github:Optional[str]
    unicrypt:Optional[str]
    discord:Optional[str]
    medium:Optional[str]
    reddit:Optional[str]
    instagram:Optional[str]

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


class Signature(BaseModel):
    signature: str
    wallet_address: str


class pairs(BaseModel):
    pair:str
    chain:str

class Addfavourte(BaseModel):
    favourites:List[pairs]

class AddProject(BaseModel):
    name:str
    userid:int
    token_symbol:str
    sub_heading:str
    about:str
    image:str

class Projectfilters(BaseModel):
    filters:List[dict]

class Projectslikes(BaseModel):
    project_slug:str
    like:bool
    dislike:bool
    wallet:str











