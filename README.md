# Salary Calculator (מחשבון שכר)

A web app that calculates take-home pay from an Excel timesheet. It handles regular hours, night/weekend shifts (1.5x), vacation days, and travel refunds.

## Prerequisites

- Python 3.8+
- A modern browser

## Setup

```bash
# 1. Create and activate a virtual environment (recommended)
python -m venv .venv
# Windows:
.venv\Scripts\activate
# Mac/Linux:
source .venv/bin/activate

# 2. Install dependencies
pip install -r requirements.txt
```

## Running Locally

Start the backend from the `api/` folder:

```bash
cd api
uvicorn main:app --reload
```

The server will be available at `http://127.0.0.1:8000`.

> **Tip:** You can also run `python main.py` directly from the `api/` folder — it does the same thing.

Then open `src/homepage.html` in your browser.

## Usage

1. Enter your hourly rate (שכר לשעה)
2. Upload your Excel timesheet (.xlsx / .xls)
3. Click **חשב** — the breakdown will appear below

## Project Structure

```
salary calc/
├── api/
│   ├── main.py          # FastAPI server
│   └── calcsalary.py    # Calculation logic
├── src/
│   ├── homepage.html    # Frontend
│   ├── script.js
│   └── style.css
└── requirements.txt
```
