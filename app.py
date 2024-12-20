from flask import Flask, request, jsonify, redirect
from flask_cors import CORS  # เปิดใช้ CORS
import time

app = Flask(__name__)
CORS(app)  # เปิดใช้งาน CORS สำหรับแอปทั้งหมด

current_target = "https://docs.google.com/forms/d/e/1FAIpQLSeGxUnI8PAfHhFT583EaSjkvmIdRw0nxZFJ2yaKCceZbD6FDQ/viewform"  # URL เริ่มต้น
valid_tokens = {}

TOKEN_EXPIRY_TIME = 60  # กำหนดเวลาให้ QR Code หมดอายุภายใน 1 นาที


# Route สำหรับหน้าเริ่มต้น (สำหรับการทดสอบ)
@app.route('/')
def index():
    return "Hello, Welcome to QR Code App!"


@app.route('/generate', methods=['POST'])
def generate_qr():
    global current_target, valid_tokens

    new_target = request.json.get('new_target')
    if not new_target:
        return jsonify({"error": "กรุณาระบุ URL เป้าหมาย"}), 400

    # สร้าง token ใหม่ทุกครั้งที่มีการอัปเดต URL
    token = str(int(time.time()))
    valid_tokens[token] = new_target  # เก็บ URL ใหม่ที่เกี่ยวข้องกับ token
    current_target = new_target

    # ส่ง URL ใหม่ที่รวมกับ token
    return jsonify({
        "qr_url": f"http://127.0.0.1:5000/redirect?token={token}",
        "message": "QR Code ใหม่ถูกสร้างเรียบร้อยแล้ว"
    })


@app.route('/redirect', methods=['GET'])
def redirect_to_target():
    token = request.args.get('token')
    if token in valid_tokens:
        # ตรวจสอบว่า token หมดอายุหรือไม่
        if time.time() - float(token) < TOKEN_EXPIRY_TIME:
            return redirect(valid_tokens[token])  # หาก token ยังไม่หมดอายุ ก็จะ redirect ไปที่ URL ที่เกี่ยวข้อง
        else:
            del valid_tokens[token]  # ลบ token ที่หมดอายุออกจาก valid_tokens
            return render_expired_page()  # เรียกใช้ฟังก์ชันแสดงหน้าเมื่อหมดอายุ
    return render_expired_page()  # หากไม่พบ token ในระบบ


def render_expired_page():
    """ฟังก์ชันสำหรับสร้างหน้า HTML เมื่อ QR Code หมดอายุ"""
    return """
    <!DOCTYPE html>
    <html lang="th">
    <head>
        <meta charset="UTF-8">
        <meta name="viewport" content="width=device-width, initial-scale=1.0">
        <title>QR Code หมดอายุ</title>
        <style>
            body {
                font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif;
                background-color: #f9f9f9;
                color: #333;
                margin: 0;
                padding: 0;
                display: flex;
                flex-direction: column;
                align-items: center;
                justify-content: center;
                height: 100vh;
                text-align: center;
            }
            h1 {
                color: #E74C3C;
                margin-bottom: 20px;
            }
            p {
                font-size: 18px;
                color: #555;
            }
            a {
                margin-top: 20px;
                display: inline-block;
                padding: 10px 20px;
                font-size: 16px;
                color: #fff;
                background-color: #3498DB;
                border-radius: 5px;
                text-decoration: none;
                transition: background-color 0.3s ease;
            }
            a:hover {
                background-color: #2980B9;
            }
        </style>
    </head>
    <body>
       <h1>QR Code นี้หมดอายุ</h1>
        <p>โปรดสเเกนใหม่อีกครั้ง</p>

    </body>
    </html>
    """, 403


if __name__ == "__main__":
    app.run(debug=True)
