from sqlmodel import SQLModel,Field
from datetime import datetime,timedelta

class Users(SQLModel,table=True):
    sno:int = Field(default=None,primary_key=True)
    name_of_client:str = Field(nullable=False)
    email:str = Field(nullable=False,unique=True) # set by user
    phone:str = Field(nullable=False,max_length=13,min_length=10) #set by user
    license_id:str = Field(unique=True, max_length=19,min_length=19)
    license_password:str = Field(max_length=14) #set by user
    url_endpoint:str = Field(nullable=False)
    amount_per_page:int = Field(nullable=False)
    registered_on:datetime = Field(default_factory=datetime.now)
    expires_on:datetime = Field(nullable=False)

class Uploaded_Files(SQLModel, table=True):
    file_id:int = Field(primary_key=True,default=None)
    amount:int = Field(default="NOT INITIATED",nullable=False)
    no_of_pages:int = Field(nullable=False)
    payment_id:str = Field(default="NOT INITIATED",nullable=False)
    printer_name:str
    status:str
    