# from curses import flash
from __future__ import with_statement
from queue import Empty
import ssl
import requests
import asyncpraw
from operator import itemgetter
from dateutil import parser
import feedparser
import requests
from fastapi import FastAPI, HTTPException, Depends, Request
from fastapi.responses import JSONResponse
from fastapi_jwt_auth import AuthJWT
from fastapi_jwt_auth.exceptions import AuthJWTException
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
import tweepy
from web3.auto import w3
from eth_account.messages import encode_defunct
from hexbytes import HexBytes

# USERS_REDIS_HOST = os.getenv("PULSETOOLS_REDIS_HOST")

USERS_REDIS_HOST = os.getenv("PULSETOOLS_REDIS_HOST")
USERPOOL = redis.ConnectionPool(host=USERS_REDIS_HOST, port=6379, db=0, decode_responses=True)
redisClient = redis.StrictRedis(connection_pool=USERPOOL, decode_responses=True)
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
        check = db.query(SocialLinks, Influencers).filter(SocialLinks.influencer_id==Influencers.id).filter(Influencers.slug==links.slug).with_entities(SocialLinks.discord,SocialLinks.influencer_id,SocialLinks.telegram,SocialLinks.twitter,Influencers.slug).all()
        if len(check)!=0:
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
            if data:
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
        influencer_data = jsonable_encoder(influencer_data)

        if influencer_data:
            device_id = db.query(Reactions).filter(
                Reactions.device_id == reaction.device_id, Reactions.influencer_id == influencer_data["id"]).first()
            devicedata=jsonable_encoder(device_id)
            if device_id: 
                update_data={
                    Reactions.dislike:reaction.dislike,
                    Reactions.heart:reaction.heart,
                    Reactions.smiley:reaction.smiley,
                    Reactions.super_duper:reaction.super_duper
                    }
                db.query(Reactions).filter(Reactions.device_id ==devicedata["device_id"],
                                             Reactions.influencer_id == influencer_data["id"]).update(update_data)
                db.commit()

                res="""
                select SUM(case when super_duper then 1 else 0 END) as count_super_duper,SUM(case when smiley then 1 else 0 END) as count_smiley,
                SUM(case when heart then 1 else 0 END) as count_heart,SUM(case when dislike then 1 else 0 END) as count_dislike FROM reactions r where r.influencer_id={};
                """.format(influencer_data["id"])
                
                df = pd.read_sql(res, engine)
                reaction_data = df.to_dict('records')

                reactions = db.query(Reactions).with_entities(Reactions.dislike,
                                                                Reactions.heart,
                                                                Reactions.smiley,
                                                                Reactions.super_duper
                                                                ).filter(Reactions.device_id == reaction.device_id,Reactions.influencer_id==influencer_data["id"]).first()
                reaction_status=jsonable_encoder(reactions)

                data={"reactions_count":reaction_data,"reaction_status":reaction_status}
                return jsonify_res(success=True, message="reactions Updated!",data=data)
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
                db.refresh(dbreactions)
                reactions = db.query(Reactions).filter(Reactions.influencer_id==data["id"]).first()
                data = jsonable_encoder(reactions)
                influencer_id = data["influencer_id"]
                res = """
                select SUM(case when super_duper then 1 else 0 END) as count_super_duper,SUM(case when smiley then 1 else 0 END) as count_smiley,
                SUM(case when heart then 1 else 0 END) as count_heart,SUM(case when dislike then 1 else 0 END) as count_dislike FROM reactions r where r.influencer_id={};
                """.format(influencer_id)

                df = pd.read_sql(res, engine)
                reaction_data = df.to_dict('records')

                reactions = db.query(Reactions).with_entities(
                    Reactions.dislike,
                    Reactions.heart,
                    Reactions.smiley,
                    Reactions.super_duper
                ).filter(Reactions.device_id == reaction.device_id, Reactions.influencer_id == influencer_data["id"]).first()

                reaction_status = jsonable_encoder(reactions)
                data = {"reactions_count": reaction_data,"reaction_status": reaction_status}
                return jsonify_res(success=True, message="reactions created!",data=data)

        else:
            return jsonify_res(message="No influencer account associated with given slug")
    except:
        exc_type, exc_obj, exc_tb = sys.exc_info()
        fname = os.path.split(exc_tb.tb_frame.f_code.co_filename)[1]
        print(exc_type, fname, exc_obj, exc_tb.tb_lineno)

@router.get("/get-reactions")
async def getreactions(slug: str,device_id:str, db: Session = Depends(get_db)):
    influencer_data = db.query(Influencers).filter(Influencers.slug == slug).first()
    if influencer_data:
        data = jsonable_encoder(influencer_data)
        influencer_id = data["id"]
        # reactions = db.query(Reactions).filter(Reactions.influencer_id == influencer_id).first()
        res = """
                select SUM(case when super_duper then 1 else 0 END) as count_super_duper,SUM(case when smiley then 1 else 0 END) as count_smiley,
                SUM(case when heart then 1 else 0 END) as count_heart,SUM(case when dislike then 1 else 0 END) as count_dislike FROM reactions r where r.influencer_id={};
                """.format(influencer_id)

        df = pd.read_sql(res, engine)
        reaction_data = df.to_dict('records')
        reactions = db.query(Reactions).with_entities(Reactions.dislike,
                                                      Reactions.heart,
                                                      Reactions.smiley,
                                                      Reactions.super_duper
                                                      ).filter(Reactions.device_id == device_id, Reactions.influencer_id == data["id"]).first()
        reaction_status = jsonable_encoder(reactions)

        data = {"reactions_count": reaction_data,
                "reaction_status": reaction_status}
        return jsonify_res(success=True, data=data)
    else:
        return jsonify_res(success=False, message="No reactions available with given id")

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
                return jsonify_res(success=True, message="Achievements created!")
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
        return jsonify_res(message="No achievements available with given id")

#<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<< Votes >>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>

@router.post("/create-votes")
async def createvotes(votes: schemas.VotesCreate, db: Session = Depends(get_db)):
    influencer_data = db.query(Influencers).filter(Influencers.slug == votes.slug).first()
    if influencer_data:
        influencer_data = jsonable_encoder(influencer_data)
        check_device = db.query(Votes).filter(
            Votes.device_id == votes.device_id, Votes.influencer_id == influencer_data["id"]).first()
        if check_device:
            data={}
            updatedata={Votes.up:votes.up,Votes.down:votes.down}
            db.query(Votes).filter(Votes.device_id == votes.device_id,
                                   Votes.influencer_id == influencer_data["id"]).update(updatedata)
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
            Influencers.image,
            Influencers.rating,
            SocialLinks.website,
            SocialLinks.twitter,
            SocialLinks.telegram,
            SocialLinks.github,
            SocialLinks.discord,
            Achievements.investor,
            Achievements.founder,
            Achievements.whale,
            Influencers.slug,
            Achievements.influencer,
            Influencers.bio,
                ).filter(
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
async def related(page:int,page_size:int,db: Session = Depends(get_db)):
    page=page
    limit=page_size
    offset=((limit*page)-limit)
    print(limit,offset)
    res="""
    SELECT i.full_name,i.slug,i.image,a.founder,a.investor,a.whale,a.influencer,
    SUM(case when up then 1 else 0 END) as up,SUM(case when down then 1 else 0 END) as down
    FROM influencers i
    inner join achievements as a ON a.influencer_id=i.id 
    left join votes ON votes.influencer_id=i.id 
    WHERE a.influencer_id=i.id
    GROUP BY i.full_name,i.slug,i.image,a.founder,a.investor,a.whale,a.influencer
    ORDER BY up DESC
    LIMIT {} OFFSET {};
    """.format(limit,offset)
    df = pd.read_sql(res, engine)
    newdata = df.to_dict('records')
    return jsonify_res(success=True, data=newdata)
#<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<< Populate script >>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>
@router.get("/populate-script")
async def script(db: Session = Depends(get_db)):
        f = open('app/routers/dbdata.json', encoding="utf8")
        data = json.load(f)
        for i in data:
            uid = str(uuid.uuid1())
            dbcreateinfluencer = Influencers(full_name=i["Token_name"],
                                            slug=uid,
                                            youtube_link=i["Youtube_link"],
                                            bio=i["About"],
                                            email="",
                                            rating=round(int(i["PHL_Score"])/10),
                                            image=i["Token_Symbol"],
                                            )
            db.add(dbcreateinfluencer)
            db.commit()
            influencer_data = db.query(Influencers).filter(
                Influencers.slug == uid).first()
            iddata = jsonable_encoder(influencer_data)
            if influencer_data:
                twitter_v = None
                telegram_v = None
                youtube_v = ""
                reddit_v = ""
                discord_v = ""
                medium_v = ""
                instagram_v = ""
                github_v = ""
                for j in range(len(i["Social_Links"])):
                    if "twitter" in i["Social_Links"][j]:
                        twitter_v = i["Social_Links"][j]
                    elif "https://t." in i["Social_Links"][j]:
                        telegram_v = i["Social_Links"][j]
                    elif "https://youtube." in i["Social_Links"][j]:
                        youtube_v = i["Social_Links"][j]
                    elif "https://reddit." in i["Social_Links"][j]:
                        reddit_v = i["Social_Links"][j]
                    elif "https://discord." in i["Social_Links"][j]:
                        discord_v = i["Social_Links"][j]
                    elif "https://medium." in i["Social_Links"][j]:
                        medium_v = i["Social_Links"][j]
                    elif "https://instagram." in i["Social_Links"][j]:
                        instagram_v = i["Social_Links"][j]
                    elif "https://github." in i["Social_Links"][j]:
                        github_v = i["Social_Links"][j]

                dbsocialmedia = SocialLinks(
                    influencer_id=iddata["id"],
                    telegram=telegram_v,
                    website=i["Token_link"],
                    twitter=twitter_v,
                    github=github_v,
                    discord=discord_v,
                    instagram=instagram_v,
                    medium=medium_v,
                    youtube=youtube_v,
                    reddit=reddit_v)
                db.add(dbsocialmedia)
                db.commit()
            whale=False
            influencer=False
            founder=False
            investor=False
            for j in range(len(i["Tags"])):
                if i["Tags"][j] =="RH":
                    founder=True
                elif i["Tags"][j] =="HEX-related":
                    whale=True
                    influencer=True
                elif i["Tags"][j] == "Airdrop":
                    investor=True
                elif i["Tags"][j] == "Sacrifice":
                    investor=True
                elif i["Tags"][j] == "App":
                    founder=True
                elif i["Tags"][j] == "RH":
                    founder=True
            achievements=Achievements(
                influencer_id=iddata["id"],
                founder=founder,
                influencer=influencer,
                whale=whale,
                investor=investor
                )
            db.add(achievements)
            db.commit()
        return "Completed!"

#<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<< Search Community >>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>> 
@router.get("/search-community")
async def search(search:str):
    try:
        res="""
        SELECT i.full_name,i.slug,i.image,a.founder,a.investor,a.whale,a.influencer,
        SUM(case when up then 1 else 0 END) as up,SUM(case when down then 1 else 0 END) as down
        FROM influencers i
        inner join achievements as a ON a.influencer_id=i.id 
        left join votes ON votes.influencer_id=i.id 
        WHERE a.influencer_id=i.id and i.full_name ILIKE '{}%%'
        GROUP BY i.full_name,i.slug,i.image,a.founder,a.investor,a.whale,a.influencer
        ORDER BY up DESC;
        """.format(search)
        df = pd.read_sql(res, engine)
        search_data = df.to_dict('records')
        print(search_data)
        return jsonify_res(success=True, data=search_data)

    except Exception as e:
        return "None"


#<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<< Related >>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>
@router.get("/related")
async def related(page:int,page_size:int,slug:str,db:Session = Depends(get_db)):
    influencer = db.query(Influencers).filter(Influencers.slug == slug).first()
    if influencer:
        influencer_data = jsonable_encoder(influencer)
        achievement = db.query(Achievements).filter(Achievements.influencer_id == influencer_data["id"]).first()
        achievement_data=jsonable_encoder(achievement)
        page = page
        limit = page_size
        offset = ((limit*page)-limit)
        print(limit, offset)
        res = """
                SELECT i.full_name,i.slug,i.image,a.founder,a.investor,a.whale,a.influencer,
                SUM(case when up then 1 else 0 END) as up,SUM(case when down then 1 else 0 END) as down
                FROM influencers i
                inner join achievements as a ON a.influencer_id=i.id 
                left join votes ON votes.influencer_id=i.id 
                WHERE a.influencer_id != {} and (a.influencer={} or a.investor={} or a.founder={} or a.whale={})
                GROUP BY i.full_name,i.slug,i.image,a.founder,a.investor,a.whale,a.influencer
                ORDER BY up DESC
                LIMIT {} OFFSET {};
                """.format(influencer_data["id"], achievement_data["influencer"], achievement_data["investor"], achievement_data["founder"], achievement_data["whale"],limit,offset)
        df = pd.read_sql(res, engine)
        newdata = df.to_dict('records')
        return jsonify_res(success=True, data=newdata)
        
#<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<< twitter >>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>
@router.get("/twitter")
async def twitter(slug: str, db: Session = Depends(get_db)):
    influencer = db.query(Influencers).filter(Influencers.slug == slug).first()
    if influencer:
        influencer_data = jsonable_encoder(influencer)
        query = db.query(SocialLinks, Influencers).with_entities(SocialLinks.twitter).filter(SocialLinks.influencer_id == Influencers.id).filter(Influencers.slug == slug).first()
        if query:
            data=jsonable_encoder(query)
            search_tweets = "#{} -filter:retweets".format(data["twitter"])
        else:
            search_tweets = "#{} -filter:retweets".format(influencer_data["full_name"])
        consumer_key = "2XLb0P7DezFX5cZ0ooqr9fmZn"
        consumer_secret = "vB5Vv0LPaaONNDVulvTTRDBW8XJUFfXsU2uJOMADGIRcgwf1GB"
        access_token = "1506977322590629896-wlEMm8jCwc1C0CtUdbcW2hEGLSZ6FH"
        access_token_secret = "I3Nd64N0LLp1SX7m74X9zfKQFTZT0LS7sDuX2ILGyDen5"
        bearer_token = "AAAAAAAAAAAAAAAAAAAAAE5UdwEAAAAAKrq2GwEt9osEV3RmmQXwoHjgFfw%3DGtXEKq5eHBJ8v2vK1vift3hnESb0BjQ56vvLyuA4mgZb5kr6Qx"

        auth = tweepy.OAuthHandler(consumer_key, consumer_secret)
        auth.set_access_token(access_token, access_token_secret)
        client = tweepy.Client(bearer_token, consumer_key,consumer_secret, access_token, access_token_secret)
        api = tweepy.API(auth, wait_on_rate_limit=True)
        search_tweets = "#HEXcrypto -filter:retweets"
        list1=[]
        for tweet in tweepy.Cursor(api.search_tweets, tweet_mode='extended', q=search_tweets, lang="en").items(100):
            twitter={}
            twitter["tweets"] = tweet.full_text
            datetime = tweet.created_at
            twitter["timestamp"] = datetime.timestamp()
            twitter["username"] = tweet.user.screen_name
            twitter["profile_picture"] = tweet.user.profile_image_url
            twitter["name"]=tweet.user.name
            if 'media' in tweet.entities:
                for image in tweet.entities['media']:
                    twitter["image"]=image['media_url']
            else:
                twitter["image"]=None

            list1.append(twitter)
        return jsonify_res(success=True,data=list1)
    return jsonify_res(message="No influencer associated with given slug")


#<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<< Metamask Api >>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>

@router.get("/get-nonce")
def nounce(ethwallet: str, db: Session = Depends(get_db)):
    nonce = str(random.randint(1111, 9999))
    ethwallet = ethwallet.lower()
    checkethwallet = db.query(Metamaskusers).filter(Metamaskusers.ethwallet == ethwallet).first()
    if checkethwallet:
        updatedata = {'nonce': nonce}
        db.query(Metamaskusers).filter(Metamaskusers.ethwallet == ethwallet).update(updatedata)
        db.commit()
    else:
        db_user = Metamaskusers(ethwallet=ethwallet, nonce=nonce.lower())
        db.add(db_user)
        db.commit()
        db.refresh(db_user)
    print(nonce, "nonce")
    return jsonify_res(success=True, nonce=nonce)


class Settings(BaseModel):
    authjwt_secret_key: str = "B6YX6ZMK6JCFNDPRELYQWFJUUJYCP6QL"

@AuthJWT.load_config
def get_config():
    return Settings()


# @router.exception_handler(AuthJWTException)
# def authjwt_exception_handler(request: Request, exc: AuthJWTException):
#     return JSONResponse(
#         status_code=exc.status_code,
#         content={"detail": exc.message}
#     )

@router.post("/post-signature")
def signature(credentials: schemas.Signature, db: Session = Depends(get_db), Authorize: AuthJWT = Depends()):
    wallet_address = credentials.wallet_address.lower()
    signature_value = credentials.signature.lower()
    checkethwallet = db.query(Metamaskusers).with_entities(Metamaskusers.nonce,Metamaskusers.id).filter(Metamaskusers.ethwallet == wallet_address).first()
    if checkethwallet:
        data = jsonable_encoder(checkethwallet)
        nonce = data["nonce"]
        message = encode_defunct(text=nonce)
        address = w3.eth.account.recover_message(
            message, signature=HexBytes(signature_value))
        print(address.lower())
        print(wallet_address)
        if address.lower() == wallet_address:
            updatedata = {'nonce': ""}
            db.query(Metamaskusers).filter(Metamaskusers.ethwallet ==wallet_address).update(updatedata)
            db.commit()
            access_token = Authorize.create_access_token(subject=data["id"], fresh=True)
            refresh_token = Authorize.create_refresh_token(subject=data["id"])
            jwt_tokens = {"access_token": access_token,
                          "refresh_token": refresh_token}
            return jsonify_res(success=True, jwt_token=jwt_tokens)
        else:
            raise HTTPException(status_code=401, detail="Bad request")
    return "No account availlable"


@router.post('/refresh')
def refresh(Authorize: AuthJWT = Depends()):
    """
    Refresh token endpoint. This will generate a new access token from
    the refresh token, but will mark that access token as non-fresh,
    as we do not actually verify a password in this endpoint.
    """
    Authorize.jwt_refresh_token_required()

    current_user = Authorize.get_jwt_subject()
    new_access_token = Authorize.create_access_token(
        subject=current_user, fresh=False)
    return {"access_token": new_access_token}

@router.post('/my-ethwallet')
def ethwallet(Authorize: AuthJWT = Depends(), db: Session = Depends(get_db)):
    Authorize.jwt_required()
    user_id = str(Authorize.get_jwt_subject())
    print(user_id)
    getethwallet= db.query(Metamaskusers).with_entities(Metamaskusers.ethwallet).filter(Metamaskusers.id==user_id).first()
    if getethwallet:
        data = jsonable_encoder(getethwallet)
        print(data["ethwallet"])
        return jsonify_res(success=True,ethwallet=data)
    return jsonify_res(success=False)

#<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<< pair id Data >>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>

# @router.post("/pairid-data")
# def pairid(pairs:dict=None, db: Session = Depends(get_db)):
#     API_ENDPOINT = "https://investdex.io/dexvision/all-chains-api/favorite_pairs_all"
#     i=0
#     data=[]
#     print(pairs['pairs'],"@@@@@@@@@@",type(pairs['pairs']))
#     print(len(pairs['pairs']))
#     while i <len(pairs['pairs']):
#         print(pairs['pairs'][i],"#######")
#         value = pairs['pairs'][i]
#         r = requests.post(url=API_ENDPOINT,json=value)
#         print(r)
#         # print(json.loads(r.text))
#         data.append(json.loads(r.text))
#     return jsonify_res(success=True,data=data)


@router.post("/pairid-data")
def pairid(pairs: dict = None, db: Session = Depends(get_db)):
    API_ENDPOINT = "https://investdex.io/dexvision/all-chains-api/favorite_pairs_all"
    r = requests.post(url=API_ENDPOINT, json=pairs)
    print(r.status_code)
    return jsonify_res(success=True,data=json.loads(r.text))

#<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<< Add and remove pair id >>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>
@router.post("/add-chain-pairid")
def addpairid(Addfavourte: schemas.Addfavourte,Authorize: AuthJWT = Depends(), db: Session = Depends(get_db)):
    Authorize.jwt_required()
    user_id = str(Authorize.get_jwt_subject())
    i=0
    # print(Addfavourte.favourites)
    while i< len(Addfavourte.favourites):
        print(Addfavourte.favourites[i].pair)
        user = db.query(Favouritecoins).filter(Favouritecoins.user_id == user_id).filter(
            Favouritecoins.pair == Addfavourte.favourites[i].pair, Favouritecoins.chain == Addfavourte.favourites[i].chain).first()
        if user:
            updatefavourite = {"pair": Addfavourte.favourites[i].pair, "chain": Addfavourte.favourites[i].chain}
            db.query(Favouritecoins).filter(Favouritecoins.user_id == user_id).filter(Favouritecoins.pair == Addfavourte.favourites[i].pair, Favouritecoins.chain == Addfavourte.favourites[i].chain).update(updatefavourite)
            db.commit()
        else:
            dbcreatefavourite = Favouritecoins(pair=Addfavourte.favourites[i].pair,
                                            chain=Addfavourte.favourites[i].chain,
                                                user_id=user_id,
                                            )
            db.add(dbcreatefavourite)
            db.commit()
        i+=1
    return jsonify_res(success=True, message="Added favourite chain pair successfully")


@router.post("/remove-chain-pairid")
def addpairid(Addfavourte: schemas.Addfavourte, Authorize: AuthJWT = Depends(), db: Session = Depends(get_db)):
    Authorize.jwt_required()
    user_id = str(Authorize.get_jwt_subject())
    i=0
    while i < len(Addfavourte.favourites):
        print(Addfavourte.favourites[i].pair)
        userfav = db.query(Favouritecoins).filter(Favouritecoins.user_id == user_id).filter(
            Favouritecoins.pair == Addfavourte.favourites[i].pair, Favouritecoins.chain == Addfavourte.favourites[i].chain).first()
        if userfav:
            db.delete(userfav)
            db.commit()
            db.close()
        i+=1
    return jsonify_res(success=True, message="Favoutite deleted")

# <<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<< For Web only >>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>
@router.get("/influencer-profiles")
async def profile(page:int,page_size:int,db: Session = Depends(get_db)):
    page = page
    limit = page_size
    offset = ((limit*page)-limit)
    print(limit, offset)
    check = db.query(Achievements, Influencers, SocialLinks).with_entities(
                Influencers.full_name,
                Influencers.image,
                Influencers.rating,
                SocialLinks.website,
                SocialLinks.twitter,
                SocialLinks.telegram,
                SocialLinks.github,
                SocialLinks.discord,
                Achievements.investor,
                Achievements.founder,
                Achievements.whale,
                Influencers.slug,
                Achievements.influencer,
                Influencers.bio,
            ).filter(
                Achievements.influencer_id == Influencers.id,
                SocialLinks.influencer_id == Influencers.id).order_by(Influencers.rating.desc()).limit(limit).offset(offset).all()
    print(len(jsonable_encoder(check)))
    return jsonify_res(success=True, data=jsonable_encoder(check))


#<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<< Lates news and feeds >>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>
@router.get("/feeds")
async def getfeeds():
    data = redisClient.get("posts_feed_details")
    if(data is not None):
        print('data from redis')
        data = json.loads(data)
        return data
    else:
        print('data from feeds')
        post_list = []
        urls = ["https://cointelegraph.com/rss", "https://www.coindesk.com/arc/outboundfeeds/rss/?outputType=xml", "https://pulse-chain.com/feed/",
                ]
        
        for feed_url in urls:
            if hasattr(ssl, '_create_unverified_context'):
                ssl._create_default_https_context = ssl._create_unverified_context
            blog_feed = feedparser.parse(feed_url)
            # getting lists of blog entries via .entries
            posts = blog_feed.entries
            # dictionary for holding posts details
            posts_details = {}

            
            # iterating over individual posts
            for post in posts:
                temp = dict()
                # return post
                # if any post doesn't have information then throw error.
                try:
                    temp["coin_name"] = blog_feed.feed.title
                    temp["title"] = post["title"]
                    temp["link"] = post["link"]
                    temp["description"] = post.description
                    strtime = post["published"]
                    epoch = parser.parse(strtime).timestamp()
                    temp["date"] = epoch
                    temp["images"] = post["media_content"][0]["url"]
                except:
                    pass

                post_list.append(temp)

        post_lists = sorted(post_list, key=itemgetter('date'), reverse=True)
        # storing lists of posts in the dictionary
        posts_details["posts"] = post_lists
        redisClient.setex("posts_feed_details",600, json.dumps(
            {"posts_details": posts_details}))
        # returning the details which is dictionary
        #posts_details
        return posts_details

#<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<< reddit hots >>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>

@router.get("/reddit-hots")
async def getreddithot():
    secret_key = 'IbrzQqRtuinpidPJmFKN7UyB0bIxGA'
    client_id = 'J2cEKnj2ZrX-m5GcTyfp8w'
    reddit = asyncpraw.Reddit(
        client_id=client_id, client_secret=secret_key, user_agent='Pulsechain')

    posts_details={}
    posts=[]
    pulsechain_subreddit = await reddit.subreddit('Pulsechain')
    async for post in pulsechain_subreddit.hot(limit=30):
        dict = {}
        dict["title"]=post.title
        dict["url"] = "https://www.reddit.com"+post.permalink
        if (".jpg" in post.url) or (".png" in post.url):
            dict["image"]=post.url
        else:
            dict["image"]=""
        dict["body"]=post.selftext
        dict["created"]=post.created

        dict["author"]=str(post.author)
        posts.append(dict)
    post_lists = sorted(posts, key=itemgetter('created'), reverse=True)
    posts_details["posts"] = post_lists
    print(posts)
    return posts_details








