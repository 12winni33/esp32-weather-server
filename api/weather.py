```python
from flask import Flask, jsonify, request
import requests
import os

app = Flask(__name__)

@app.route("/weather")
def weather():
    try:
        # 取得訪問者 IP（優先取 X-Forwarded-For，Vercel 部署時適用）
        ip = request.headers.get("X-Forwarded-For", request.remote_addr)
        ip = ip.split(",")[0].strip()
        print(f"Client IP: {ip}")

        # 查詢 IP 所在縣市
        ip_api = f"https://ipwho.is/{ip}"
        ip_res = requests.get(ip_api, timeout=5)
        region_data = ip_res.json()
        city_name = region_data.get("city", "Taipei")

        # 查詢中央氣象局即時觀測資料
        api_key = os.getenv("CWA_API_KEY")
        cwa_url = f"https://opendata.cwa.gov.tw/api/v1/rest/datastore/O-A0001-001?Authorization={api_key}"
        cwa_res = requests.get(cwa_url, timeout=10)
        cwa_data = cwa_res.json()

        # 找與城市名稱相近的測站
        nearest = None
        for loc in cwa_data["records"]["location"]:
            if city_name in loc["parameter"][0]["parameterValue"]:
                nearest = loc
                break
        if not nearest:
            nearest = cwa_data["records"]["location"][0]

        weather_element = nearest["weatherElement"]
        data = {
            "station": nearest["locationName"],
            "temperature": weather_element[3]["elementValue"],
            "humidity": weather_element[4]["elementValue"],
            "windSpeed": weather_element[2]["elementValue"],
            "weather": weather_element[20]["elementValue"],
        }

        return jsonify(data)

    except Exception as e:
        return jsonify({"error": str(e)}), 500
```

