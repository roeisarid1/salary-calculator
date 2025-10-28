from fastapi import FastAPI, UploadFile, File, Form
from fastapi.middleware.cors import CORSMiddleware
import pandas as pd
from io import BytesIO
from calcsalary import calc_salary as compute_salary  

app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.post("/calc")
async def calc_endpoint(
    file: UploadFile = File(...),
    salary: float = Form(...)
):
    content = await file.read()
    df = pd.read_excel(BytesIO(content), header=2, engine="openpyxl")
    result = compute_salary(df, salary)
    return result
