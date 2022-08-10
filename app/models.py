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
    full_name=Column(String,default=None,unique=True,index=True)
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
    twitter=Column(String, default=None,unique=True)
    github=Column(String, default=None)
    unicrypt=Column(String,default=None)
    discord=Column(String,default=None)
    update_ts=Column(TIMESTAMP, onupdate=func.now())
    

class Reactions(Base):
    __tablename__="reactions"
    id = Column(Integer, primary_key=True, autoincrement=True)
    influencer_id=Column(Integer,ForeignKey(Influencers.id))
    super_duper=Column(Integer,default=0)
    smiley=Column(Integer,default=0)
    heart=Column(Integer,default=0)
    dislike=Column(Integer,default=0)
    update_ts=Column(TIMESTAMP, onupdate=func.now())

class Achievements(Base):
    __tablename__="achievements"
    id = Column(Integer, primary_key=True, autoincrement=True)
    influencer_id=Column(Integer,ForeignKey(Influencers.id))
    founder=Column(String, default=None)
    investor=Column(String, default=None)
    whale=Column(String, default=None)
    influencer=Column(String, default=None)
    update_ts=Column(TIMESTAMP, onupdate=func.now())

class DeviceId(Base):
    __tablename__="deviceids"
    id = Column(Integer, primary_key=True, autoincrement=True)
    influencer_id=Column(Integer,ForeignKey(Influencers.id))
    device_id = Column(String, default=None, unique=True)
    up=Column(Boolean,default="False")
    down=Column(Boolean,default="False")







    

