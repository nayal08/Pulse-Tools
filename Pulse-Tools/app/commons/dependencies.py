import requests
from fastapi import APIRouter, Depends, HTTPException, status, Response
from typing import Optional
from .. import schemas
from ..database import *
from passlib.context import CryptContext
from jose import JWTError, jwt
from fastapi.security import OAuth2PasswordBearer
from fastapi.responses import JSONResponse
from datetime import datetime, timedelta, date
from fastapi.encoders import jsonable_encoder
import redis
import os
import math
import random
import json
import string
import http.client
from ..models import *
from ..commons.error_msg import *
from ..commons.success_msg import *
from ..commons.info_msg import *
import traceback
import uuid
import os.path

import sqlalchemy
import psycopg2
from psycopg2 import errors
import re
from sqlalchemy import or_,and_

JWT_SECRET_KEY = os.getenv("JWT_SECRET_KEY")

ACCESS_TOKEN_EXPIRE_HOURS = 20
ALGORITHM = "HS256"

USERS_REDIS_HOST = os.getenv("REDIS_HOST")
USERPOOL = redis.ConnectionPool(host=USERS_REDIS_HOST, port=6379, db=0, decode_responses=True)
rclient = redis.StrictRedis(connection_pool=USERPOOL, decode_responses=True)

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="token")

import logging
from logging.handlers import TimedRotatingFileHandler


logger = logging.getLogger("Rotating Log")
logger.setLevel(logging.INFO)

handler = TimedRotatingFileHandler('./api.log',
                                   when="d",
                                   interval=7,
                                   backupCount=3)
logger.addHandler(handler)


def get_password_hash(password):
    return pwd_context.hash(password)

router = APIRouter()

#House of Commons
def jsonify_res(**args):
    res={}
    # print(args)
    flag = 0
    for arg in args.items():
        # print('****************')
        # print(arg[0])
        # print('****************')
        res[arg[0]]=arg[1]

        if(arg[0] == 'success' and arg[1] == False):
            flag = 1
    
    if(flag == 1):
        return JSONResponse(res,status_code=404)
    return JSONResponse(res)

def schema_to_dict(**args):
    for arg in args.items():
        print(arg)
    
def error_handler(value):
    def decorate(f):
        def applicator(*args, **kwargs):
            try:
                return f(*args,**kwargs)
            except Exception as e:
                traceback.print_exc()
                print(e)
                return value
        return applicator
    return decorate

# def generate_otp():
#     digits = [i for i in range(0, 10)]
#     generatedOTP = ""
#     for i in range(6):
#         index = math.floor(random.random() * 10)
#         generatedOTP += str(digits[index])
#     return generatedOTP


# async def get_current_user(token: str = Depends(oauth2_scheme)):
#     credentials_exception = HTTPException(
#         status_code=status.HTTP_401_UNAUTHORIZED,
#         detail="Session Expired! Please login to continue",
#         headers={"WWW-Authenticate": "Bearer"},
#     )
#     try:
#         payload = jwt.decode(token, TWITTER_SECRET_KEY, algorithms=[ALGORITHM])
#         redisPayload: str = payload.get("sub")
#         email = rclient.get(redisPayload)
#         user = get_user_by_email_without_sess(email)
#         if redisPayload is None:
#             raise credentials_exception
#     except JWTError as e:
#         print(e)
#         raise credentials_exception
#     if user is None:
#         print("user does not exist")
#         raise credentials_exception
#     return user

# async def get_current_active_user(current_user: schemas.UsersFetch = Depends(get_current_user)):
#     if not current_user.email_verified:
#         raise HTTPException(status_code=400, detail="Inactive user")
#     return current_user


# def get_user_by_email_without_sess(email: str):
#     db = SessionLocal()
#     return db.query(Users).with_entities(Users.name, Users.email, Users.phone_number, Users.email_verified,Users.updated_at,Users.created_at).filter(Users.email == email).first()

# def get_user_by_email(db: Session, email: str):
#     return db.query(Users).filter(Users.email == email).first()

# async def logout_current_user(token: str = Depends(oauth2_scheme)):
#     credentials_exception = HTTPException(
#         status_code=status.HTTP_401_UNAUTHORIZED,
#         detail="Session Expired! Please login to continue",
#         headers={"WWW-Authenticate": "Bearer"},
#     )
#     try:
#         payload = jwt.decode(token, TWITTER_SECRET_KEY, algorithms=[ALGORITHM])
#         redisPayload: str = payload.get("sub")
#         rclient.delete(redisPayload)
#         if redisPayload is None:
#             raise credentials_exception
#     except Exception as e:
#         print(e)
#         raise credentials_exception
#     return True