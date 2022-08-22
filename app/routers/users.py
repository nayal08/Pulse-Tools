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
async def getreactions(slug: str, db: Session = Depends(get_db)):
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
        return jsonify_res(success=True, data=reaction_data)
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
    res="""
    SELECT i.full_name,i.slug,i.image,a.founder,a.investor,a.whale,a.influencer,
    SUM(case when up then 1 else 0 END) as up,SUM(case when down then 1 else 0 END) as down
    FROM influencers i
    inner join achievements as a ON a.influencer_id=i.id 
    left join votes ON votes.influencer_id=i.id 
    WHERE a.influencer_id=i.id 
    GROUP BY i.full_name,i.slug,i.image,a.founder,a.investor,a.whale,a.influencer
    ORDER BY up DESC;
    """
    df = pd.read_sql(res, engine)
    newdata = df.to_dict('records')
    print(len(newdata))
    countdata=page*page_size
    initialpage=countdata-page_size
    totaldatacount=len(newdata)
    data = []
    for currpage in range(int(len(newdata)/page_size)+2):
        if page==0:
            break
        elif currpage==page:
            if countdata>len(newdata):
                data=newdata[initialpage:]
                break
            else:
                data=newdata[initialpage:countdata]
                break
        else:
            pass
    return jsonify_res(success=True, data=data, totaldatacount=totaldatacount)
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






