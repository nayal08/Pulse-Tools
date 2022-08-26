# from enum import Enum
import email
from email.policy import default
from enum import unique
from operator import index
from sqlite3 import Timestamp
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





    

