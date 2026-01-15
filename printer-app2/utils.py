import random
import string
from .models import Users,Uploaded_Files
from sqlmodel import Session,select
from .db import engine
from datetime import datetime
from sqlalchemy import func
from fastapi import HTTPException
import PyPDF2 

def generate_license(session:Session):
    license:str = ""
    start_index = 0
    while True:
        for i in range(4):
            for m in range(4):
                value = random.choice(string.digits + string.ascii_lowercase)
                license+=value
                start_index+=1
            if i!=3:
                start_index+=1
                license+= '-'
                start_index+=1
        query = select(Users).where(Users.license_id == license)
        is_license_available = session.exec(query).one_or_none()
        if is_license_available == None:
            break
    return license

def generate_url(license:str):
    return license.replace("-","")

def isValidPrinter(printer_name:str):
    with Session(engine) as session:
        query = select(Users).where(Users.url_endpoint == printer_name)
        user = session.exec(query).one_or_none()
        if(user == None):
            return False
        else:
            current_date = datetime.now()
            expiry_date = user.expires_on

            if(current_date> expiry_date):
                return False
            return True
        
def generate_unique_file_id():
    with Session(engine) as session:
        try:
            query = select(func.max(Uploaded_Files.file_id))
            unique_id = session.exec(query).one() +1
            return unique_id
        except Exception as e:
        
            raise HTTPException(status_code=403, detail="Something went wrong")
        
def get_no_of_pages(file_name:str):
    if(file_name.endswith(".jpg") or file_name.endswith(".png") or file_name.endswith(".jpeg") or file_name.endswith(".webp")):
        return 1
    elif(file_name.endswith(".pdf")):
        with open(file_name,"rb") as f:
            reader = PyPDF2.PdfReader(f)
            return len(reader.pages)
    else:
        with open(file_name,"rb") as f:
            reader = PyPDF2.PdfReader(f)
            return len(reader.pages)