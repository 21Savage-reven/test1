from flask import Flask, request, jsonify, redirect, render_template_string
from flask_cors import CORS
import time
import os

app = Flask(__name__)
CORS(app, resources={r"/*": {"origins": "*"}})  # Allow all origins (or specify domains)

# เวลาหมดอายุของ token (60 วินาที)
TOKEN_EXPIRY_TIME = int(os.environ.get("TOKEN_EXPIRY_TIME", 60))  # ค่าเริ่มต้นคือ 60 วินาที
current_target = "https://docs.google.com/forms/d/e/1FAIpQLSeGxUnI8PAfHhFT583EaSjkvmIdRw0nxZFJ2yaKCceZbD6FDQ/viewform"
valid_tokens = {}


@app.route('/')
def index():
    return render_template_string(INDEX_HTML, current_target=current_target)

# Endpoint สำหรับ Generate QR Code
@app.route('/generate', methods=['POST'])
def generate_qr():
    global current_target, valid_tokens

    new_target = request.json.get('new_target')
    if not new_target:
        return jsonify({"error": "กรุณาระบุ URL เป้าหมาย"}), 400

    # กำหนด URL ที่ต้องการให้ไป
    target_url = "https://docs.google.com/forms/d/e/1FAIpQLSeGxUnI8PAfHhFT583EaSjkvmIdRw0nxZFJ2yaKCceZbD6FDQ/viewform"
    
    # สร้าง token จากเวลา
    token = str(int(time.time()))
    valid_tokens[token] = target_url
    current_target = target_url

    qr_url = f"/redirect?token={token}"

    return jsonify({
        "qr_url": qr_url,
        "message": "QR Code ใหม่ถูกสร้างเรียบร้อยแล้ว"
    })

@app.route('/redirect', methods=['GET'])
def redirect_to_target():
    token = request.args.get('token')
    if token in valid_tokens:
        if time.time() - float(token) < TOKEN_EXPIRY_TIME:
            return redirect(valid_tokens[token])  # เปลี่ยนเส้นทางไปยัง URL ที่กำหนด
        else:
            del valid_tokens[token]
            return "QR Code หมดอายุ", 403
    return "QR Code ไม่ถูกต้อง", 403

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=int(os.environ.get("PORT", 5000)), debug=True)
