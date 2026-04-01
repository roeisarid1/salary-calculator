import logging
from fastapi import FastAPI, UploadFile, File, Form, HTTPException
from fastapi.middleware.cors import CORSMiddleware
import pandas as pd
from io import BytesIO
from calcsalary import calc_salary as compute_salary

logging.basicConfig(level=logging.INFO, format="%(asctime)s %(levelname)s %(message)s")
logger = logging.getLogger(__name__)

app = FastAPI(title="מחשבון שכר", version="1.0.0")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["POST"],
    allow_headers=["*"],
)


@app.post("/calc")
async def calc_endpoint(file: UploadFile = File(...), salary: float = Form(...)):
    if salary <= 0:
        raise HTTPException(status_code=400, detail="שכר לשעה חייב להיות מספר חיובי")

    if not file.filename.endswith((".xlsx", ".xls")):
        raise HTTPException(status_code=400, detail="יש להעלות קובץ אקסל בלבד (.xlsx / .xls)")

    content = await file.read()
    if len(content) == 0:
        raise HTTPException(status_code=400, detail="הקובץ שהועלה ריק")

    try:
        df = pd.read_excel(BytesIO(content), header=2, engine="openpyxl")
    except Exception as e:
        logger.error(f"Failed to parse Excel file: {e}")
        raise HTTPException(status_code=422, detail="לא ניתן לקרוא את קובץ האקסל – בדוק שהפורמט תקין")

    if df.empty:
        raise HTTPException(status_code=422, detail="הקובץ אינו מכיל נתונים")

    try:
        result = compute_salary(df, salary)
    except KeyError as e:
        logger.error(f"Missing expected column: {e}")
        raise HTTPException(status_code=422, detail=f"עמודה חסרה בקובץ: {e}")
    except Exception as e:
        logger.error(f"Salary calculation failed: {e}")
        raise HTTPException(status_code=500, detail="שגיאה פנימית בחישוב השכר")

    logger.info(f"Calculated salary: {result['total_salary']} ₪ for {result['regular_hours']}h regular + {result['night_hours']}h night")
    return result


if __name__ == "__main__":
    import uvicorn
    import os
    uvicorn.run(
        "main:app",
        host=os.getenv("HOST", "127.0.0.1"),
        port=int(os.getenv("PORT", 8000)),
        reload=os.getenv("RELOAD", "true").lower() == "true",
    )
