# from curses import flash
from __future__ import with_statement
from email import message
import imp
from turtle import update
from urllib import response
from fastapi import APIRouter, Depends, HTTPException, status
from typing import Optional
from ..commons.dependencies import *
from .. import models, schemas
from ..database import *
from passlib.context import CryptContext
from jose import JWTError, jwt
from fastapi.security import OAuth2PasswordBearer
from fastapi.responses import JSONResponse
from datetime import datetime, timedelta
from fastapi.encoders import jsonable_encoder
import redis
import os
import random
import string
import json
import sys
from app.schemas import * 
from app.models import *

#<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<< Influencer >>>>>>>>>>>>>>>>>>>>>>>>>

@router.post("/create-influencer")
async def createinfluencer(influencer:schemas.InfluencerCreate,db:Session=Depends(get_db)):
    try:
        created_at = datetime.now()
        dbcreateinfluencer=Influencers(
            full_name=influencer.full_name,
            email=influencer.email,
            youtube_link=influencer.youtube_link,
            bio=influencer.bio,
            upvotes=influencer.upvotes,
            downvotes=influencer.downvotes,
            rating=influencer.rating,
            add_ts = created_at,
            update_ts = created_at)

        db.add(dbcreateinfluencer)
        db.commit()
        return jsonify_res(success=True,message="Created successfully")
    except:
        exc_type, exc_obj, exc_tb = sys.exc_info()
        fname = os.path.split(exc_tb.tb_frame.f_code.co_filename)[1]
        print(exc_type, fname, exc_obj, exc_tb.tb_lineno)
@router.get("/get-influencer")
def getinfluencer(influencer_id:int,db:Session=Depends(get_db)):
    q=db.query(Influencers).filter(Influencers.id==influencer_id).all()
    if q:
        data=jsonable_encoder(q)
        return jsonify_res(success=True, message=data)
    else:
        return jsonify_res(success=False, message="no influencer available with given id")

# @router.update("update-influencer")
# async def updateinfluencer(influencer:schemas.InfluencerCreate, db:Session=Depends(get_db)):
#     q=db.query(Influencers).filter(influencer.id==influencer.id).all()
#     if q:
#         data=
#<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<< Social links >>>>>>>>>>>>>>>>>>>>>>

@router.post("/create-social-links")
def createlinks(links:schemas.SocialMediaCreate,db:Session=Depends(get_db)):
    try:
        created_at = datetime.now()
        dbsocialmedia=SocialLinks(
            influencer_id=links.influencer_id,
            website=links.website,
            telegram=links.telegram,
            twitter=links.twitter,
            github=links.github,
            unicrypt=links.unicrypt,
            discord=links.discord,
            update_ts=created_at
        )
        db.add(dbsocialmedia)
        db.commit()
        return jsonify_res(success=True, message="social-links created !")
    except:
        exc_type, exc_obj, exc_tb = sys.exc_info()
        fname = os.path.split(exc_tb.tb_frame.f_code.co_filename)[1]
        print(exc_type, fname, exc_obj, exc_tb.tb_lineno)
@router.get("/getsocial-links")
def getsociallinks(influencer_id:int,db:Session=Depends(get_db)):
    q=db.query(SocialLinks).filter(SocialLinks.influencer_id==influencer_id).all()
    if q:
        data=jsonable_encoder(q)
        return jsonify_res(success=True, message=data)
    else:
        return jsonify_res(success=False, message="no social-links available with given id")

#<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<< Reactions >>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>

@router.post("/create-reactions")
def createreactions(reaction:schemas.ReactionCreate,db:Session=Depends(get_db)):
    try:
        created_at = datetime.now()
        dbreactions=Reactions(
            influencer_id=reaction.influencer_id,
            super_duper=reaction.super_duper,
            smiley=reaction.smiley,
            heart=reaction.heart,
            dislike=reaction.dislike,
            update_ts=created_at,
        )
        db.add(dbreactions)
        db.commit()
        return jsonify_res(success=True, message="reactions created!")
    except:
        exc_type, exc_obj, exc_tb = sys.exc_info()
        fname = os.path.split(exc_tb.tb_frame.f_code.co_filename)[1]
        print(exc_type, fname, exc_obj, exc_tb.tb_lineno)
@router.get("/get-reactions")
def getreactions(influencer_id:int,db:Session=Depends(get_db)):
    q=db.query(Reactions).filter(Reactions.influencer_id==influencer_id).all()
    if q:
        data=jsonable_encoder(q)
        return jsonify_res(success=True, message=data)
    else:
        return jsonify_res(success=False, message="no reactions available with given id")

#<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<Achievements >>>>>>>>>>>>>>>>>>>>>>>>>>>>>.

@router.post("/create-achievements")
def createachievements(achievements:schemas.AchievementsCreate,db:Session=Depends(get_db)):
    try:
        created_at = datetime.now()
        dbachievements=Achievements(
            influencer_id=achievements.influencer_id,
            founder=achievements.founder,
            investor=achievements.investor,
            whale=achievements.whale,
            influencer=achievements.influencer,
            update_ts=created_at,
        )
        db.add(dbachievements)
        db.commit()
        return jsonify_res(success=True, message="achievements created!")
    except:
        exc_type, exc_obj, exc_tb = sys.exc_info()
        fname = os.path.split(exc_tb.tb_frame.f_code.co_filename)[1]
        print(exc_type, fname, exc_obj, exc_tb.tb_lineno)

@router.get("/get-achievements")
def getsociallinks(influencer_id:int,db:Session=Depends(get_db)):
    q=db.query(Achievements).filter(Achievements.influencer_id==influencer_id).all()
    if q:
        data=jsonable_encoder(q)
        return jsonify_res(success=True, message=data)
    else:
        return jsonify_res(success=False, message="no achievements available with given id")

