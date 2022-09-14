from __future__ import with_statement
import requests
from fastapi import FastAPI, HTTPException, Depends, Request
from fastapi.responses import JSONResponse
from fastapi_jwt_auth import AuthJWT
from fastapi_jwt_auth.exceptions import AuthJWTException
from fastapi import APIRouter, Depends, HTTPException, status
from ..commons.dependencies import *
from .. import models, schemas
from ..database import *
from passlib.context import CryptContext
from jose import JWTError, jwt
from fastapi.security import OAuth2PasswordBearer
from fastapi.responses import JSONResponse
from datetime import datetime, timedelta
from fastapi.encoders import jsonable_encoder
from app.schemas import *
from app.models import *
import uuid
import sys

@router.post("/add-project")
async def addProject(addproject:schemas.AddProject,db: Session = Depends(get_db)):
    print(addproject.userid, type(addproject.userid))
    try:
        AddProject = Project(   slug=str(uuid.uuid1()),
                                name= addproject.name,
                                userid=addproject.userid,
                                token_symbol=addproject.token_symbol,
                                sub_heading=addproject.sub_heading,
                                image=addproject.image,
                                about=addproject.about
                            )
        db.add(AddProject)
        db.commit()
        return jsonify_res(success=True, message="Created successfully")
    except:
        exc_type, exc_obj, exc_tb = sys.exc_info()
        fname = os.path.split(exc_tb.tb_frame.f_code.co_filename)[1]
        print(exc_type, fname, exc_obj, exc_tb.tb_lineno)

@router.get("/get-project")
async def getProjects(slug: str, db: Session = Depends(get_db)):
    project= db.query(Project).filter(Project.slug == slug).first()
    if project:
        data=jsonable_encoder(project)
        return jsonify_res(success=True, Influencers=data)
    else:
        return jsonify_res(success=False,Influencers="no project available with given slug")

@router.get("/project-search")
async def getallProjects(name: str, db: Session = Depends(get_db)):
    search = "%{}%".format(name)
    projects = db.query(Project).with_entities(Project.slug,Project.sub_heading,Project.name,Project.image).filter(Project.verify==True).filter(Project.name.ilike(search)).all()
    i=0
    data=[]
    if projects:
        while i < len(projects):
            singleproject = jsonable_encoder(projects[i])
            data.append(singleproject)
            i+=1
        return jsonify_res(success=True, Influencers=data)
    else:
        return jsonify_res(success=False, Influencers="no project available with given name")

@router.post("/project-filter")
async def getallfilter(project_filter:schemas.Projectfilters, db: Session = Depends(get_db)):
    if project_filter.filters[1]['sort_by'] == 'new':
        projects = db.query(Project).join(
            ProjectType, ProjectType.project_id == Project.id).join(ProjectSubType, ProjectSubType.project_type == ProjectType.project_id, isouter=True).join(
                ProjectSocial, ProjectSocial.project_id == Project.id, isouter=True).filter(ProjectType.type == project_filter.filters[0]["category"]).filter(
                    ProjectSubType.subtype == project_filter.filters[0]["sub_category"]).with_entities(
                        Project.name, Project.sub_heading, Project.token_symbol, Project.image, ProjectType.type, ProjectSubType.subtype, Project.slug, ProjectSocial.website).order_by(
                            Project.add_ts.desc()).all()
    
    elif project_filter.filters[1]['sort_by'] == "old":
        projects = db.query(Project).join(
            ProjectType, ProjectType.project_id == Project.id).join(ProjectSubType, ProjectSubType.project_type == ProjectType.project_id, isouter=True).join(
                ProjectSocial, ProjectSocial.project_id == Project.id, isouter=True).filter(ProjectType.type == project_filter.filters[0]["category"]).filter(
                    ProjectSubType.subtype == project_filter.filters[0]["sub_category"]).with_entities(
                        Project.name, Project.sub_heading, Project.token_symbol, Project.image, ProjectType.type, ProjectSubType.subtype, Project.slug, ProjectSocial.website).order_by(
                            Project.add_ts).all()
    
    elif project_filter.filters[1]['sort_by'] == "a-z":
        projects = db.query(Project).join(
            ProjectType, ProjectType.project_id == Project.id).join(ProjectSubType, ProjectSubType.project_type == ProjectType.project_id, isouter=True).join(
                ProjectSocial, ProjectSocial.project_id == Project.id, isouter=True).filter(ProjectType.type == project_filter.filters[0]["category"]).filter(
                    ProjectSubType.subtype == project_filter.filters[0]["sub_category"]).with_entities(
                        Project.name, Project.sub_heading, Project.token_symbol, Project.image, ProjectType.type, ProjectSubType.subtype, Project.slug, ProjectSocial.website).order_by(
                            Project.name).all()
    print(projects)
    return projects

@router.get("/get-all-projects")
async def getallfilter(db: Session = Depends(get_db)):
    projects = db.query(Project).join(ProjectType, ProjectType.project_id == Project.id).join(ProjectSubType, ProjectSubType.project_type == ProjectType.project_id, isouter=True).join(
        ProjectSocial, ProjectSocial.project_id == Project.id, isouter=True).with_entities(
            Project.name, Project.sub_heading, Project.token_symbol, Project.image, ProjectType.type, ProjectSubType.subtype, Project.slug, ProjectSocial.website).all()
    return projects   

        




