from fastapi import FastAPI,Response
from dotenv import load_dotenv
import os
from datetime import datetime, timedelta
from .models import Users,Sirpur_Review,Sirpur_Report
from sqlmodel import Session,select
from .db import init_db,engine
from .routers import printers
from contextlib import asynccontextmanager
from .configs.dataModels import RegisterationModel,SirpurReviewModel,SirpurReportModel
from .utils import generate_license, generate_url
from fastapi.staticfiles import StaticFiles
from fastapi.middleware.cors import CORSMiddleware
from pathlib import Path

load_dotenv()

origins = [
    "*"
]

#setting up the environment variables:

static_files_dir = os.environ.get("STATIC_FILES_DIR")


# defining lifespan events for the database connection events 
@asynccontextmanager
async def lifespan(app:FastAPI):
    init_db()
    yield


app = FastAPI(lifespan=lifespan)

app.include_router(router=printers.router)
app.add_middleware(CORSMiddleware, allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"])

app.mount("/static-files",StaticFiles(directory=static_files_dir ),"files") 


#########configuring the redis database connection

@app.post("/registeration")
def index(data:RegisterationModel,response:Response):
    with Session(engine) as session:
        print(data.email)
        name_of_client = data.name_of_client
        email = data.email        
        query = select(Users).where(Users.email == email)
        is_user_exists = session.exec(query).one_or_none()
        if is_user_exists == None:
            try:
                license_id = generate_license(session=session)
                endpoint_url = generate_url(license_id)
                password = data.password
                phone = data.phone
                amount_per_page_in_rupee = data.amount_per_page
                amount_in_paisa:int = int(amount_per_page_in_rupee*100)

                expiry_date = datetime.now()+timedelta(days=30)
                new_client = Users(email=email,name_of_client=name_of_client,license_id=license_id,license_password=password,url_endpoint=endpoint_url,password=password,phone=phone,expires_on=expiry_date,amount_per_page=amount_in_paisa)
                session.add(new_client)
                session.commit()
                response.status_code = 200
                
                return {
                    "message":"successfully registered"
                }

            except Exception as e:
                response.status_code = 409
                print(e)
                return {
                    "message":"something went wrong"
                }

        else:
            response.status_code = 409

            return {
                "message":"Email is not valid"
            }


@app.post("/sirpur-review")
def sirpur_review(data:SirpurReviewModel,response:Response):
    try:
        with Session(engine) as session:
            new_suggestion = Sirpur_Review(name=data.name,email=data.email,feedback=data.feedback,suggestion=data.suggestions)
            session.add(new_suggestion)
            session.commit()
        response.status_code = 200
        return {
            "message":"submitted"
        }
            

    except Exception as e:
        response.status_code = 403
        return {
            "message":"failed"
        }
@app.post("/sirpur-report")
def sirpur_report(data:SirpurReportModel,response:Response):
    try:
        with Session(engine) as session:
            new_report = Sirpur_Report(file_id=data.file_id,problem=data.problem,phone=data.phone)
            session.add(new_report)
            session.commit()
        response.status_code = 200
        return {
            "message":"submitted"
        }
            

    except Exception as e:
        response.status_code = 403
        return {
            "message":"failed"
        }