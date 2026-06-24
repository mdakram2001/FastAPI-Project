from fastapi import FastAPI, Path, HTTPException, Query
from fastapi.responses import JSONResponse
from pydantic import BaseModel, Field, computed_field
from typing import Annotated, Literal
import json

app = FastAPI()


class Patient(BaseModel):
    id: Annotated[str, Field(..., description='ID of the Patient')]
    name:Annotated[str, Field(..., description='Name of the Patient')]
    city:Annotated[str, Field(..., description='City of the Patient')]
    age:Annotated[int, Field(..., gt=0, lt=120, description='Age of the Patient')]
    gender:Annotated[Literal['Male', 'Female', 'Others'], Field(..., description='Gender of the Patient')]
    height:Annotated[float, Field(..., gt=0, description='Height of the Patient in mtrs')]
    weight:Annotated[float, Field(..., gt=0, description='Weight of the Patient in kgs')]

    @computed_field
    @property
    def bmi(self)-> float:
        return round(self.weight/(self.height**2), 2)
    
    @computed_field
    @property
    def verdict(self)->str:
        if self.bmi < 18.5:
            return 'underweight'
        elif self.bmi < 25:
            return 'normal'
        elif self.bmi < 30:
            return 'overweight'
        else:
            return 'obese'

def load_data():
    with open('patients.json', 'r') as f:
        data = json.load(f)

    return data

def save_data(data):
    with open('patients.json', 'w') as f:
        json.dump(data, f)

@app.get("/")
async def root():
    return {"message": "Home Page"}

@app.get("/about")
async def about():
    return {"message": "This is the about page"}

@app.get('/view')
def view(sort_by: str = Query('weight', description="Sorts the patients with the given parameters"), order: str = Query('asc', description="Sorts in Ascending or Descending Order")):
    valid_fields = ['height', 'weight', 'bmi']
    if sort_by not in valid_fields:
        raise HTTPException(400, detail="Invalid Field Selected")
    
    data = load_data()
    order_by = True if order == 'desc' else False
    sorted_data = sorted(data.values(), key=lambda x: x.get(sort_by, 0), reverse=order_by)
    return sorted_data

@app.get('/patient/{patient_id}')
def view_patient(patient_id: str = Path(..., description='ID of the Patient', examples='P001')):
    data = load_data()
    if patient_id in data:
        return data[patient_id]
    raise HTTPException(status_code=404, detail="Patient Not Found!")

@app.post('/create')
def create_patient(patient: Patient):

    # load
    data = load_data()

    # check
    if patient.id in data:
        raise HTTPException(status_code=400, detail="Patient already exists")
    # create
    data[patient.id] = patient.model_dump(exclude=['id'])

    # save
    save_data(data)

    # response
    return JSONResponse(status_code=201, content={'message':'Patient created successfully'})
