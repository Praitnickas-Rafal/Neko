from fastapi import FastAPI, File, UploadFile, Form, HTTPException, Request
from fastapi.responses import JSONResponse, FileResponse
import cv2
import numpy as np
import os
import random
from lib.captcha_solver.inferenceModel import ImageToWordModel
from mltu.configs import BaseModelConfigs
from starlette.middleware.sessions import SessionMiddleware

app = FastAPI()

app.add_middleware(SessionMiddleware, secret_key="secret") # add env var

# Absolute path to the configs.yaml file
config_path = os.path.join(
    os.path.dirname(__file__),
    "lib", "captcha_solver", "Models", "02_captcha_to_text", "202504131954", "configs.yaml"
)

# Load configs from file
configs = BaseModelConfigs.load(config_path)

# Make the model_path absolute by resolving it relative to the config file's folder
model_path = os.path.dirname(config_path)

model = ImageToWordModel(model_path=model_path, char_list=configs.vocab)

@app.get("/")
def read_root(request: Request):
    page = "logged-in.html" if request.session.get("authenticated") else "index.html"
    path = os.path.join(os.path.dirname(__file__), "static", "pages", page)
    return FileResponse(path)

@app.get("/captcha")
def random_captcha(request: Request):
    captcha_dir = os.path.join(os.path.dirname(__file__), "static", "captchas")
    files = [f for f in os.listdir(captcha_dir) if f.lower().endswith(('.png', '.jpg', '.jpeg'))]

    if not files:
        raise HTTPException(status_code=500, detail="No CAPTCHA images available.")

    random_file = random.choice(files)

    # Extract the filename (without extension) as the captcha code
    code, _ = os.path.splitext(random_file)
    request.session['captcha_code'] = code.upper()

    return FileResponse(os.path.join(captcha_dir, random_file))
    
@app.post("/login")
def login(
    request: Request,
    username: str = Form(...),
    password: str = Form(...),
    captcha: str = Form(...)
):
    expected_code = request.session.get("captcha_code")
    
    print(f"Expected captcha code: {expected_code}")

    if not expected_code or captcha.strip().upper() != expected_code:
        return JSONResponse(status_code=400, content={"error": "Invalid captcha"})

    # Optional: Invalidate used captcha
    request.session["captcha_code"] = None

    if username == "admin" and password == "pass":
        request.session["user"] = username
        request.session["authenticated"] = True
        return {"message": "Login successful"}

    return JSONResponse(status_code=401, content={"error": "Invalid credentials"})

@app.get("/logout")
def logout(request: Request):
    request.session.clear()
    return JSONResponse(content={"message": "Logged out successfully"})