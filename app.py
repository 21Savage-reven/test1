from flask import Flask, request, jsonify, redirect, render_template_string
from flask_cors import CORS
import time
import os

app = Flask(__name__)
CORS(app)

TOKEN_EXPIRY_TIME = int(os.environ.get("TOKEN_EXPIRY_TIME", 60))  # ค่าเริ่มต้นคือ 60 วินาที
current_target = "https://docs.google.com/forms/d/e/1FAIpQLSeGxUnI8PAfHhFT583EaSjkvmIdRw0nxZFJ2yaKCceZbD6FDQ/viewform"
valid_tokens = {}

# HTML Template
INDEX_HTML = """
<!DOCTYPE html>
<html lang="th">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>QR Code Google Form</title>
    <script src="https://cdn.jsdelivr.net/npm/qrcode/build/qrcode.min.js"></script>
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
            min-height: 100vh;
        }
    
        h1 {
            color: #4CAF50;
            margin-bottom: 10px;
        }
    
        #qrcode-container {
            background: #fff;
            border-radius: 10px;
            box-shadow: 0 4px 6px rgba(0, 0, 0, 0.1);
            padding: 20px;
            margin-top: 10px; /* ลดระยะห่างให้น้อยลง */
            display: inline-block;
        }
    
        #qrcode-img {
            margin-top: 20px;
            padding: 10px;
            width: 400px;
            height: 400px;
        }
    
        p#datetime {
            font-size: 60px; /* ปรับขนาดฟอนต์ */
            color: #363636;
            margin: 5px 0; /* ลดระยะห่างระหว่างข้อความและ QR Code */
        }
    
        p {
            margin-top: 15px;
            font-size: 25px;
            color: #555;
        }
    
        footer {
            margin-top: 20px;
            font-size: 18px;
            color: #aaa;
        }
    
        #countdown {
            font-size: 18px;
            color: #777;
        }
    </style>
</head>
<body>
    <h1>QR Code สำหรับเช็คชื่อ</h1>
    <p id="datetime">เวลาปัจจุบัน: กำลังโหลด...</p>
    <div id="qrcode-container">
        <img id="qrcode-img" alt="กำลังโหลด QR Code...">
    </div>
    <p id="countdown">QR Code จะรีเซ็ตในอีก 60 วินาที</p>
    <footer>Made with ❤️ by <strong>AKA_23Savge&Dreak</strong></footer>

    <script>
        const API_URL = "/generate"; // ใช้ endpoint ในแอป Flask
        const REFRESH_INTERVAL = 60; // ระยะเวลานับถอยหลัง (วินาที)
        let countdown = REFRESH_INTERVAL;

        async function fetchQRCode() {
            try {
                const response = await fetch(API_URL, {
                    method: "POST",
                    headers: { "Content-Type": "application/json" },
                    body: JSON.stringify({ new_target: "{{ current_target }}" })
                });

                if (!response.ok) throw new Error("ไม่สามารถสร้าง QR Code ได้");

                const data = await response.json();
                return data.qr_url;
            } catch (error) {
                console.error("Error fetching QR Code:", error);
                alert("เกิดข้อผิดพลาดในการสร้าง QR Code");
                return null;
            }
        }

        function updateDatetime() {
            const datetimeElement = document.getElementById("datetime");
            const options = { timeZone: "Asia/Bangkok", hour12: true, hour: "2-digit", minute: "2-digit", second: "2-digit", day: "2-digit", month: "2-digit", year: "numeric" };
            const currentTime = new Date().toLocaleString("th-TH", options);
            datetimeElement.textContent = `เวลาปัจจุบัน: ${currentTime}`;
        }

        function startCountdown() {
            const countdownElement = document.getElementById("countdown");
            const interval = setInterval(() => {
                countdown--;
                countdownElement.textContent = `QR Code จะรีเซ็ตในอีก ${countdown} วินาที`;

                if (countdown <= 0) {
                    clearInterval(interval);
                    countdown = REFRESH_INTERVAL;
                    fetchQRCode();
                    startCountdown();
                }
            }, 1000);
        }

        fetchQRCode();
        startCountdown();
        setInterval(updateDatetime, 1000);
    </script>
</body>
</html>
"""

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

    token = str(int(time.time()))
    valid_tokens[token] = new_target
    current_target = new_target

    return jsonify({
        "qr_url": f"/redirect?token={token}",
        "message": "QR Code ใหม่ถูกสร้างเรียบร้อยแล้ว"
    })

@app.route('/redirect', methods=['GET'])
def redirect_to_target():
    token = request.args.get('token')
    if token in valid_tokens:
        if time.time() - float(token) < TOKEN_EXPIRY_TIME:
            return redirect(valid_tokens[token])
        else:
            del valid_tokens[token]
            return "QR Code หมดอายุ", 403
    return "QR Code ไม่ถูกต้อง", 403


if __name__ == "__main__":
    app.run(host="0.0.0.0", port=int(os.environ.get("PORT", 5000)), debug=True)
