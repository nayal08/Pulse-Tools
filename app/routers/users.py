# from curses import flash
from __future__ import with_statement
from email import message
from sqlalchemy.sql import func
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
import pandas as pd
import redis
import os
import json
import sys
from app.schemas import * 
from app.models import *
import uuid

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
            dbcreateinfluencer=Influencers(full_name=influencer.full_name,
                                            slug=str(uuid.uuid1()),
                                            email=influencer.email,
                                            youtube_link=influencer.youtube_link,
                                            bio=influencer.bio,
                                            rating=influencer.rating
                                            )
            db.add(dbcreateinfluencer)
            db.commit()
            return jsonify_res(success=True,message="Created successfully")
        return jsonify_res(message="Ratings should be less than or equal to 10")
    except:
        exc_type, exc_obj, exc_tb = sys.exc_info()
        fname = os.path.split(exc_tb.tb_frame.f_code.co_filename)[1]
        print(exc_type, fname, exc_obj, exc_tb.tb_lineno)

@router.get("/get-influencer")
async def getinfluencer(slug: str, db: Session=Depends(get_db)):
    q=db.query(Influencers).filter(Influencers.slug==slug).all()
    if q:
        data=jsonable_encoder(q)
        return jsonify_res(success=True, Influencers=data)
    else:
        return jsonify_res(Influencers="no influencer available with given slug")

@router.post("/update-influencer")
async def updateinfluencer(influencer:schemas.UpdateInfluencer, db:Session=Depends(get_db)):
    data=db.query(Influencers).filter(Influencers.slug==influencer.slug).first()
    influencer_ratings = influencer.rating
    if data:
        if influencer_ratings <= 10:
            updatedata = {Influencers.email: influencer.email, Influencers.youtube_link: influencer.youtube_link,
            Influencers.bio:influencer.bio,Influencers.rating:influencer.rating}

            db.query(Influencers).filter(Influencers.slug == influencer.slug).update(updatedata)
            db.commit()
            return jsonify_res(success=True, message="Influencer data updated")
        else:
            return jsonify_res(message="Ratings should be less than or equal to 10")
    return jsonify_res(message="No user present with the given user id")

#<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<< Social links >>>>>>>>>>>>>>>>>>>>>>

@router.post("/create-social-links")
async def createlinks(links:schemas.SocialMediaCreate,db:Session=Depends(get_db)): 
    try:
        telegram_link = links.telegram
        twitter_link = links.twitter
        influencer_data = db.query(Influencers).filter(Influencers.slug == links.slug).first()
        if influencer_data:
            data=jsonable_encoder(influencer_data)
            social_info = db.query(SocialLinks).filter(SocialLinks.influencer_id == data["id"]).first()
            if social_info:
                return jsonify_res(success=False, message="Social media links already present for given id")

            else:
                check_twitter = db.query(SocialLinks).filter(SocialLinks.twitter == twitter_link).all()
                check_telegram = db.query(SocialLinks).filter(SocialLinks.telegram == telegram_link).all()
                influencer_data = db.query(Influencers).filter(Influencers.slug == links.slug).first()
                data=jsonable_encoder(influencer_data)
                if check_twitter and check_telegram:
                    return jsonify_res(message="Twitter and Telegram links already present, it must be unique")
                elif check_twitter:
                    return jsonify_res( message="Twitter link already present, it must be unique")
                elif check_telegram:    
                    return jsonify_res(message="Telegram link already present, it must be unique")

                created_at = datetime.now()
                dbsocialmedia=SocialLinks(
                    influencer_id=data["id"],
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
        return jsonify_res(message="No influencer account associated with given slug")

    except Exception as e:
        exc_type, exc_obj, exc_tb = sys.exc_info()
        fname = os.path.split(exc_tb.tb_frame.f_code.co_filename)[1]
        print(exc_type, fname, exc_obj, exc_tb.tb_lineno)

@router.get("/getsocial-links")
async def getsociallinks(slug: str, db: Session = Depends(get_db)):
    influencer_data = db.query(Influencers).filter(Influencers.slug == slug).first()
    if influencer_data:
        data=jsonable_encoder(influencer_data)
        check_user=db.query(SocialLinks).filter(SocialLinks.influencer_id==data["id"]).first()
        if check_user:
            data=jsonable_encoder(check_user)
            return jsonify_res(success=True, SocialLinks=data)
        else:
            return jsonify_res(message="no social-links available with given id")
    return jsonify_res(message="No influencer account associated with given slug")

@router.post("/updatesocial-links")
async def updatesociallinks(links: schemas.SocialMediaCreate, db: Session = Depends(get_db)):
    telegram_link = links.telegram
    twitter_link = links.twitter
    check_twitter = db.query(SocialLinks).filter(SocialLinks.twitter == twitter_link).all()
    check_telegram = db.query(SocialLinks).filter(SocialLinks.telegram == telegram_link).all()
    influencer_data = db.query(Influencers).filter(Influencers.slug == links.slug).first()
    if influencer_data:
        data = jsonable_encoder(influencer_data)
        if check_twitter and check_telegram:
            return jsonify_res(success=False, message="Twitter and Telegram link already present, it must be unique")
        elif check_twitter:
            return jsonify_res(success=False, message="Twitter link already present, it must be unique")
        elif check_telegram:
            return jsonify_res(success=False, message="Telegram link already present, it must be unique")
        check_user = db.query(SocialLinks).filter(SocialLinks.influencer_id == data["id"]).all()
        if check_user:
            data_to_update={SocialLinks.telegram:links.telegram,SocialLinks.twitter:links.twitter,SocialLinks.discord:links.discord,SocialLinks.github:links.github,SocialLinks.unicrypt:links.unicrypt,SocialLinks.website:links.website}
            db.query(SocialLinks).filter(SocialLinks.influencer_id == data["id"]).update(data_to_update)
            db.commit()
            return jsonify_res(success=True, message="Social links updated ")
        return jsonify_res(success=False, message="Sorry not updated ")
    return jsonify_res(success=False, message="No influencer account associated with given slug")

#<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<< Reactions >>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>

@router.post("/create-reactions")
async def createreactions(reaction:schemas.ReactionCreate,db:Session=Depends(get_db)):
    try:
        influencer_data = db.query(Influencers).filter(Influencers.slug == reaction.slug).first()
        if influencer_data:
            device_id = db.query(Reactions).filter(Reactions.device_id == reaction.device_id).first()
            if device_id: 
                update_data={
                    Reactions.dislike:reaction.dislike,
                    Reactions.heart:reaction.heart,
                    Reactions.smiley:reaction.smiley,
                    Reactions.super_duper:reaction.super_duper
                    }
                db.query(Reactions).filter(Reactions.device_id == reaction.device_id).update(update_data)
                return jsonify_res(success=True, message="reactions Upvaded!")
            else:
                data = jsonable_encoder(influencer_data)
                dbreactions=Reactions(
                    influencer_id=data["id"],
                    device_id=reaction.device_id,
                    super_duper=reaction.super_duper,
                    smiley=reaction.smiley,
                    heart=reaction.heart,
                    dislike=reaction.dislike
                )
                db.add(dbreactions)
                db.commit()
                return jsonify_res(success=True, message="reactions created!")
        else:
            return jsonify_res(message="No influencer account associated with given slug")
    except:
        exc_type, exc_obj, exc_tb = sys.exc_info()
        fname = os.path.split(exc_tb.tb_frame.f_code.co_filename)[1]
        print(exc_type, fname, exc_obj, exc_tb.tb_lineno)

@router.get("/get-reactions")
async def getreactions(slug: str, db: Session = Depends(get_db)):
    q=db.query(Reactions).filter(Reactions.influencer_id==slug).all()
    if q:
        data=jsonable_encoder(q)
        return jsonify_res(success=True, data=data)
    else:
        return jsonify_res(success=False, message="no reactions available with given id")

#<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<< Achievements >>>>>>>>>>>>>>>>>>>>>>>>>>>>>.

@router.post("/create-achievements")
async def createachievements(achievements:schemas.AchievementsCreate,db:Session=Depends(get_db)):
    try:
        influencer_data = db.query(Influencers).filter(Influencers.slug == achievements.slug).first()
        if influencer_data:
            data = jsonable_encoder(influencer_data)
            achievement = db.query(Achievements).filter(Achievements.influencer_id == data["id"]).first()
            # achievement_data = jsonable_encoder(achievement)
            if achievement:
                return jsonify_res(message="Achievements already present for the given slug")
            else:
                dbachievements=Achievements(
                    influencer_id=data["id"],
                    founder=achievements.founder,
                    investor=achievements.investor,
                    whale=achievements.whale,
                    influencer=achievements.influencer
                )
                db.add(dbachievements)
                db.commit()
                return jsonify_res(success=True, message="achievements created!")
        return jsonify_res(message="No influencer account associated with given slug")
    except:
        exc_type, exc_obj, exc_tb = sys.exc_info()
        fname = os.path.split(exc_tb.tb_frame.f_code.co_filename)[1]
        print(exc_type, fname, exc_obj, exc_tb.tb_lineno)

@router.get("/get-achievements")
async def getsociallinks(slug: str, db: Session = Depends(get_db)):
    influencer = db.query(Influencers).filter(Influencers.slug == slug).first()
    if influencer:
        data=jsonable_encoder(influencer)
        print(data["id"])
        achievement=db.query(Achievements).filter(Achievements.influencer_id == data["id"]).first()
        achievement_data=jsonable_encoder(achievement)
        return jsonify_res(success=True, data=achievement_data)
    else:
        return jsonify_res(message="no achievements available with given id")

#<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<< Votes >>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>

@router.post("/create-votes")
async def createvotes(votes: schemas.VotesCreate, db: Session = Depends(get_db)):
    influencer_data = db.query(Influencers).filter(Influencers.slug == votes.slug).first()
    if influencer_data:
        influencer_data = jsonable_encoder(influencer_data)
        check_device = db.query(Votes).filter(Votes.device_id == votes.device_id).first()
        if check_device:
            data={}
            updatedata={Votes.up:votes.up,Votes.down:votes.down}
            db.query(Votes).filter(Votes.device_id==votes.device_id,Votes.influencer_id==influencer_data["id"]).update(updatedata)
            db.commit()
            updata = db.query(Votes).filter(Votes.influencer_id == influencer_data["id"], Votes.up == True).count()
            downdata = db.query(Votes).filter(Votes.influencer_id == influencer_data["id"], Votes.down == True).count()
            data["updata"]=updata
            data["downdata"]=downdata
            data["up"]=votes.up
            data["down"]=votes.down
            return jsonify_res(success=True,message="Updated! device id already present.",data=data)
        else:
            dbdeviceid = Votes(
                influencer_id=influencer_data["id"],
                device_id=votes.device_id,
                up=votes.up,
                down=votes.down
                )
            db.add(dbdeviceid)
            db.commit()
            data={}
            updata = db.query(Votes).filter(Votes.influencer_id ==influencer_data["id"], Votes.up == True).count()
            downdata = db.query(Votes).filter(Votes.influencer_id ==influencer_data["id"], Votes.down ==True).count()
            data["updata"] = updata
            data["downdata"] = downdata
            data["up"] = votes.up
            data["down"] = votes.down
            return jsonify_res(success=True, message="votes created!", data=data)
    return jsonify_res(message="No influencer account associated with given slug")

#<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<< Details -------> influencer,socialmedia,achievements >>>>>>>>>>>>>>>>>>>

@router.get("/profile")
async def profile(slug: str, db: Session = Depends(get_db)):
    influencer = db.query(Influencers).filter(Influencers.slug ==slug).first()
    if influencer:
        influencer_data=jsonable_encoder(influencer)
        achievement = db.query(Achievements).filter(Achievements.influencer_id ==influencer_data["id"]).first()
        if achievement:
            check=db.query(Achievements,Influencers,SocialLinks).with_entities(
                Influencers.full_name,
                Influencers.rating,
                SocialLinks.website,
                SocialLinks.twitter,
                SocialLinks.telegram,
                SocialLinks.github,
                SocialLinks.discord,
                Achievements.investor,
                Achievements.founder,
                Achievements.whale,
                Achievements.influencer,
                Influencers.bio).filter(
                    Achievements.influencer_id == Influencers.id, 
                    Influencers.id == influencer_data["id"], 
                    SocialLinks.influencer_id == Influencers.id).all()
        if influencer and achievement:
            return jsonify_res(success=True,data=jsonable_encoder(check))
        elif influencer:
            data = {"influencer_data": influencer_data,"achievement_data": "null"}
            return jsonify_res(success=True, data=data)
        else:
            return jsonify_res(message="No profile with given id")
    return jsonify_res(message="No influencer profile associated with given slug")
    
#<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<< Community Ranking >>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>
@router.get("/community-ranking")
async def related(db: Session = Depends(get_db)):
    # res = {}
    res="""
    SELECT i.full_name,i.id,i.slug,a.founder,a.investor,a.whale,a.influencer,
    SUM(case when up then 1 else 0 END) as up,SUM(case when down then 1 else 0 END) as down
    FROM influencers i
    inner join achievements as a ON a.influencer_id=i.id 
    inner join votes ON votes.influencer_id=i.id 
    WHERE a.influencer_id=i.id 
    GROUP BY i.full_name,i.id,a.founder,a.investor,a.whale,a.influencer;
    """
    df = pd.read_sql(res, engine)
    data = df.to_dict('records')
    return jsonify_res(success=True,data=data)











