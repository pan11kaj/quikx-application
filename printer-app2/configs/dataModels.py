from pydantic import BaseModel


class RegisterationModel(BaseModel):
    email:str
    phone:str
    password:str
    name_of_client:str
    amount_per_page:float


class SirpurReviewModel(BaseModel):
    name:str
    email:str
    feedback:str
    suggestions:str

class QueueModel(BaseModel):
    printer_name:str
    queue_list:list

class QueueList(BaseModel):
    queue_list:list

class SirpurReportModel(BaseModel):
    file_id:str
    problem:str
    phone:str