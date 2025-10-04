import json
import random
import sys

import pandas as pd
from typing import Optional
from fastapi import FastAPI, UploadFile, File, Request, Form
from fastapi.responses import JSONResponse, HTMLResponse
from fastapi.templating import Jinja2Templates
from fastapi.staticfiles import StaticFiles
import uvicorn
import io
import os
from picker import generate_random_list

app = FastAPI()
templates = Jinja2Templates(directory="templates")
# app.mount("/static", StaticFiles(directory="static"), name="static")
uploaded_files = {}
@app.get("/", response_class=HTMLResponse)
async def home(request: Request):
    return templates.TemplateResponse("index.html", {"request": request})

@app.post("/upload")
async def upload_excel(file: UploadFile = File(...)):
    # Read Excel bytes into pandas DataFrame
    contents = await file.read()
    df = pd.read_excel(io.BytesIO(contents))
    uploaded_files["current"] = df  # store in memory

    # Columns to offer filters
    filter_columns = ["Tags", "Type"]  # replace with your column names

    # Get unique values per column
    unique_values = {}
    for col in filter_columns:
        if col in df.columns:
            unique_values[col] = pd.Series(
                                    [tag.strip() for sublist in df[col].dropna().str.split(',') for tag in sublist]
                                    ).unique().tolist()


    # Optional: preview first 10 rows, safely handle NaN

    return JSONResponse(content={
        "unique_values": unique_values
    })

@app.post("/analyze")
async def analyze_excel(
    filters: str = Form(...),
    desired_avg_cost: float = Form(None),
    num_items: int = Form(None),
    minimum_cost: Optional[float] = Form(None),
    maximum_cost: Optional[float] = Form(None)
):
    df = uploaded_files.get("current")
    if df is None:
        return JSONResponse(content={"error": "No file uploaded"}, status_code=400)

    filters_dict = json.loads(filters)

    # Call your generate_random_list (or equivalent algorithm)
    result = generate_random_list(
        df,
        desired_avg_cost,
        num_items,
        include_tags= filters_dict['Tags'],
        include_product= filters_dict['Type'],
        minimum_cost=minimum_cost,
        maximum_cost=maximum_cost
    )
    if result[0] == -1:
        results = {
            'Error': result[1]
        }
    else:
        items, avg_cost, total_items = result
        results = {
            "Selected Items": items[1:],
            "Total Cost": items[0],
            "Average Cost": avg_cost,
            "Total Number of Items": total_items
        }

    return JSONResponse(content={"results": results})







