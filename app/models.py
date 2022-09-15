# from enum import Enum
import email
from email.policy import default
from enum import unique
from itertools import chain
from operator import index
from sqlite3 import Timestamp
from tkinter.messagebox import NO
from unicodedata import name
from sqlalchemy import Boolean, Column, ForeignKey, Integer, String, TIMESTAMP, DECIMAL, Date, BIGINT, Enum
from sqlalchemy.sql import func

from .database import Base
from datetime import datetime

######################################### ADMIN ############################################

class Influencers(Base):
    __tablename__ ="influencers"

    id = Column(Integer, primary_key=True, autoincrement=True)
    slug=Column(String,unique=True,index=True)
    full_name=Column(String,default=None,unique=True,index=True)
    image=Column(String,default=None,index=True)
    email=Column(String,default=None,index=True)
    rating=Column(Integer,default=None)
    youtube_link=Column(String,default=None)
    bio=Column(String,default=None)
    add_ts=Column(TIMESTAMP, server_default=func.now())
    update_ts=Column(TIMESTAMP, onupdate=func.now())

class SocialLinks(Base):
    __tablename__="social_links"

    id = Column(Integer, primary_key=True, autoincrement=True, index=True)
    influencer_id=Column(Integer,ForeignKey(Influencers.id))
    website=Column(String, default=None)
    telegram=Column(String, default=None,unique=True)
    youtube=Column(String,default=None)
    twitter=Column(String, default=None,unique=True)
    github=Column(String, default=None)
    unicrypt=Column(String,default=None)
    discord=Column(String,default=None)
    reddit=Column(String,default=None)
    instagram=Column(String,default=None)
    medium = Column(String, default=None)
    update_ts=Column(TIMESTAMP, onupdate=func.now())
    

class Reactions(Base):
    __tablename__="reactions"
    id = Column(Integer, primary_key=True, autoincrement=True)
    device_id = Column(String, default=None)
    influencer_id=Column(Integer,ForeignKey(Influencers.id))
    super_duper=Column(Boolean,default=False)
    smiley=Column(Boolean,default=False)
    heart=Column(Boolean,default=False)
    dislike=Column(Boolean,default=False)
    update_ts=Column(TIMESTAMP, onupdate=func.now())

class Achievements(Base):
    __tablename__="achievements"
    id = Column(Integer, primary_key=True, autoincrement=True)
    influencer_id=Column(Integer,ForeignKey(Influencers.id))
    founder=Column(Boolean, default=False)
    investor=Column(Boolean, default=False)
    whale = Column(Boolean, default=False)
    influencer = Column(Boolean, default=False)
    update_ts=Column(TIMESTAMP, onupdate=func.now())

class Votes(Base):
    __tablename__="votes"
    id = Column(Integer, primary_key=True, autoincrement=True)
    influencer_id=Column(Integer,ForeignKey(Influencers.id))
    device_id = Column(String, default=None)
    up = Column(Boolean, default=False)
    down = Column(Boolean, default=False)

class Metamaskusers (Base):
    __tablename__ = "metamaskusers"
    id = Column(Integer, primary_key=True, index=True)
    username = Column(String, default=None)
    ethwallet = Column(String, unique=True, index=True, nullable=False)
    nonce = Column(String, unique=False, nullable=False)
    updated_at = Column(TIMESTAMP, onupdate=func.now())
    created_at = Column(TIMESTAMP, server_default=func.now())

class Favouritecoins(Base):
    id = Column(Integer, primary_key=True, index=True)
    user_id=Column(Integer,ForeignKey(Metamaskusers.id))
    pair=Column(String,default=None)
    chain=Column(String,default=None)
    update_ts = Column(TIMESTAMP, onupdate=func.now())

class Project(Base):
    id = Column(Integer, primary_key=True,index=True)
    verify= Column(Boolean,default=False)
    slug = Column(String, unique=True, index=True)
    about=Column(String,default=None)
    name=Column(String,default=None)
    token_symbol=Column(String,default=None)
    sub_heading=Column(String,default=None)
    image=Column(String,default=None)
    add_ts = Column(TIMESTAMP, server_default=func.now())
    update_ts = Column(TIMESTAMP, onupdate=func.now())

class ProjectSocial(Base):
    id = Column(Integer, primary_key=True, autoincrement=True, index=True)
    project_id = Column(Integer, ForeignKey(Project.id))
    website = Column(String, default=None)
    telegram = Column(String, default=None)
    youtube = Column(String, default=None)
    twitter = Column(String, default=None)
    github = Column(String, default=None)
    discord = Column(String, default=None)
    medium = Column(String, default=None)
    update_ts = Column(TIMESTAMP, onupdate=func.now())

class ProjectType(Base):
    id = Column(Integer, primary_key=True, autoincrement=True, index=True)
    project_id = Column(Integer, ForeignKey(Project.id))
    type = Column(String, default=None)

class ProjectSubType(Base):
    id = Column(Integer, primary_key=True, autoincrement=True, index=True)
    project_type = Column(Integer, ForeignKey(ProjectType.id))
    subtype = Column(String, default=None)

class ProjectChain(Base):
    id = Column(Integer, primary_key=True, autoincrement=True, index=True)
    project_id = Column(Integer, ForeignKey(Project.id))
    chain = Column(String, default=None)
    token_address = Column(String, default=None)

class ProjectStats(Base):
    id = Column(Integer, primary_key=True, autoincrement=True, index=True)
    project_stat = Column(Integer, ForeignKey(Project.id))
    circulating_supply=Column(Integer,default=None)
    volume=Column(Integer,default=None)
    market_cap = Column(Integer, default=None)
    price = Column(Integer, default=None)

class ProjectLikes(Base):
    __tablename__ = "projectlikes"
    id = Column(Integer, primary_key=True, autoincrement=True)
    project_id = Column(Integer, ForeignKey(Influencers.id))
    like = Column(Boolean, default=False)
    dislike = Column(Boolean, default=False)
    user_wallet = Column(String, ForeignKey(Metamaskusers.ethwallet))
    
















    

