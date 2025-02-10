from flask import Flask, jsonify, request
from flask_cors import CORS
import undetected_chromedriver as uc
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from openai import OpenAI
from dotenv import load_dotenv
import os
import time
import json

load_dotenv()
app = Flask(__name__)
CORS(app, resources={
    r"/verify": {
        "origins": "*",
        "methods": ["GET"],
        "allow_headers": ["Content-Type"]
    }
})

driver = None
openai_client = OpenAI(api_key=os.environ.get("OPENAI_API_KEY"))
gen_q_prompt = """Ask ChatGPT your {field}. Return just the question as a JSON string, nothing else."""

def extract_answer(gen):
    prompt = f"""Extract the answer as a value, nothing else: {gen}"""
    response = openai_client.chat.completions.create(
        model="gpt-3.5-turbo",
        messages=[{"role": "user", "content": prompt}],
        temperature=0.3
    )
    return response.choices[0].message.content

logged_in = True

def login_uc():
    pass

@app.route('/verify', methods=['GET'])
def verify():
    global driver
    if not driver:
        opts = uc.ChromeOptions()
        opts.add_argument('--remote-debugging-port=9223')
        opts.add_argument('--user-data-dir=./chrome-debug-profile')
        driver = uc.Chrome(options=opts, use_subprocess=True)
        driver.set_window_size(500, 1080)
        driver.set_window_position(1571, 261)
    
    fields_param = request.args.get('fields', None)
    field_pairs = [f.split(':') for f in fields_param.split(',')]
    fields = [{"id": p[0], "label": p[1]} for p in field_pairs]

    if not logged_in:
        login_uc()
    driver.get("https://chatgpt.com/c/67478768-b708-8003-866f-9f093604ba81")
    time.sleep(3)

    input_box = WebDriverWait(driver, 10).until(
        EC.presence_of_element_located((By.CSS_SELECTOR, "#prompt-textarea"))
    )
    results = {}
    for f in fields:
        fid, label = f["id"].strip(), f["label"].strip()
        q = json.loads(openai_client.chat.completions.create(
            model="gpt-3.5-turbo",
            messages=[{"role": "user", "content": gen_q_prompt.format(field=label)}],
            response_format={"type": "json_object"},
            temperature=0.3
        ).choices[0].message.content)["question"]
        input_box.clear()
        input_box.send_keys(q + Keys.RETURN)
        send_button = WebDriverWait(driver, 10).until(
            EC.element_to_be_clickable((By.CSS_SELECTOR, "button[data-testid='send-button']"))
        )
        send_button.click()
        time.sleep(5)
        res = driver.find_elements(By.CSS_SELECTOR, ".markdown")[-1].text.strip()
        ans = extract_answer(res)
        results[fid] = {"label": label, "question": q, "answer": ans}
    
    return jsonify({"results": results, "timestamp": time.time()})

if __name__ == '__main__':
    from OpenSSL import SSL
    context = SSL.Context(SSL.TLSv1_2_METHOD)
    context.use_privatekey_file('server.key')
    context.use_certificate_file('server.crt')
    app.run(port=5000, ssl_context=('server.crt', 'server.key'))
