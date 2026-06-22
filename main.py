from fastapi import FastAPI, Path, HTTPException, Query
import json

app = FastAPI()

def load_data():
    with open('patients.json', 'r') as f:
        data = json.load(f)

    return data

@app.get("/")
async def root():
    return {"message": "Hello World"}

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
def view_patient(patient_id: str = Path(..., description='ID of the Patient', example='P001')):
    data = load_data()
    if patient_id in data:
        return data[patient_id]
    raise HTTPException(status_code=404, detail="Patient Not Found!")
