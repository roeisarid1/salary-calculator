from fastapi import FastAPI, UploadFile, File, Form
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import FileResponse
from pathlib import Path
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

PROJECT_DIR = Path(__file__).resolve().parent

@app.get("/")
def serve_home():
    return FileResponse(PROJECT_DIR / "homepage.html")


@app.post("/calc")
async def calc_endpoint(
    file: UploadFile = File(...),
    salary: float = Form(...)
):
    content = await file.read()
    df = pd.read_excel(BytesIO(content), header=2, engine="openpyxl")
    result = compute_salary(df, salary)
    return result


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="127.0.0.1", port=8000, reload=True)
