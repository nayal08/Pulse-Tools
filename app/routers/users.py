# from curses import flash
from __future__ import with_statement
from email import message
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
        influencer_name=influencer.full_name
        check_name=db.query(Influencers).filter(Influencers.full_name==influencer_name).first()
        if check_name:
            return jsonify_res(success=False, message="Name already present, it must be unique")
        influencer_ratings=influencer.rating
        if influencer_ratings<=10:
            dbcreateinfluencer=Influencers(full_name=influencer.full_name,email=influencer.email,
                youtube_link=influencer.youtube_link,bio=influencer.bio,rating=influencer.rating)
            # add_ts = created_at,
            # update_ts = created_at)
            db.add(dbcreateinfluencer)
            db.commit()
            return jsonify_res(success=True,message="Created successfully")
        return jsonify_res(success=False, message="Ratings should be less than or equal to 10")
    except:
        exc_type, exc_obj, exc_tb = sys.exc_info()
        fname = os.path.split(exc_tb.tb_frame.f_code.co_filename)[1]
        print(exc_type, fname, exc_obj, exc_tb.tb_lineno)

@router.get("/get-influencer")
async def getinfluencer(influencer_id: int, db: Session=Depends(get_db)):
    q=db.query(Influencers).filter(Influencers.id==influencer_id).all()
    if q:
        data=jsonable_encoder(q)
        return jsonify_res(success=True, message=data)
    else:
        return jsonify_res(success=False, message="no influencer available with given id")

@router.post("/update-influencer")
async def updateinfluencer(influencer:schemas.UpdateInfluencer, db:Session=Depends(get_db)):
    data=db.query(Influencers).filter(Influencers.id==influencer.influencer_id).first()
    influencer_ratings = influencer.rating
    if data:
        if influencer_ratings <= 10:
            updatedata = {Influencers.email: influencer.email, Influencers.youtube_link: influencer.youtube_link,
            Influencers.bio:influencer.bio,Influencers.rating:influencer.rating}

            db.query(Influencers).filter(Influencers.id == influencer.influencer_id).update(updatedata)
            db.commit()
            return jsonify_res(success=True, message="Influencer data updated")
        else:
            return jsonify_res(success=False, message="Ratings should be less than or equal to 10")
    return jsonify_res(success=False, message="No user present with the given user id")

#<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<< Social links >>>>>>>>>>>>>>>>>>>>>>

@router.post("/create-social-links")
async def createlinks(links:schemas.SocialMediaCreate,db:Session=Depends(get_db)):
    try:
        telegram_link = links.telegram
        twitter_link = links.twitter
        check_twitter = db.query(SocialLinks).filter(SocialLinks.twitter == twitter_link).all()
        check_telegram = db.query(SocialLinks).filter(SocialLinks.telegram == telegram_link).all()
        if check_twitter and check_telegram:
            return jsonify_res(success=False, message="Twitter and Telegram links already present, it must be unique")
        elif check_twitter:
            return jsonify_res(success=False, message="Twitter link already present, it must be unique")
        elif check_telegram:    
            return jsonify_res(success=False, message="Telegram link already present, it must be unique")

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
        return jsonify_res(success=True, message="social-links created!")

    except Exception as e:
        exc_type, exc_obj, exc_tb = sys.exc_info()
        fname = os.path.split(exc_tb.tb_frame.f_code.co_filename)[1]
        print(exc_type, fname, exc_obj, exc_tb.tb_lineno)
        return jsonify_res(success=True, message="twitter and telegram already present")

@router.get("/getsocial-links")
async def getsociallinks(influencer_id:int,db:Session=Depends(get_db)):
    check_user=db.query(SocialLinks).filter(SocialLinks.influencer_id==influencer_id).all()
    if check_user:
        data=jsonable_encoder(check_user)
        return jsonify_res(success=True, message=data)
    else:
        return jsonify_res(success=False, message="no social-links available with given id")

@router.post("/updatesocial-links")
async def updatesociallinks(links: schemas.SocialMediaCreate, db: Session = Depends(get_db)):
    telegram_link = links.telegram
    twitter_link = links.twitter
    check_twitter = db.query(SocialLinks).filter(SocialLinks.twitter == twitter_link).all()
    check_telegram = db.query(SocialLinks).filter(SocialLinks.telegram == telegram_link).all()
    if check_twitter and check_telegram:
        return jsonify_res(success=False, message="Twitter and Telegram link already present, it must be unique")
    elif check_twitter:
        return jsonify_res(success=False, message="Twitter link already present, it must be unique")
    elif check_telegram:
        return jsonify_res(success=False, message="Telegram link already present, it must be unique")
    check_user = db.query(SocialLinks).filter(SocialLinks.influencer_id == links.influencer_id).all()
    if check_user:
        data_to_update={SocialLinks.telegram:links.telegram,SocialLinks.twitter:links.twitter,SocialLinks.discord:links.discord,SocialLinks.github:links.github,SocialLinks.unicrypt:links.unicrypt,SocialLinks.website:links.website}
        db.query(SocialLinks).filter(SocialLinks.influencer_id == links.influencer_id).update(data_to_update)
        db.commit()
        return jsonify_res(success=True, message="Social links updated!")
    return jsonify_res(success=False, message="Sorry not updated!")

#<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<< Reactions >>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>

@router.post("/create-reactions")
async def createreactions(reaction:schemas.ReactionCreate,db:Session=Depends(get_db)):
    try:
        dbreactions=Reactions(
            influencer_id=reaction.influencer_id,
            super_duper=reaction.super_duper,
            smiley=reaction.smiley,
            heart=reaction.heart,
            dislike=reaction.dislike
        )
        db.add(dbreactions)
        db.commit()
        return jsonify_res(success=True, message="reactions created!")
    except:
        exc_type, exc_obj, exc_tb = sys.exc_info()
        fname = os.path.split(exc_tb.tb_frame.f_code.co_filename)[1]
        print(exc_type, fname, exc_obj, exc_tb.tb_lineno)

@router.get("/get-reactions")
async def getreactions(influencer_id:int,db:Session=Depends(get_db)):
    q=db.query(Reactions).filter(Reactions.influencer_id==influencer_id).all()
    if q:
        data=jsonable_encoder(q)
        return jsonify_res(success=True, message=data)
    else:
        return jsonify_res(success=False, message="no reactions available with given id")

#<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<< Achievements >>>>>>>>>>>>>>>>>>>>>>>>>>>>>.

@router.post("/create-achievements")
async def createachievements(achievements:schemas.AchievementsCreate,db:Session=Depends(get_db)):
    try:
        dbachievements=Achievements(
            influencer_id=achievements.influencer_id,
            founder=achievements.founder,
            investor=achievements.investor,
            whale=achievements.whale,
            influencer=achievements.influencer
        )
        db.add(dbachievements)
        db.commit()
        return jsonify_res(success=True, message="achievements created!")
    except:
        exc_type, exc_obj, exc_tb = sys.exc_info()
        fname = os.path.split(exc_tb.tb_frame.f_code.co_filename)[1]
        print(exc_type, fname, exc_obj, exc_tb.tb_lineno)

@router.get("/get-achievements")
async def getsociallinks(influencer_id:int,db:Session=Depends(get_db)):
    q=db.query(Achievements).filter(Achievements.influencer_id==influencer_id).all()
    if q:
        data=jsonable_encoder(q)
        return jsonify_res(success=True, message=data)
    else:
        return jsonify_res(success=False, message="no achievements available with given id")

#<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<< Votes >>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>
@router.post("/create-votes")
async def createvotes(influencer:schemas.VotesCreate,db: Session = Depends(get_db)):
    try:
        check_influencer = db.query(Influencers).filter(Influencers.id == influencer.influencer_id).first()
        influencer_upvotes=influencer.upvotes,
        influencer_downvotes=influencer.downvotes,
        
        if check_influencer:
            dbvotes=Votes(
                influencer_id=influencer.influencer_id,
                influencer_upvotes=influencer.upvotes,
                influencer_downvotes=influencer.downvotes)
            db.add(dbvotes)
            db.commit()
            return jsonify_res(success=True,message="Votes submitted successfully")
        return jsonify_res(success=True,message="No valid influencer id")
    except:
        exc_type, exc_obj, exc_tb = sys.exc_info()
        fname = os.path.split(exc_tb.tb_frame.f_code.co_filename)[1]
        print(exc_type, fname, exc_obj, exc_tb.tb_lineno)
        


@router.get("/votes")
async def votes(influencer_id:int,db:Session=Depends(get_db)):
    influencer_votes=db.query(Votes).filter(Votes.Influencers_id==influencer_id).first()
    if influencer_votes:
        votes_data=jsonable_encoder(influencer_votes)
        return jsonify_res(success=True,message=votes_data)
    return jsonify_res(success=False,message="no votes available for the given id")



#<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<< Details -------> influencer,socialmedia,achievements >>>>>>>>>>>>>>>>>>>

@router.get("/profile")
async def profile(influencer_id: int, db: Session = Depends(get_db)):
    influencer = db.query(Influencers).filter(Influencers.id == influencer_id).all()
    achievement = db.query(Achievements).filter(Achievements.influencer_id == influencer_id).all()
    if influencer:
        influencer_data=jsonable_encoder(influencer)
    if achievement:
        achievement_data=jsonable_encoder(achievement)
    if influencer and achievement:
        data={"influencer_data":influencer_data,"achievement_data":achievement_data}
        return jsonify_res(success=True, message=data)
    elif influencer:
        data = {"influencer_data": influencer_data,"achievement_data": "null"}
        return jsonify_res(success=True, message=data)
    else:
        return jsonify_res(success=False, message="No profile with given id")


@router.get("/community-ranking")
async def related(db: Session = Depends(get_db)):
    new_related = q = db.query(Achievements, Influencers, Votes).with_entities(Influencers.id, Influencers.full_name, Achievements.founder, Achievements.influencer, Achievements.investor,Achievements.whale, Votes.upvotes, Votes.downvotes).filter(Achievements.influencer_id == Influencers.id).filter(Achievements.influencer_id == Votes.influencers_id).all()
    new_related = jsonable_encoder(new_related)
    return new_related



# @router.get("/Community-ranking")
# async def communityranking()












