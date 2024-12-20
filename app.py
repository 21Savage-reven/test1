from flask import Flask, request, jsonify, render_template_string
from flask_cors import CORS
import os

app = Flask(__name__)
CORS(app, resources={r"/*": {"origins": "*"}})  # Allow all origins (or specify domains)

# เวลาหมดอายุของ token (60 วินาที)
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
        const API_URL = "https://test1-j6x3.onrender.com/generate"; // URL ของเซิร์ฟเวอร์ที่ deploy บน Render
        const REFRESH_INTERVAL = 60; // ระยะเวลานับถอยหลัง (วินาที)
        let countdown = REFRESH_INTERVAL;

        // ฟังก์ชันสำหรับดึง URL ของ QR Code จาก API
        async function fetchQRCode() {
            try {
                const response = await fetch(API_URL, {
                    method: "POST",
                    headers: { "Content-Type": "application/json" },
                    body: JSON.stringify({ new_target: "https://docs.google.com/forms/d/e/1FAIpQLSeGxUnI8PAfHhFT583EaSjkvmIdRw0nxZFJ2yaKCceZbD6FDQ/viewform" })
                });

                if (!response.ok) throw new Error("ไม่สามารถสร้าง QR Code ได้");

                const data = await response.json();
                return data.qr_url; // รับ URL ของ QR Code ใหม่
            } catch (error) {
                console.error("Error fetching QR Code:", error);
                alert("เกิดข้อผิดพลาดในการสร้าง QR Code");
                return null;
            }
        }

        // ฟังก์ชันสำหรับรีเฟรช QR Code
        async function refreshQRCode() {
            const qrUrl = await fetchQRCode();
            if (qrUrl) {
                QRCode.toDataURL(qrUrl, (error, dataUrl) => {
                    if (error) {
                        console.error("เกิดข้อผิดพลาดในการสร้าง QR Code:", error);
                        document.getElementById("qrcode-img").alt = "ไม่สามารถโหลด QR Code ได้";
                    } else {
                        document.getElementById("qrcode-img").src = dataUrl;
                        console.log("QR Code สร้างเรียบร้อย");
                    }
                });
            }
        }

        // ฟังก์ชันสำหรับอัพเดตเวลา
        function updateDatetime() {
            const datetimeElement = document.getElementById("datetime");
            const options = { timeZone: "Asia/Bangkok", hour12: true, hour: "2-digit", minute: "2-digit", second: "2-digit", day: "2-digit", month: "2-digit", year: "numeric" };
            const currentTime = new Date().toLocaleString("th-TH", options);
            datetimeElement.textContent = `เวลาปัจจุบัน: ${currentTime}`;
        }

        // ฟังก์ชันสำหรับการนับถอยหลัง
        function startCountdown() {
            const countdownElement = document.getElementById("countdown");
            const interval = setInterval(() => {
                countdown--;
                countdownElement.textContent = `QR Code จะรีเซ็ตในอีก ${countdown} วินาที`;

                if (countdown <= 0) {
                    countdown = REFRESH_INTERVAL; // รีเซ็ตเวลานับถอยหลัง
                    refreshQRCode(); // รีเฟรช QR Code ใหม่
                }
            }, 1000);  // รีเฟรชทุกๆ 1 วินาที
        }

        // เรียกฟังก์ชันต่างๆ
        refreshQRCode(); // สร้าง QR Code ทันทีเมื่อเปิดหน้าเว็บ
        startCountdown(); // เริ่มต้นการนับถอยหลัง
        setInterval(updateDatetime, 1000); // อัพเดตเวลาไทยทุกวินาที
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
    global current_target

    new_target = request.json.get('new_target')
    if not new_target:
        return jsonify({"error": "กรุณาระบุ URL เป้าหมาย"}), 400

    # กำหนด URL ที่ต้องการให้ไป
    target_url = new_target  # ใช้ URL ที่มาจาก request

    # สร้าง QR Code ที่ไปยัง URL ของ Google Form โดยตรง
    qr_url = target_url  # ไม่ต้องใช้ token ในที่นี้

    return jsonify({
        "qr_url": qr_url,
        "message": "QR Code ใหม่ถูกสร้างเรียบร้อยแล้ว"
    })

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=int(os.environ.get("PORT", 5000)), debug=True)
